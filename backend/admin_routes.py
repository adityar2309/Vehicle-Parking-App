from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
# from models import db, User, ParkingLot, ParkingSpot, Reservation  # Updated for MongoDB
from models import User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime
# from sqlalchemy import func  # Commented out - SQLAlchemy dependency
import functools

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin role"""
    @functools.wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            # Convert string user_id to string for MongoDB lookup
            user_id = str(user_id)
            user = User.objects(id=user_id).first()
            
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authorization failed'}), 401
    return decorated_function

@admin_bp.route('/parking-lots', methods=['GET'])
@admin_required
def get_parking_lots():
    """Get all parking lots"""
    try:
        lots = ParkingLot.objects()
        return jsonify({
            'parking_lots': [lot.to_dict() for lot in lots]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch parking lots: ' + str(e)}), 500

@admin_bp.route('/parking-lots', methods=['POST'])
@admin_required
def create_parking_lot():
    """Create a new parking lot"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validation
        required_fields = ['prime_location_name', 'address', 'pin_code', 'number_of_spots', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate numeric fields
        try:
            number_of_spots = int(data['number_of_spots'])
            price = float(data['price'])
        except ValueError:
            return jsonify({'error': 'Invalid number format for spots or price'}), 400
        
        if number_of_spots <= 0:
            return jsonify({'error': 'Number of spots must be positive'}), 400
        
        if price <= 0:
            return jsonify({'error': 'Price must be positive'}), 400
        
        # Create parking lot
        lot = ParkingLot(
            prime_location_name=data['prime_location_name'].strip(),
            address=data['address'].strip(),
            pin_code=data['pin_code'].strip(),
            number_of_spots=number_of_spots,
            price=price
        )
        
        lot.save()
        
        # Create parking spots automatically
        for i in range(1, number_of_spots + 1):
            spot = ParkingSpot(
                lot_id=str(lot.id),
                spot_number=f"P{i:03d}",  # P001, P002, etc.
                status='A'
            )
            spot.save()
        
        return jsonify({
            'message': 'Parking lot created successfully',
            'parking_lot': lot.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create parking lot: ' + str(e)}), 500

@admin_bp.route('/parking-lots/<lot_id>', methods=['PUT'])
@admin_required
def update_parking_lot(lot_id):
    """Update a parking lot"""
    try:
        lot = ParkingLot.objects(id=lot_id).first()
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
            
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'prime_location_name' in data:
            lot.prime_location_name = data['prime_location_name'].strip()
        
        if 'address' in data:
            lot.address = data['address'].strip()
        
        if 'pin_code' in data:
            lot.pin_code = data['pin_code'].strip()
        
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    return jsonify({'error': 'Price must be positive'}), 400
                lot.price = price
            except ValueError:
                return jsonify({'error': 'Invalid price format'}), 400
        
        # Handle number of spots change
        if 'number_of_spots' in data:
            try:
                new_spots = int(data['number_of_spots'])
                if new_spots <= 0:
                    return jsonify({'error': 'Number of spots must be positive'}), 400
                
                current_spots = ParkingSpot.objects(lot_id=str(lot.id)).count()
                
                if new_spots < current_spots:
                    # Check if we can reduce spots (no occupied spots in the range to be removed)
                    all_spots = list(ParkingSpot.objects(lot_id=str(lot.id)).order_by('spot_number'))
                    spots_to_remove = all_spots[new_spots:]
                    occupied_spots = [spot for spot in spots_to_remove if spot.status == 'O']
                    
                    if occupied_spots:
                        return jsonify({'error': 'Cannot reduce spots as some spots are currently occupied'}), 400
                    
                    # Remove excess spots
                    for spot in spots_to_remove:
                        spot.delete()
                
                elif new_spots > current_spots:
                    # Add new spots
                    for i in range(current_spots + 1, new_spots + 1):
                        spot = ParkingSpot(
                            lot_id=str(lot.id),
                            spot_number=f"P{i:03d}",
                            status='A'
                        )
                        spot.save()
                
                lot.number_of_spots = new_spots
                
            except ValueError:
                return jsonify({'error': 'Invalid number of spots format'}), 400
        
        lot.save()
        
        return jsonify({
            'message': 'Parking lot updated successfully',
            'parking_lot': lot.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update parking lot: ' + str(e)}), 500

@admin_bp.route('/parking-lots/<lot_id>', methods=['DELETE'])
@admin_required
def delete_parking_lot(lot_id):
    """Delete a parking lot (only if all spots are empty)"""
    try:
        lot = ParkingLot.objects(id=lot_id).first()
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        # Check if any spots are occupied
        occupied_spots = ParkingSpot.objects(lot_id=lot_id, status='O').count()
        if occupied_spots > 0:
            return jsonify({'error': 'Cannot delete parking lot with occupied spots'}), 400
        
        # Delete all spots first
        ParkingSpot.objects(lot_id=lot_id).delete()
        
        # Delete the lot
        lot.delete()
        
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to delete parking lot: ' + str(e)}), 500

@admin_bp.route('/parking-lots/<lot_id>/spots', methods=['GET'])
@admin_required
def get_parking_spots(lot_id):
    """Get all parking spots for a specific lot"""
    try:
        # Check if lot exists
        lot = ParkingLot.objects(id=lot_id).first()
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        spots = ParkingSpot.objects(lot_id=lot_id).order_by('spot_number')
        return jsonify({
            'parking_spots': [spot.to_dict() for spot in spots],
            'lot_info': lot.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch parking spots: ' + str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users"""
    try:
        users = User.objects()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch users: ' + str(e)}), 500

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_data():
    """Get admin dashboard statistics"""
    try:
        # Get basic counts
        total_users = User.objects(role='user').count()
        total_admins = User.objects(role='admin').count()
        total_lots = ParkingLot.objects.count()
        total_spots = ParkingSpot.objects.count()
        occupied_spots = ParkingSpot.objects(status='O').count()
        available_spots = ParkingSpot.objects(status='A').count()
        
        # Get reservation statistics
        total_reservations = Reservation.objects.count()
        active_reservations = Reservation.objects(leaving_timestamp=None).count()
        completed_reservations = Reservation.objects(leaving_timestamp__ne=None).count()
        
        # Calculate total revenue
        completed_reservations_list = Reservation.objects(leaving_timestamp__ne=None)
        total_revenue = sum([r.parking_cost or 0 for r in completed_reservations_list])
        
        # Get recent reservations
        recent_reservations = Reservation.objects().order_by('-created_at').limit(5)
        
        return jsonify({
            'stats': {
                'users': {
                    'total_users': total_users,
                    'total_admins': total_admins,
                    'total': total_users + total_admins
                },
                'parking': {
                    'total_lots': total_lots,
                    'total_spots': total_spots,
                    'occupied_spots': occupied_spots,
                    'available_spots': available_spots,
                    'occupancy_rate': round((occupied_spots / total_spots * 100) if total_spots > 0 else 0, 1)
                },
                'reservations': {
                    'total_reservations': total_reservations,
                    'active_reservations': active_reservations,
                    'completed_reservations': completed_reservations,
                    'total_revenue': round(total_revenue, 2)
                }
            },
            'recent_reservations': [res.to_dict() for res in recent_reservations]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch dashboard data: ' + str(e)}), 500 