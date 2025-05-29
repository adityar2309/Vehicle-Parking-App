from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
# from models import db, User  # Updated for MongoDB
from models import User
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_username(username):
    """Validate username format"""
    if not username or len(username) < 3:
        return False
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None

def validate_password(password):
    """Validate password strength"""
    if not password or len(password) < 6:
        return False
    return True

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not validate_username(username):
            return jsonify({'error': 'Username must be at least 3 characters and contain only letters, numbers, and underscores'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists - MongoDB query
        if User.objects(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        # Create new user
        user = User(username=username, role='user')
        user.set_password(password)
        user.save()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Registration failed: ' + str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user - MongoDB query
        user = User.objects(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create access token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role, 'username': user.username}
        )
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed: ' + str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token and return user info"""
    try:
        print("=== JWT Verify Debug ===")
        user_id = get_jwt_identity()
        print(f"User ID from token: {user_id}")
        
        # Convert string user_id to string for MongoDB lookup
        user_id = str(user_id)
        user = User.objects(id=user_id).first()
        print(f"User found in database: {user}")
        
        if not user:
            print("User not found in database")
            return jsonify({'error': 'User not found'}), 404
        
        print("Token verification successful")
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Token verification error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Token verification failed: ' + str(e)}), 500 