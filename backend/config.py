import os
from datetime import timedelta

class Config:
    """Configuration class for Flask application"""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MongoDB configuration - Replace PostgreSQL with MongoDB
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/parking_app',
        'connect': False  # Disable automatic connection for better error handling
    }
    
    # Legacy SQLAlchemy config (commented out for MongoDB migration)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/parking_app'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',') if os.environ.get('CORS_ORIGINS') else ['http://localhost:3000']
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-app-password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'your-email@gmail.com'
    
    # Caching configuration (commented out - Redis dependency)
    # CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'redis'
    # CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or 'redis://localhost:6379/0'
    # CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT') or 300)  # 5 minutes
    
    # Celery configuration (commented out - Redis dependency)
    # CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/1'
    # CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/1'
    
    # Scheduler configuration (modified to use memory store instead of Redis)
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = os.environ.get('SCHEDULER_TIMEZONE') or 'UTC'
    SCHEDULER_JOBSTORE = 'memory'  # Use memory instead of Redis
    
    # Job configuration
    DAILY_REMINDER_TIME = os.environ.get('DAILY_REMINDER_TIME') or '18:00'  # 6 PM
    MONTHLY_REPORT_DAY = int(os.environ.get('MONTHLY_REPORT_DAY') or 1)  # 1st day of month
    MONTHLY_REPORT_TIME = os.environ.get('MONTHLY_REPORT_TIME') or '09:00'  # 9 AM
    
    # File storage configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'temp_files'
    CSV_EXPORT_EXPIRY_HOURS = int(os.environ.get('CSV_EXPORT_EXPIRY_HOURS') or 24)
    
    # Google Chat Webhook (optional)
    GOOGLE_CHAT_WEBHOOK_URL = os.environ.get('GOOGLE_CHAT_WEBHOOK_URL')
    
    # SMS configuration (optional - using Twilio as example)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER') 