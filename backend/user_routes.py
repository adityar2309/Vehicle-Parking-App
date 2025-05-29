from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import User, ParkingLot, ParkingSpot, Reservation, UserActivity
from datetime import datetime
import functools
import json
from cache_service import CacheService, cached_response, monitor_performance, cache
import logging

# Configure logging
logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/user')

def user_required(f):
    """Decorator to require user role"""
    @functools.wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            # Convert string user_id back to string for MongoDB lookup
            user_id = str(user_id)
            user = User.objects(id=user_id).first()
            
            if not user or user.role != 'user':
                return jsonify({'error': 'User access required'}), 403
            
            # Update last login timestamp
            user.update_last_login()
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authorization failed'}), 401
    return decorated_function

@user_bp.route('/parking-lots', methods=['GET'])
@user_required
@cached_response(timeout=300, key_func=lambda: "user:parking_lots:available")
@monitor_performance("get_available_parking_lots")
def get_available_parking_lots():
    """
    Get all parking lots with availability information
    
    This endpoint is cached for 5 minutes to improve performance.
    Cache is invalidated when parking lot data changes.
    """
    try:
        # Try to get from cache first
        cached_data = CacheService.get_cached_parking_lots()
        if cached_data:
            # Filter only lots with available spots for users
            available_lots = [lot for lot in cached_data if lot.get('available_spots', 0) > 0]
            logger.debug("Serving parking lots from cache")
            return jsonify({'parking_lots': available_lots}), 200
        
        # If not in cache, fetch from database - MongoDB query
        lots = ParkingLot.objects()
        available_lots = []
        
        for lot in lots:
            available_spots = ParkingSpot.objects(lot_id=str(lot.id), status='A').count()
            if available_spots > 0:  # Only show lots with available spots
                lot_data = lot.to_dict()
                available_lots.append(lot_data)
        
        # Cache the result
        CacheService.cache_parking_lots(available_lots, timeout=300)
        
        return jsonify({
            'parking_lots': available_lots
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching parking lots: {str(e)}")
        return jsonify({'error': 'Failed to fetch parking lots: ' + str(e)}), 500

@user_bp.route('/book-spot', methods=['POST'])
@user_required
@monitor_performance("book_parking_spot")
def book_parking_spot():
    """Book the first available parking spot in a selected lot"""
    try:
        user_id = get_jwt_identity()
        # Convert string user_id to string for MongoDB lookup
        user_id = str(user_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        lot_id = data.get('lot_id')
        vehicle_number = data.get('vehicle_number', '').strip()
        
        if not lot_id:
            return jsonify({'error': 'Parking lot ID is required'}), 400
        
        if not vehicle_number:
            return jsonify({'error': 'Vehicle number is required'}), 400
        
        # Check if user already has an active reservation - MongoDB query
        active_reservation = Reservation.objects(
            user_id=user_id,
            leaving_timestamp=None
        ).first()
        
        if active_reservation:
            return jsonify({'error': 'You already have an active parking reservation'}), 400
        
        # Find the first available spot in the selected lot - MongoDB query
        available_spot = ParkingSpot.objects(
            lot_id=lot_id,
            status='A'
        ).first()
        
        if not available_spot:
            return jsonify({'error': 'No available spots in this parking lot'}), 400
        
        # Create reservation
        reservation = Reservation(
            spot_id=str(available_spot.id),
            user_id=user_id,
            vehicle_number=vehicle_number,
            parking_timestamp=datetime.utcnow()
        )
        
        # Update spot status to occupied
        available_spot.status = 'O'
        
        reservation.save()
        available_spot.save()
        
        # Update user's last booking timestamp
        user = User.objects(id=user_id).first()
        user.update_last_booking()
        
        # Log activity
        activity = UserActivity(
            user_id=user_id,
            activity_type='booking_created',
            activity_data=json.dumps({
                'lot_id': lot_id,
                'spot_id': str(available_spot.id),
                'spot_number': available_spot.spot_number,
                'vehicle_number': vehicle_number
            })
        )
        activity.save()
        
        # Invalidate relevant caches
        CacheService.invalidate_parking_lot_cache(lot_id)
        CacheService.invalidate_user_cache(user_id)
        
        logger.info(f"User {user_id} booked spot {available_spot.spot_number} in lot {lot_id}")
        
        return jsonify({
            'message': 'Parking spot booked successfully',
            'reservation': reservation.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error booking parking spot: {str(e)}")
        return jsonify({'error': 'Failed to book parking spot: ' + str(e)}), 500

@user_bp.route('/release-spot', methods=['POST'])
@user_required
@monitor_performance("release_parking_spot")
def release_parking_spot():
    """Release the user's current parking spot"""
    try:
        user_id = get_jwt_identity()
        # Convert string user_id to string for MongoDB lookup
        user_id = str(user_id)
        
        # Find user's active reservation - MongoDB query
        active_reservation = Reservation.objects(
            user_id=user_id,
            leaving_timestamp=None
        ).first()
        
        if not active_reservation:
            return jsonify({'error': 'No active parking reservation found'}), 400
        
        # Update reservation with leaving timestamp and calculate cost
        active_reservation.leaving_timestamp = datetime.utcnow()
        active_reservation.parking_cost = active_reservation.calculate_cost()
        
        # Update spot status to available
        parking_spot = ParkingSpot.objects(id=active_reservation.spot_id).first()
        parking_spot.status = 'A'
        lot_id = parking_spot.lot_id
        
        # Save changes
        active_reservation.save()
        parking_spot.save()
        
        # Log activity
        activity = UserActivity(
            user_id=user_id,
            activity_type='booking_completed',
            activity_data=json.dumps({
                'reservation_id': str(active_reservation.id),
                'lot_id': lot_id,
                'spot_id': str(parking_spot.id),
                'spot_number': parking_spot.spot_number,
                'duration_hours': round((active_reservation.leaving_timestamp - active_reservation.parking_timestamp).total_seconds() / 3600, 2),
                'cost': active_reservation.parking_cost
            })
        )
        activity.save()
        
        # Invalidate relevant caches
        CacheService.invalidate_parking_lot_cache(lot_id)
        CacheService.invalidate_user_cache(user_id)
        
        logger.info(f"User {user_id} released spot {parking_spot.spot_number}, cost: ${active_reservation.parking_cost}")
        
        return jsonify({
            'message': 'Parking spot released successfully',
            'reservation': active_reservation.to_dict(),
            'cost': active_reservation.parking_cost
        }), 200
        
    except Exception as e:
        logger.error(f"Error releasing parking spot: {str(e)}")
        return jsonify({'error': 'Failed to release parking spot: ' + str(e)}), 500

@user_bp.route('/reservations', methods=['GET'])
@user_required
@monitor_performance("get_user_reservations")
def get_user_reservations():
    """Get all reservations for the current user"""
    try:
        user_id = get_jwt_identity()
        # Convert string user_id to string for MongoDB lookup
        user_id = str(user_id)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Try cache for first page
        if page == 1:
            cache_key = CacheService.get_user_reservations_cache_key(user_id)
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug(f"Serving user {user_id} reservations from cache")
                return jsonify(cached_data), 200
        
        # MongoDB pagination
        skip = (page - 1) * per_page
        reservations = Reservation.objects(user_id=user_id).order_by('-created_at').skip(skip).limit(per_page)
        total_count = Reservation.objects(user_id=user_id).count()
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        result = {
            'reservations': [reservation.to_dict() for reservation in reservations],
            'pagination': {
                'page': page,
                'pages': total_pages,
                'per_page': per_page,
                'total': total_count,
                'has_next': has_next,
                'has_prev': has_prev
            }
        }
        
        # Cache first page for 2 minutes
        if page == 1:
            cache_key = CacheService.get_user_reservations_cache_key(user_id)
            cache.set(cache_key, result, timeout=120)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching user reservations: {str(e)}")
        return jsonify({'error': 'Failed to fetch reservations: ' + str(e)}), 500

@user_bp.route('/current-reservation', methods=['GET'])
@user_required
@monitor_performance("get_current_reservation")
def get_current_reservation():
    """Get user's current active reservation"""
    try:
        user_id = get_jwt_identity()
        # Convert string user_id to string for MongoDB lookup
        user_id = str(user_id)
        
        active_reservation = Reservation.objects(
            user_id=user_id,
            leaving_timestamp=None
        ).first()
        
        if not active_reservation:
            return jsonify({'current_reservation': None}), 200
        
        return jsonify({
            'current_reservation': active_reservation.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching current reservation: {str(e)}")
        return jsonify({'error': 'Failed to fetch current reservation: ' + str(e)}), 500

@user_bp.route('/dashboard', methods=['GET'])
@user_required
@monitor_performance("get_user_dashboard")
def get_user_dashboard():
    """Get user dashboard with statistics and current status"""
    try:
        user_id = get_jwt_identity()
        # Convert string user_id to string for MongoDB lookup
        user_id = str(user_id)
        
        # Try cache first
        cache_key = CacheService.get_dashboard_stats_cache_key(user_id)
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Serving user {user_id} dashboard from cache")
            return jsonify(cached_data), 200
        
        # Get user statistics - MongoDB queries
        total_reservations = Reservation.objects(user_id=user_id).count()
        completed_reservations = Reservation.objects(
            user_id=user_id,
            leaving_timestamp__ne=None
        ).count()
        
        # Calculate total spent
        completed_reservations_list = Reservation.objects(
            user_id=user_id,
            leaving_timestamp__ne=None
        )
        total_spent = sum([r.parking_cost or 0 for r in completed_reservations_list])
        
        # Get current active reservation
        active_reservation = Reservation.objects(
            user_id=user_id,
            leaving_timestamp=None
        ).first()
        
        # Get recent reservations
        recent_reservations = Reservation.objects(user_id=user_id).order_by('-created_at').limit(5)
        
        # Get most used parking lot
        most_used_lot = None
        if total_reservations > 0:
            # Count usage by lot
            lot_usage = {}
            all_reservations = Reservation.objects(user_id=user_id)
            for reservation in all_reservations:
                parking_spot = ParkingSpot.objects(id=reservation.spot_id).first()
                if parking_spot:
                    parking_lot = ParkingLot.objects(id=parking_spot.lot_id).first()
                    if parking_lot:
                        lot_name = parking_lot.prime_location_name
                        lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1
            
            if lot_usage:
                most_used_lot = max(lot_usage, key=lot_usage.get)
        
        dashboard_data = {
            'user_stats': {
                'total_reservations': total_reservations,
                'completed_reservations': completed_reservations,
                'active_reservations': 1 if active_reservation else 0,
                'total_spent': float(total_spent),
                'most_used_lot': most_used_lot
            },
            'current_reservation': active_reservation.to_dict() if active_reservation else None,
            'recent_reservations': [res.to_dict() for res in recent_reservations],
            'available_lots_count': ParkingLot.objects.count()
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, dashboard_data, timeout=300)
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        logger.error(f"Error fetching user dashboard: {str(e)}")
        return jsonify({'error': 'Failed to fetch dashboard data: ' + str(e)}), 500

@user_bp.route('/activity', methods=['GET'])
@user_required
def get_user_activity():
    """Get user's activity history"""
    try:
        user_id = get_jwt_identity()
        user_id = str(user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        activity_type = request.args.get('type')
        
        # Build MongoDB query
        query_filter = {'user_id': user_id}
        if activity_type:
            query_filter['activity_type'] = activity_type
        
        # MongoDB pagination
        skip = (page - 1) * per_page
        activities = UserActivity.objects(**query_filter).order_by('-timestamp').skip(skip).limit(per_page)
        total_count = UserActivity.objects(**query_filter).count()
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return jsonify({
            'activities': [activity.to_dict() for activity in activities],
            'pagination': {
                'page': page,
                'pages': total_pages,
                'per_page': per_page,
                'total': total_count,
                'has_next': has_next,
                'has_prev': has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user activity: {str(e)}")
        return jsonify({'error': 'Failed to fetch activity: ' + str(e)}), 500 