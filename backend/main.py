#!/usr/bin/env python3
"""
Main entry point for Google App Engine deployment
"""

import os
import logging
from app import create_app, init_database, start_background_services

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask app
app = create_app()

# Initialize database on app startup
try:
    init_database(app)
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")

# Start background services
try:
    start_background_services(app)
    logger.info("Background services started successfully")
except Exception as e:
    logger.error(f"Background services startup failed: {str(e)}")

# Create temp directory for file uploads
temp_dir = app.config.get('UPLOAD_FOLDER', 'temp_files')
os.makedirs(temp_dir, exist_ok=True)

# Log startup information
logger.info("Vehicle Parking App - Backend deployed to Google Cloud")
logger.info("API Health Check: /health")
logger.info("API Documentation: /")

if __name__ == '__main__':
    # This is used when running locally
    app.run(debug=False, host='0.0.0.0', port=8080)
else:
    # This is the entry point for App Engine
    logger.info("App Engine entry point loaded successfully") 