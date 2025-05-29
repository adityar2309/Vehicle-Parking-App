# MongoDB Models using MongoEngine
from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, ReferenceField, ListField, BooleanField
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

# Legacy SQLAlchemy imports (commented out)
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime
# import uuid

# db = SQLAlchemy()  # Commented out for MongoDB

class User(Document):
    """User model for both admin and regular users"""
    meta = {'collection': 'users'}
    
    username = StringField(max_length=80, unique=True, required=True)
    email = StringField(max_length=120, unique=True)
    password_hash = StringField(max_length=120, required=True)
    role = StringField(max_length=20, required=True, default='user')  # 'admin' or 'user'
    last_login = DateTimeField()
    last_booking = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.save()
    
    def update_last_booking(self):
        """Update last booking timestamp"""
        self.last_booking = datetime.utcnow()
        self.save()
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_booking': self.last_booking.isoformat() if self.last_booking else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ParkingLot(Document):
    """Parking lot model"""
    meta = {'collection': 'parking_lots'}
    
    prime_location_name = StringField(max_length=100, required=True)
    address = StringField(required=True)
    pin_code = StringField(max_length=10, required=True)
    number_of_spots = IntField(required=True)
    price = FloatField(required=True)  # Price per hour
    created_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        """Convert parking lot object to dictionary"""
        # Count available and occupied spots
        available_spots = ParkingSpot.objects(lot_id=str(self.id), status='A').count()
        occupied_spots = ParkingSpot.objects(lot_id=str(self.id), status='O').count()
        
        return {
            'id': str(self.id),
            'prime_location_name': self.prime_location_name,
            'address': self.address,
            'pin_code': self.pin_code,
            'number_of_spots': self.number_of_spots,
            'price': self.price,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'available_spots': available_spots,
            'occupied_spots': occupied_spots
        }

class ParkingSpot(Document):
    """Parking spot model"""
    meta = {'collection': 'parking_spots'}
    
    lot_id = StringField(required=True)  # Reference to ParkingLot ID
    spot_number = StringField(max_length=10, required=True)
    status = StringField(max_length=1, required=True, default='A')  # 'A' for Available, 'O' for Occupied
    created_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        """Convert parking spot object to dictionary"""
        current_reservation = None
        if self.status == 'O':
            # Get the current active reservation
            active_reservation = Reservation.objects(
                spot_id=str(self.id),
                leaving_timestamp=None
            ).first()
            if active_reservation:
                user = User.objects(id=active_reservation.user_id).first()
                current_reservation = {
                    'user_id': active_reservation.user_id,
                    'username': user.username if user else 'Unknown',
                    'parking_timestamp': active_reservation.parking_timestamp.isoformat(),
                    'vehicle_number': active_reservation.vehicle_number
                }
        
        return {
            'id': str(self.id),
            'lot_id': self.lot_id,
            'spot_number': self.spot_number,
            'status': self.status,
            'status_display': 'Available' if self.status == 'A' else 'Occupied',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'current_reservation': current_reservation
        }

class Reservation(Document):
    """Reservation model for parking bookings"""
    meta = {'collection': 'reservations'}
    
    spot_id = StringField(required=True)  # Reference to ParkingSpot ID
    user_id = StringField(required=True)  # Reference to User ID
    vehicle_number = StringField(max_length=20, required=True)
    parking_timestamp = DateTimeField(required=True, default=datetime.utcnow)
    leaving_timestamp = DateTimeField()
    parking_cost = FloatField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    def calculate_cost(self):
        """Calculate parking cost based on time spent"""
        if not self.leaving_timestamp:
            return 0.0
        
        # Calculate hours parked (minimum 1 hour)
        time_diff = self.leaving_timestamp - self.parking_timestamp
        hours = max(1, time_diff.total_seconds() / 3600)
        
        # Get parking lot price
        parking_spot = ParkingSpot.objects(id=self.spot_id).first()
        if parking_spot:
            parking_lot = ParkingLot.objects(id=parking_spot.lot_id).first()
            if parking_lot:
                cost = hours * parking_lot.price
                return round(cost, 2)
        
        return 0.0
    
    def to_dict(self):
        """Convert reservation object to dictionary"""
        # Get related objects
        parking_spot = ParkingSpot.objects(id=self.spot_id).first()
        parking_lot = None
        if parking_spot:
            parking_lot = ParkingLot.objects(id=parking_spot.lot_id).first()
        
        return {
            'id': str(self.id),
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'vehicle_number': self.vehicle_number,
            'parking_timestamp': self.parking_timestamp.isoformat() if self.parking_timestamp else None,
            'leaving_timestamp': self.leaving_timestamp.isoformat() if self.leaving_timestamp else None,
            'parking_cost': self.parking_cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'spot_number': parking_spot.spot_number if parking_spot else 'Unknown',
            'lot_name': parking_lot.prime_location_name if parking_lot else 'Unknown',
            'lot_address': parking_lot.address if parking_lot else 'Unknown',
            'status': 'Active' if not self.leaving_timestamp else 'Completed'
        }

class ExportJob(Document):
    """Model to track CSV export jobs"""
    meta = {'collection': 'export_jobs'}
    
    user_id = StringField(required=True)  # Reference to User ID
    job_id = StringField(unique=True, required=True, default=lambda: str(uuid.uuid4()))
    status = StringField(max_length=20, required=True, default='pending')  # pending, processing, completed, failed
    file_path = StringField()
    download_url = StringField()
    error_message = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()
    expires_at = DateTimeField()
    
    def to_dict(self):
        """Convert export job object to dictionary"""
        return {
            'id': str(self.id),
            'job_id': self.job_id,
            'status': self.status,
            'download_url': self.download_url,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class UserActivity(Document):
    """Model to track user activity for analytics"""
    meta = {'collection': 'user_activities'}
    
    user_id = StringField(required=True)  # Reference to User ID
    activity_type = StringField(max_length=50, required=True)  # login, booking, release, etc.
    activity_data = StringField()  # JSON data for additional info
    timestamp = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        """Convert activity object to dictionary"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'activity_data': self.activity_data,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

# Legacy SQLAlchemy models (commented out)
"""
class User(db.Model):
    # ... SQLAlchemy User model code commented out ...
    pass

class ParkingLot(db.Model):
    # ... SQLAlchemy ParkingLot model code commented out ...
    pass

class ParkingSpot(db.Model):
    # ... SQLAlchemy ParkingSpot model code commented out ...
    pass

class Reservation(db.Model):
    # ... SQLAlchemy Reservation model code commented out ...
    pass

class ExportJob(db.Model):
    # ... SQLAlchemy ExportJob model code commented out ...
    pass

class UserActivity(db.Model):
    # ... SQLAlchemy UserActivity model code commented out ...
    pass
""" 