# Background Jobs - Celery functionality commented out, using simple synchronous jobs
# from celery import Celery  # Commented out - Redis/Celery dependency
from datetime import datetime, timedelta
# from sqlalchemy import func, and_, or_  # Commented out - SQLAlchemy dependency
from flask import current_app
import pandas as pd
import os
import logging
from email_service import EmailService, NotificationService
# from models import db, User, ParkingLot, Reservation, ExportJob, UserActivity  # Updated for MongoDB
from models import User, ParkingLot, Reservation, ExportJob, UserActivity
from cache_service import CacheService
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Legacy Celery code (commented out)
"""
def make_celery(app):
    # Create Celery instance and configure it with Flask app
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        # Make celery tasks work with Flask app context
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Global celery instance - will be set by make_celery
celery = None
"""

# Simple job execution without Celery
def make_celery(app):
    """Placeholder function for Celery initialization (disabled)"""
    logger.info("Celery disabled - using synchronous job execution")
    return None

# Placeholder task decorators - these will be replaced when celery is initialized
def task_decorator(func):
    """Placeholder decorator for when celery is not available"""
    func.delay = lambda *args, **kwargs: func(*args, **kwargs)
    return func

@task_decorator
def daily_reminder_job():
    """
    Daily reminder job - Check inactive users and send reminders
    
    This job runs daily and:
    1. Identifies users who haven't logged in or booked recently
    2. Checks if parking lots are available
    3. Sends reminder emails/notifications
    """
    try:
        logger.info("Starting daily reminder job")
        
        # Calculate cutoff dates
        login_cutoff = datetime.utcnow() - timedelta(days=7)  # 7 days since last login
        booking_cutoff = datetime.utcnow() - timedelta(days=14)  # 14 days since last booking
        
        # Find inactive users (regular users only, not admins) - MongoDB query
        inactive_users = User.objects(
            role='user',
            email__ne=None,  # Only users with email addresses
        )
        
        # Filter inactive users
        filtered_users = []
        for user in inactive_users:
            is_inactive = (
                user.last_login is None or user.last_login < login_cutoff or
                user.last_booking is None or user.last_booking < booking_cutoff
            )
            if is_inactive:
                filtered_users.append(user)
        
        # Get count of available parking lots
        parking_lots_count = ParkingLot.objects.count()
        
        # Send reminders
        sent_count = 0
        failed_count = 0
        
        for user in filtered_users:
            try:
                # Send email reminder
                if EmailService.send_daily_reminder(user, parking_lots_count):
                    sent_count += 1
                    
                    # Log activity
                    activity = UserActivity(
                        user_id=str(user.id),
                        activity_type='reminder_sent',
                        activity_data=json.dumps({
                            'type': 'daily_reminder',
                            'parking_lots_count': parking_lots_count
                        })
                    )
                    activity.save()
                    
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to send reminder to user {user.id}: {str(e)}")
                failed_count += 1
        
        # Send summary to Google Chat if configured
        summary_message = f"""
        📅 Daily Reminder Job Completed
        
        • Inactive users found: {len(filtered_users)}
        • Reminders sent successfully: {sent_count}
        • Failed to send: {failed_count}
        • Available parking lots: {parking_lots_count}
        
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """
        
        NotificationService.send_google_chat_notification(summary_message)
        
        logger.info(f"Daily reminder job completed. Sent: {sent_count}, Failed: {failed_count}")
        
        return {
            'status': 'completed',
            'inactive_users': len(filtered_users),
            'sent_count': sent_count,
            'failed_count': failed_count,
            'parking_lots_count': parking_lots_count
        }
        
    except Exception as e:
        logger.error(f"Daily reminder job failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}

@task_decorator
def monthly_report_job():
    """
    Monthly activity report job - Generate and send monthly reports to users
    
    This job runs on the first day of each month and:
    1. Generates activity reports for all users
    2. Calculates statistics for the previous month
    3. Sends detailed HTML reports via email
    """
    try:
        logger.info("Starting monthly report job")
        
        # Calculate previous month date range
        today = datetime.utcnow()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        month_year = last_day_previous_month.strftime('%B %Y')
        
        # Get all users with email addresses - MongoDB query
        users_with_email = User.objects(
            role='user',
            email__ne=None
        )
        
        sent_count = 0
        failed_count = 0
        
        for user in users_with_email:
            try:
                # Generate report data for this user
                report_data = generate_user_monthly_report(
                    str(user.id), 
                    first_day_previous_month, 
                    last_day_previous_month
                )
                
                report_data['month_year'] = month_year
                
                # Send report email
                if EmailService.send_monthly_report(user, report_data):
                    sent_count += 1
                    
                    # Log activity
                    activity = UserActivity(
                        user_id=str(user.id),
                        activity_type='monthly_report_sent',
                        activity_data=json.dumps({
                            'month_year': month_year,
                            'total_bookings': report_data['total_bookings'],
                            'total_spent': report_data['total_spent']
                        })
                    )
                    activity.save()
                    
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to send monthly report to user {user.id}: {str(e)}")
                failed_count += 1
        
        # Send summary notification
        summary_message = f"""
        📊 Monthly Report Job Completed
        
        • Report period: {month_year}
        • Users processed: {len(users_with_email)}
        • Reports sent successfully: {sent_count}
        • Failed to send: {failed_count}
        
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """
        
        NotificationService.send_google_chat_notification(summary_message)
        
        logger.info(f"Monthly report job completed. Sent: {sent_count}, Failed: {failed_count}")
        
        return {
            'status': 'completed',
            'month_year': month_year,
            'users_processed': len(users_with_email),
            'sent_count': sent_count,
            'failed_count': failed_count
        }
        
    except Exception as e:
        logger.error(f"Monthly report job failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}

@task_decorator
def export_user_csv_job(user_id, job_id):
    """
    Sync CSV export job - Generate CSV file with user's parking history
    
    Args:
        user_id (str): ID of the user requesting the export
        job_id (str): Unique job identifier
    """
    try:
        logger.info(f"Starting CSV export job for user {user_id}, job {job_id}")
        
        # Update job status to processing
        job = ExportJob.objects(job_id=job_id).first()
        if not job:
            raise Exception(f"Export job {job_id} not found")
        
        job.status = 'processing'
        job.save()
        
        # Get user
        user = User.objects(id=user_id).first()
        if not user:
            raise Exception(f"User {user_id} not found")
        
        # Get user's reservation history - MongoDB query
        reservations = Reservation.objects(user_id=user_id).order_by('-parking_timestamp')
        
        if not reservations:
            # Create empty CSV for users with no history
            csv_data = pd.DataFrame(columns=[
                'Reservation ID', 'Spot ID', 'Spot Number', 'Parking Lot', 
                'Address', 'Vehicle Number', 'Parking Start', 'Parking End', 
                'Duration (Hours)', 'Cost ($)', 'Status', 'Created At'
            ])
        else:
            # Prepare data for CSV
            csv_data = []
            for reservation in reservations:
                # Get related objects
                parking_spot = ParkingSpot.objects(id=reservation.spot_id).first()
                parking_lot = None
                if parking_spot:
                    parking_lot = ParkingLot.objects(id=parking_spot.lot_id).first()
                
                duration_hours = 0
                if reservation.leaving_timestamp:
                    duration = reservation.leaving_timestamp - reservation.parking_timestamp
                    duration_hours = round(duration.total_seconds() / 3600, 2)
                
                csv_data.append({
                    'Reservation ID': str(reservation.id),
                    'Spot ID': reservation.spot_id,
                    'Spot Number': parking_spot.spot_number if parking_spot else 'Unknown',
                    'Parking Lot': parking_lot.prime_location_name if parking_lot else 'Unknown',
                    'Address': parking_lot.address if parking_lot else 'Unknown',
                    'Vehicle Number': reservation.vehicle_number,
                    'Parking Start': reservation.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Parking End': reservation.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if reservation.leaving_timestamp else 'Active',
                    'Duration (Hours)': duration_hours,
                    'Cost ($)': reservation.parking_cost or 0,
                    'Status': 'Completed' if reservation.leaving_timestamp else 'Active',
                    'Created At': reservation.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            csv_data = pd.DataFrame(csv_data)
        
        # Create temp directory if it doesn't exist
        temp_dir = current_app.config.get('UPLOAD_FOLDER', 'temp_files')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"parking_history_{user.username}_{timestamp}.csv"
        file_path = os.path.join(temp_dir, filename)
        
        # Save CSV file
        csv_data.to_csv(file_path, index=False)
        
        # Update job with completion details
        job.status = 'completed'
        job.file_path = file_path
        job.download_url = f"/api/export/download/{job_id}"
        job.completed_at = datetime.utcnow()
        job.expires_at = datetime.utcnow() + timedelta(
            hours=current_app.config.get('CSV_EXPORT_EXPIRY_HOURS', 24)
        )
        
        job.save()
        
        # Send notification email
        EmailService.send_csv_export_notification(user, job)
        
        # Log activity
        activity = UserActivity(
            user_id=user_id,
            activity_type='csv_export_completed',
            activity_data=json.dumps({
                'job_id': job_id,
                'filename': filename,
                'record_count': len(csv_data)
            })
        )
        activity.save()
        
        logger.info(f"CSV export job completed for user {user_id}, job {job_id}")
        
        return {
            'status': 'completed',
            'job_id': job_id,
            'filename': filename,
            'record_count': len(csv_data),
            'file_path': file_path
        }
        
    except Exception as e:
        logger.error(f"CSV export job failed for user {user_id}, job {job_id}: {str(e)}")
        
        # Update job status to failed
        try:
            job = ExportJob.objects(job_id=job_id).first()
            if job:
                job.status = 'failed'
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                job.save()
                
                # Send failure notification
                user = User.objects(id=user_id).first()
                if user:
                    EmailService.send_csv_export_notification(user, job)
        except Exception as update_error:
            logger.error(f"Failed to update job status: {str(update_error)}")
        
        return {'status': 'failed', 'error': str(e)}

@task_decorator
def cleanup_expired_files_job():
    """
    Cleanup job - Remove expired CSV export files
    
    This job runs daily to clean up expired export files
    """
    try:
        logger.info("Starting cleanup job for expired files")
        
        # Find expired export jobs - MongoDB query
        expired_jobs = ExportJob.objects(
            expires_at__lt=datetime.utcnow(),
            status='completed',
            file_path__ne=None
        )
        
        cleaned_count = 0
        
        for job in expired_jobs:
            try:
                # Remove file if it exists
                if os.path.exists(job.file_path):
                    os.remove(job.file_path)
                    logger.info(f"Removed expired file: {job.file_path}")
                
                # Update job record
                job.file_path = None
                job.download_url = None
                job.save()
                cleaned_count += 1
                
            except Exception as e:
                logger.error(f"Failed to clean up file for job {job.job_id}: {str(e)}")
        
        logger.info(f"Cleanup job completed. Cleaned {cleaned_count} expired files")
        
        return {
            'status': 'completed',
            'cleaned_count': cleaned_count
        }
        
    except Exception as e:
        logger.error(f"Cleanup job failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}

def generate_user_monthly_report(user_id, start_date, end_date):
    """
    Generate monthly report data for a specific user
    
    Args:
        user_id (str): User ID
        start_date (datetime): Start of the month
        end_date (datetime): End of the month
    
    Returns:
        dict: Report data
    """
    # Get reservations for the month - MongoDB query
    reservations = Reservation.objects(
        user_id=user_id,
        parking_timestamp__gte=start_date,
        parking_timestamp__lte=end_date
    )
    
    total_bookings = len(reservations)
    total_spent = sum([r.parking_cost or 0 for r in reservations])
    
    # Calculate total hours
    total_hours = 0
    for reservation in reservations:
        if reservation.leaving_timestamp:
            duration = reservation.leaving_timestamp - reservation.parking_timestamp
            total_hours += duration.total_seconds() / 3600
    
    total_hours = round(total_hours, 1)
    
    # Find most used parking lot
    most_used_lot = None
    if reservations:
        lot_usage = {}
        for reservation in reservations:
            parking_spot = ParkingSpot.objects(id=reservation.spot_id).first()
            if parking_spot:
                parking_lot = ParkingLot.objects(id=parking_spot.lot_id).first()
                if parking_lot:
                    lot_name = parking_lot.prime_location_name
                    lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1
        
        most_used_lot = max(lot_usage, key=lot_usage.get) if lot_usage else None
    
    # Get recent bookings for the table
    recent_bookings = []
    for reservation in list(reservations)[-5:]:  # Last 5 bookings
        parking_spot = ParkingSpot.objects(id=reservation.spot_id).first()
        parking_lot = None
        if parking_spot:
            parking_lot = ParkingLot.objects(id=parking_spot.lot_id).first()
        
        recent_bookings.append({
            'date': reservation.parking_timestamp.strftime('%Y-%m-%d'),
            'location': parking_lot.prime_location_name if parking_lot else 'Unknown',
            'spot': parking_spot.spot_number if parking_spot else 'Unknown',
            'cost': f"{reservation.parking_cost or 0:.2f}"
        })
    
    return {
        'total_bookings': total_bookings,
        'total_spent': f"{total_spent:.2f}",
        'total_hours': total_hours,
        'most_used_lot': most_used_lot,
        'recent_bookings': recent_bookings
    }

def register_celery_tasks(celery_instance):
    """Register tasks with the actual Celery instance (disabled)"""
    logger.info("Celery task registration disabled - using synchronous execution")
    pass

# Legacy Celery code (commented out)
"""
# All the original Celery-related code is commented out here
# ... extensive Celery implementation ...
""" 