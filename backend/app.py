from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
# MongoDB imports
from mongoengine import connect
from models import User, ParkingLot, ParkingSpot, ExportJob, UserActivity
from auth import auth_bp
from admin_routes import admin_bp
from user_routes import user_bp
from export_routes import export_bp
from email_service import mail
from cache_service import CacheService
from scheduler import SchedulerService, SimpleScheduler
from background_jobs import make_celery, is_celery_available  # Re-enabled Celery
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize MongoDB connection
    try:
        connect(host=app.config['MONGODB_SETTINGS']['host'])
        logger.info("MongoDB connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
    
    # Initialize extensions
    # db.init_app(app)  # Commented out - SQLAlchemy dependency
    jwt = JWTManager(app)
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize email service
    mail.init_app(app)
    
    # Initialize cache service (Redis or fallback to simple cache)
    try:
        CacheService.init_cache(app)
        logger.info("Cache service initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize cache service: {str(e)}")
    
    # Initialize Celery for background jobs
    try:
        celery = make_celery(app)
        app.celery = celery
        if is_celery_available():
            logger.info("Celery initialized successfully")
        else:
            logger.info("Celery fallback mode - synchronous execution")
    except Exception as e:
        logger.warning(f"Failed to initialize Celery: {str(e)}")
    
    # Initialize scheduler
    try:
        scheduler = SchedulerService(app)
        app.scheduler = scheduler
        logger.info("Scheduler service initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize scheduler service: {str(e)}")
        # Fallback to simple scheduler
        try:
            scheduler = SimpleScheduler(app)
            app.scheduler = scheduler
            logger.info("Simple scheduler initialized as fallback")
        except Exception as e2:
            logger.error(f"Failed to initialize any scheduler: {str(e2)}")
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(export_bp)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"JWT expired token error: header={jwt_header}, payload={jwt_payload}")
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"JWT invalid token error: {error}")
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"JWT missing token error: {error}")
        return jsonify({'error': 'Authorization token is required'}), 401
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        cache_status = 'redis' if CacheService.is_redis_available() else 'simple'
        celery_status = 'active' if is_celery_available() else 'sync_fallback'
        
        return jsonify({
            'status': 'healthy',
            'message': 'Vehicle Parking App API is running',
            'services': {
                'database': 'mongodb_connected',
                'cache': cache_status,
                'scheduler': 'active' if hasattr(app, 'scheduler') else 'disabled',
                'celery': celery_status
            }
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information"""
        job_mode = 'Async (Celery)' if is_celery_available() else 'Sync (Fallback)'
        cache_type = 'Redis Cache' if CacheService.is_redis_available() else 'Simple Cache'
        
        return jsonify({
            'message': 'Vehicle Parking App API',
            'version': '4.0',
            'database': 'MongoDB',
            'features': [
                'JWT Authentication',
                'Role-based Access Control',
                'Parking Management',
                f'Background Jobs ({job_mode})',
                'Email Notifications',
                'CSV Export',
                cache_type,
                'Scheduled Tasks'
            ],
            'endpoints': {
                'auth': {
                    'login': '/auth/login',
                    'register': '/auth/register',
                    'verify': '/auth/verify'
                },
                'admin': {
                    'parking_lots': '/admin/parking-lots',
                    'users': '/admin/users',
                    'dashboard': '/admin/dashboard'
                },
                'user': {
                    'parking_lots': '/user/parking-lots',
                    'book_spot': '/user/book-spot',
                    'release_spot': '/user/release-spot',
                    'reservations': '/user/reservations',
                    'dashboard': '/user/dashboard'
                },
                'export': {
                    'request_csv': '/api/export/csv/request',
                    'status': '/api/export/csv/status/<job_id>',
                    'download': '/api/export/download/<job_id>',
                    'history': '/api/export/csv/history'
                }
            }
        }), 200
    
    # Admin endpoint for job management
    @app.route('/admin/jobs', methods=['GET'])
    def admin_jobs():
        """Admin endpoint to view scheduled jobs"""
        try:
            job_info = {
                'celery_available': is_celery_available(),
                'execution_mode': 'async' if is_celery_available() else 'sync'
            }
            
            if hasattr(app, 'scheduler'):
                jobs = app.scheduler.get_jobs()
                job_info.update({
                    'scheduled_jobs': jobs,
                    'scheduler_type': type(app.scheduler).__name__
                })
            else:
                job_info['scheduler'] = 'not_available'
            
            return jsonify(job_info), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Admin endpoint for cache management
    @app.route('/admin/cache/clear', methods=['POST'])
    def admin_clear_cache():
        """Admin endpoint to clear cache"""
        try:
            from cache_service import CacheStats
            if CacheStats.clear_all_cache():
                return jsonify({'message': 'Cache cleared successfully'}), 200
            else:
                return jsonify({'error': 'Failed to clear cache'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Admin endpoint for cache info
    @app.route('/admin/cache/info', methods=['GET'])
    def admin_cache_info():
        """Admin endpoint to get cache information"""
        try:
            from cache_service import CacheStats
            cache_info = CacheStats.get_cache_info()
            return jsonify(cache_info), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

def init_database(app):
    """Initialize database with collections and default admin user"""
    with app.app_context():
        # MongoDB doesn't require explicit table creation
        print("MongoDB collections will be created automatically!")
        
        # Check if admin user already exists
        admin_user = User.objects(username='admin').first()
        
        if not admin_user:
            # Create default admin user
            admin_user = User(
                username='admin',
                email='admin@parkingapp.com',
                role='admin'
            )
            admin_user.set_password('admin123')
            admin_user.save()
            
            print("Default admin user created!")
            print("Username: admin")
            print("Email: admin@parkingapp.com")
            print("Password: admin123")
        else:
            print("Admin user already exists!")
        
        # Create sample parking lots if none exist
        if ParkingLot.objects.count() == 0:
            sample_lots = [
                {
                    'prime_location_name': 'City Center Mall',
                    'address': '123 Main Street, Downtown',
                    'pin_code': '12345',
                    'number_of_spots': 50,
                    'price': 5.0
                },
                {
                    'prime_location_name': 'Airport Terminal 1',
                    'address': '456 Airport Road',
                    'pin_code': '54321',
                    'number_of_spots': 100,
                    'price': 8.0
                },
                {
                    'prime_location_name': 'Business District Plaza',
                    'address': '789 Corporate Avenue',
                    'pin_code': '67890',
                    'number_of_spots': 75,
                    'price': 6.5
                }
            ]
            
            for lot_data in sample_lots:
                lot = ParkingLot(**lot_data)
                lot.save()
                
                # Create parking spots for this lot
                for i in range(1, lot_data['number_of_spots'] + 1):
                    spot = ParkingSpot(
                        lot_id=str(lot.id),
                        spot_number=f"P{i:03d}",
                        status='A'
                    )
                    spot.save()
            
            print("Sample parking lots created!")
        
        # Create sample regular user if none exist
        if User.objects(role='user').count() == 0:
            sample_user = User(
                username='testuser',
                email='testuser@example.com',
                role='user'
            )
            sample_user.set_password('password123')
            sample_user.save()
            
            print("Sample user created!")
            print("Username: testuser")
            print("Email: testuser@example.com")
            print("Password: password123")

def start_background_services(app):
    """Start background services like scheduler"""
    try:
        if hasattr(app, 'scheduler'):
            app.scheduler.start()
            logger.info("Background services started successfully")
        else:
            logger.warning("No scheduler available to start")
    except Exception as e:
        logger.error(f"Failed to start background services: {str(e)}")

if __name__ == '__main__':
    app = create_app()
    
    # Initialize database
    init_database(app)
    
    # Start background services
    start_background_services(app)
    
    # Create temp directory for file uploads
    temp_dir = app.config.get('UPLOAD_FOLDER', 'temp_files')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Run the application
    print("\n" + "="*60)
    print("Vehicle Parking App - Backend Server Starting")
    print("="*60)
    print("Server URL: http://localhost:5000")
    print("Admin Login: username=admin, password=admin123")
    print("Test User: username=testuser, password=password123")
    print("API Documentation: http://localhost:5000")
    print("\nUpdated Features:")
    print("• MongoDB Database")
    print("• Background Jobs (Synchronous)")
    print("• CSV Export with Processing")
    print("• Email Notifications")
    print("• Simple In-Memory Caching")
    print("• Scheduled Task Management")
    print("• Redis Dependencies Removed")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 