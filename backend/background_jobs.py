# Background Jobs - Celery integration with fallback to synchronous execution
from celery import Celery
from datetime import datetime, timedelta
from flask import current_app
import pandas as pd
import os
import logging
from email_service import EmailService, NotificationService
from models import User, ParkingLot, Reservation, ExportJob, UserActivity
from cache_service import CacheService
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global celery instance
celery = None

def make_celery(app):
    """Create Celery instance and configure it with Flask app"""
    global celery
    try:
        # Redis disabled - Celery configuration commented out
        # celery = Celery(
        #     app.import_name,
        #     backend=app.config['CELERY_RESULT_BACKEND'],
        #     broker=app.config['CELERY_BROKER_URL']
        # )
        
        # celery.conf.update(app.config)
        
        # class ContextTask(celery.Task):
        #     """Make celery tasks work with Flask app context"""
        #     def __call__(self, *args, **kwargs):
        #         with app.app_context():
        #             return self.run(*args, **kwargs)
        
        # celery.Task = ContextTask
        
        # Test the connection
        # celery.control.inspect().stats()
        
        # logger.info("Celery initialized successfully")
        # return celery
        
        # Redis disabled - return None instead of Celery instance
        logger.info("Redis/Celery disabled - using synchronous job execution")
        celery = None
        return None
        
    except Exception as e:
        logger.warning(f"Celery initialization failed: {str(e)}")
        logger.info("Falling back to synchronous job execution")
        celery = None
        return None

def is_celery_available():
    """Check if Celery is available and working"""
    return celery is not None

def task_decorator(func):
    """Smart decorator that uses Celery if available, otherwise executes synchronously"""
    if celery:
        # Use Celery task decorator
        task_func = celery.task(func)
        return task_func
    else:
        # Fallback: add a 'delay' method that executes synchronously
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
        
        # Send summary to Google Chat if configured
        summary_message = f"""
        📊 Monthly Report Job Completed ({month_year})
        
        • Users with email: {len(users_with_email)}
        • Reports sent successfully: {sent_count}
        • Failed to send: {failed_count}
        
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """
        
        NotificationService.send_google_chat_notification(summary_message)
        
        logger.info(f"Monthly report job completed. Sent: {sent_count}, Failed: {failed_count}")
        
        return {
            'status': 'completed',
            'users_count': len(users_with_email),
            'sent_count': sent_count,
            'failed_count': failed_count,
            'month_year': month_year
        }
        
    except Exception as e:
        logger.error(f"Monthly report job failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}

@task_decorator
def export_user_csv_job(user_id, job_id):
    """
    Background job to export user data to CSV
    
    Args:
        user_id (str): ID of the user requesting the export
        job_id (str): Export job ID for tracking
    """
    try:
        logger.info(f"Starting CSV export job {job_id} for user {user_id}")
        
        # Get the export job - MongoDB query
        export_job = ExportJob.objects(id=job_id).first()
        if not export_job:
            logger.error(f"Export job {job_id} not found")
            return {'status': 'failed', 'error': 'Job not found'}
        
        # Update job status to processing
        export_job.status = 'processing'
        export_job.started_at = datetime.utcnow()
        export_job.save()
        
        # Get user data - MongoDB query
        user = User.objects(id=user_id).first()
        if not user:
            export_job.status = 'failed'
            export_job.error_message = 'User not found'
            export_job.save()
            return {'status': 'failed', 'error': 'User not found'}
        
        # Determine data to export based on export type
        export_data = []
        
        if export_job.export_type == 'reservations':
            # Export user's reservations - MongoDB query
            reservations = Reservation.objects(user_id=user_id)
            
            for reservation in reservations:
                # Get parking lot info
                lot = ParkingLot.objects(id=reservation.lot_id).first()
                
                export_data.append({
                    'Reservation ID': str(reservation.id),
                    'Parking Lot': lot.prime_location_name if lot else 'Unknown',
                    'Address': lot.address if lot else 'Unknown',
                    'Spot Number': reservation.spot_number,
                    'Start Time': reservation.start_time.strftime('%Y-%m-%d %H:%M:%S') if reservation.start_time else '',
                    'End Time': reservation.end_time.strftime('%Y-%m-%d %H:%M:%S') if reservation.end_time else '',
                    'Duration (hours)': reservation.duration_hours,
                    'Price': f"${reservation.price:.2f}" if reservation.price else '$0.00',
                    'Status': reservation.status,
                    'Created At': reservation.created_at.strftime('%Y-%m-%d %H:%M:%S') if reservation.created_at else ''
                })
        
        elif export_job.export_type == 'activity':
            # Export user's activity log - MongoDB query
            activities = UserActivity.objects(user_id=user_id).order_by('-created_at')
            
            for activity in activities:
                activity_data = json.loads(activity.activity_data) if activity.activity_data else {}
                
                export_data.append({
                    'Activity ID': str(activity.id),
                    'Activity Type': activity.activity_type,
                    'Description': activity_data.get('description', ''),
                    'Details': json.dumps(activity_data) if activity_data else '',
                    'IP Address': activity.ip_address,
                    'User Agent': activity.user_agent,
                    'Created At': activity.created_at.strftime('%Y-%m-%d %H:%M:%S') if activity.created_at else ''
                })
        
        elif export_job.export_type == 'all_data':
            # Export comprehensive user data
            # This would include reservations, activities, and user profile info
            # For brevity, implementing basic version
            user_data = {
                'User ID': str(user.id),
                'Username': user.username,
                'Email': user.email,
                'Role': user.role,
                'Created At': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                'Last Login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
                'Total Reservations': Reservation.objects(user_id=user_id).count(),
                'Total Activities': UserActivity.objects(user_id=user_id).count()
            }
            export_data.append(user_data)
        
        if not export_data:
            export_job.status = 'completed'
            export_job.completed_at = datetime.utcnow()
            export_job.error_message = 'No data found to export'
            export_job.save()
            return {'status': 'completed', 'message': 'No data found'}
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(export_data)
        
        # Create export filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"export_{export_job.export_type}_{user_id}_{timestamp}.csv"
        
        # Get upload folder from config
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'temp_files')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        
        # Save CSV file
        df.to_csv(filepath, index=False)
        
        # Update job with success status
        export_job.status = 'completed'
        export_job.completed_at = datetime.utcnow()
        export_job.file_path = filepath
        export_job.file_name = filename
        export_job.records_count = len(export_data)
        export_job.save()
        
        # Send completion email if user has email
        if user.email:
            try:
                EmailService.send_csv_export_ready(user, export_job)
                logger.info(f"CSV export notification sent to {user.email}")
            except Exception as e:
                logger.warning(f"Failed to send export notification: {str(e)}")
        
        # Log activity
        activity = UserActivity(
            user_id=user_id,
            activity_type='csv_export_completed',
            activity_data=json.dumps({
                'job_id': str(export_job.id),
                'export_type': export_job.export_type,
                'records_count': len(export_data),
                'filename': filename
            })
        )
        activity.save()
        
        logger.info(f"CSV export job {job_id} completed successfully. File: {filename}")
        
        return {
            'status': 'completed',
            'job_id': str(export_job.id),
            'filename': filename,
            'records_count': len(export_data)
        }
        
    except Exception as e:
        logger.error(f"CSV export job {job_id} failed: {str(e)}")
        
        # Update job with error status
        try:
            export_job = ExportJob.objects(id=job_id).first()
            if export_job:
                export_job.status = 'failed'
                export_job.error_message = str(e)
                export_job.save()
        except:
            pass
        
        return {'status': 'failed', 'error': str(e)}

@task_decorator
def cleanup_expired_files_job():
    """
    Background job to clean up expired export files
    
    This job:
    1. Finds CSV export files older than configured expiry time
    2. Deletes the files from disk
    3. Updates export job records
    """
    try:
        logger.info("Starting cleanup expired files job")
        
        # Get expiry hours from config
        expiry_hours = current_app.config.get('CSV_EXPORT_EXPIRY_HOURS', 24)
        cutoff_time = datetime.utcnow() - timedelta(hours=expiry_hours)
        
        # Find expired export jobs - MongoDB query
        expired_jobs = ExportJob.objects(
            status='completed',
            completed_at__lt=cutoff_time,
            file_path__ne=None
        )
        
        deleted_count = 0
        error_count = 0
        
        for job in expired_jobs:
            try:
                # Delete file if it exists
                if job.file_path and os.path.exists(job.file_path):
                    os.remove(job.file_path)
                    logger.debug(f"Deleted expired file: {job.file_path}")
                
                # Update job record
                job.file_path = None
                job.file_name = None
                job.save()
                
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Failed to delete expired file {job.file_path}: {str(e)}")
                error_count += 1
        
        logger.info(f"Cleanup completed. Deleted: {deleted_count}, Errors: {error_count}")
        
        return {
            'status': 'completed',
            'deleted_count': deleted_count,
            'error_count': error_count,
            'expiry_hours': expiry_hours
        }
        
    except Exception as e:
        logger.error(f"Cleanup expired files job failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}

def generate_user_monthly_report(user_id, start_date, end_date):
    """
    Generate monthly report data for a specific user
    
    Args:
        user_id (str): User ID
        start_date (datetime): Start of the period
        end_date (datetime): End of the period
    
    Returns:
        dict: Report data
    """
    try:
        # Get user's reservations in the date range - MongoDB query
        reservations = Reservation.objects(
            user_id=user_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Calculate statistics
        total_bookings = len(reservations)
        total_spent = sum([r.price for r in reservations if r.price])
        total_hours = sum([r.duration_hours for r in reservations if r.duration_hours])
        
        # Get most used parking lot
        lot_usage = {}
        for reservation in reservations:
            if reservation.lot_id:
                lot_usage[reservation.lot_id] = lot_usage.get(reservation.lot_id, 0) + 1
        
        most_used_lot = None
        if lot_usage:
            most_used_lot_id = max(lot_usage.keys(), key=lambda k: lot_usage[k])
            lot = ParkingLot.objects(id=most_used_lot_id).first()
            most_used_lot = lot.prime_location_name if lot else 'Unknown'
        
        # Get user activities in the period
        activities = UserActivity.objects(
            user_id=user_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        activity_count = len(activities)
        
        return {
            'total_bookings': total_bookings,
            'total_spent': total_spent,
            'total_hours': total_hours,
            'most_used_lot': most_used_lot,
            'activity_count': activity_count,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
        
    except Exception as e:
        logger.error(f"Failed to generate monthly report for user {user_id}: {str(e)}")
        return {
            'total_bookings': 0,
            'total_spent': 0,
            'total_hours': 0,
            'most_used_lot': None,
            'activity_count': 0,
            'error': str(e)
        }

def register_celery_tasks(celery_instance):
    """Register all background tasks with Celery instance"""
    if celery_instance:
        logger.info("Registering Celery tasks")
        # Tasks are automatically registered when decorated with @celery.task
        return True
    else:
        logger.info("Celery not available - tasks will run synchronously")
        return False

def get_job_status():
    """Get status of background job system"""
    return {
        'celery_available': is_celery_available(),
        'execution_mode': 'async' if is_celery_available() else 'sync',
        'tasks_registered': True
    } 