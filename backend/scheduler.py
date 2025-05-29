from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.jobstores.redis import RedisJobStore  # Commented out - Redis dependency
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime, time
import logging
import atexit
from background_jobs import daily_reminder_job, monthly_report_job, cleanup_expired_files_job

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    """Service class for managing scheduled jobs using APScheduler"""
    
    def __init__(self, app=None):
        self.scheduler = None
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize scheduler with Flask app"""
        self.app = app
        
        # Configure job stores and executors (using memory instead of Redis)
        jobstores = {
            'default': MemoryJobStore()  # Use memory instead of Redis
            # 'default': RedisJobStore(  # Commented out - Redis dependency
            #     host='localhost',
            #     port=6379,
            #     db=2,  # Use different DB than cache
            #     password=None
            # )
        }
        
        executors = {
            'default': ThreadPoolExecutor(20),
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        # Create scheduler
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=app.config.get('SCHEDULER_TIMEZONE', 'UTC')
        )
        
        # Register shutdown handler
        atexit.register(lambda: self.shutdown())
        
        logger.info("Scheduler service initialized (using memory job store)")
    
    def start(self):
        """Start the scheduler and add all jobs"""
        if not self.scheduler:
            logger.error("Scheduler not initialized")
            return False
        
        try:
            # Start the scheduler
            self.scheduler.start()
            
            # Add scheduled jobs
            self.add_daily_reminder_job()
            self.add_monthly_report_job()
            self.add_cleanup_job()
            
            logger.info("Scheduler started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            return False
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")
    
    def add_daily_reminder_job(self):
        """Add daily reminder job to scheduler"""
        try:
            # Parse time from config
            reminder_time_str = self.app.config.get('DAILY_REMINDER_TIME', '18:00')
            hour, minute = map(int, reminder_time_str.split(':'))
            
            # Add job to run daily at specified time
            self.scheduler.add_job(
                func=self._run_daily_reminder_job,
                trigger='cron',
                hour=hour,
                minute=minute,
                id='daily_reminder_job',
                name='Daily Reminder Job',
                replace_existing=True,
                misfire_grace_time=3600  # 1 hour grace time
            )
            
            logger.info(f"Daily reminder job scheduled for {reminder_time_str} daily")
            
        except Exception as e:
            logger.error(f"Failed to add daily reminder job: {str(e)}")
    
    def add_monthly_report_job(self):
        """Add monthly report job to scheduler"""
        try:
            # Parse time from config
            report_time_str = self.app.config.get('MONTHLY_REPORT_TIME', '09:00')
            hour, minute = map(int, report_time_str.split(':'))
            report_day = self.app.config.get('MONTHLY_REPORT_DAY', 1)
            
            # Add job to run monthly on specified day and time
            self.scheduler.add_job(
                func=self._run_monthly_report_job,
                trigger='cron',
                day=report_day,
                hour=hour,
                minute=minute,
                id='monthly_report_job',
                name='Monthly Report Job',
                replace_existing=True,
                misfire_grace_time=7200  # 2 hours grace time
            )
            
            logger.info(f"Monthly report job scheduled for day {report_day} at {report_time_str}")
            
        except Exception as e:
            logger.error(f"Failed to add monthly report job: {str(e)}")
    
    def add_cleanup_job(self):
        """Add cleanup job to scheduler"""
        try:
            # Run cleanup job daily at 2 AM
            self.scheduler.add_job(
                func=self._run_cleanup_job,
                trigger='cron',
                hour=2,
                minute=0,
                id='cleanup_job',
                name='Cleanup Expired Files Job',
                replace_existing=True,
                misfire_grace_time=3600  # 1 hour grace time
            )
            
            logger.info("Cleanup job scheduled for 2:00 AM daily")
            
        except Exception as e:
            logger.error(f"Failed to add cleanup job: {str(e)}")
    
    def _run_daily_reminder_job(self):
        """Wrapper to run daily reminder job with app context"""
        with self.app.app_context():
            try:
                logger.info("Executing daily reminder job")
                # result = daily_reminder_job.delay()  # Commented out - Celery dependency
                result = daily_reminder_job()  # Direct execution instead of Celery
                logger.info(f"Daily reminder job completed: {result}")
            except Exception as e:
                logger.error(f"Failed to execute daily reminder job: {str(e)}")
    
    def _run_monthly_report_job(self):
        """Wrapper to run monthly report job with app context"""
        with self.app.app_context():
            try:
                logger.info("Executing monthly report job")
                # result = monthly_report_job.delay()  # Commented out - Celery dependency
                result = monthly_report_job()  # Direct execution instead of Celery
                logger.info(f"Monthly report job completed: {result}")
            except Exception as e:
                logger.error(f"Failed to execute monthly report job: {str(e)}")
    
    def _run_cleanup_job(self):
        """Wrapper to run cleanup job with app context"""
        with self.app.app_context():
            try:
                logger.info("Executing cleanup job")
                # result = cleanup_expired_files_job.delay()  # Commented out - Celery dependency
                result = cleanup_expired_files_job()  # Direct execution instead of Celery
                logger.info(f"Cleanup job completed: {result}")
            except Exception as e:
                logger.error(f"Failed to execute cleanup job: {str(e)}")
    
    def get_jobs(self):
        """Get list of all scheduled jobs"""
        if not self.scheduler:
            return []
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return jobs
    
    def pause_job(self, job_id):
        """Pause a specific job"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job {job_id} paused")
            return True
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {str(e)}")
            return False
    
    def resume_job(self, job_id):
        """Resume a specific job"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job {job_id} resumed")
            return True
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {str(e)}")
            return False
    
    def run_job_now(self, job_id):
        """Run a specific job immediately"""
        try:
            job = self.scheduler.get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return False
            
            # Execute the job function
            job.func()
            logger.info(f"Job {job_id} executed manually")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run job {job_id}: {str(e)}")
            return False
    
    def get_job_status(self, job_id):
        """Get status of a specific job"""
        try:
            job = self.scheduler.get_job(job_id)
            if not job:
                return {'status': 'not_found'}
            
            return {
                'status': 'active',
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}

# Alternative simple scheduler using threading (fallback option)
import threading
import time as time_module

class SimpleScheduler:
    """Simple scheduler implementation as fallback when APScheduler is not available"""
    
    def __init__(self, app=None):
        self.app = app
        self.running = False
        self.threads = []
    
    def init_app(self, app):
        """Initialize simple scheduler with Flask app"""
        self.app = app
        logger.info("Simple scheduler initialized (fallback mode)")
    
    def start(self):
        """Start the simple scheduler"""
        self.running = True
        
        # Start daily reminder thread
        daily_thread = threading.Thread(target=self._daily_reminder_loop, daemon=True)
        daily_thread.start()
        self.threads.append(daily_thread)
        
        # Start monthly report thread
        monthly_thread = threading.Thread(target=self._monthly_report_loop, daemon=True)
        monthly_thread.start()
        self.threads.append(monthly_thread)
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        cleanup_thread.start()
        self.threads.append(cleanup_thread)
        
        logger.info("Simple scheduler started")
        return True
    
    def shutdown(self):
        """Shutdown the simple scheduler"""
        self.running = False
        logger.info("Simple scheduler shutdown")
    
    def _daily_reminder_loop(self):
        """Loop for daily reminder job"""
        while self.running:
            try:
                now = datetime.now()
                reminder_time_str = self.app.config.get('DAILY_REMINDER_TIME', '18:00')
                hour, minute = map(int, reminder_time_str.split(':'))
                
                if now.hour == hour and now.minute == minute:
                    with self.app.app_context():
                        logger.info("Executing daily reminder job (simple scheduler)")
                        # daily_reminder_job.delay()  # Commented out - Celery dependency
                        daily_reminder_job()  # Direct execution
                    
                    # Sleep for 60 seconds to avoid running multiple times in the same minute
                    time_module.sleep(60)
                
                time_module.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in daily reminder loop: {str(e)}")
                time_module.sleep(60)
    
    def _monthly_report_loop(self):
        """Loop for monthly report job"""
        while self.running:
            try:
                now = datetime.now()
                report_time_str = self.app.config.get('MONTHLY_REPORT_TIME', '09:00')
                hour, minute = map(int, report_time_str.split(':'))
                report_day = self.app.config.get('MONTHLY_REPORT_DAY', 1)
                
                if now.day == report_day and now.hour == hour and now.minute == minute:
                    with self.app.app_context():
                        logger.info("Executing monthly report job (simple scheduler)")
                        # monthly_report_job.delay()  # Commented out - Celery dependency
                        monthly_report_job()  # Direct execution
                    
                    # Sleep for 60 seconds to avoid running multiple times
                    time_module.sleep(60)
                
                time_module.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in monthly report loop: {str(e)}")
                time_module.sleep(300)
    
    def _cleanup_loop(self):
        """Loop for cleanup job"""
        while self.running:
            try:
                now = datetime.now()
                
                if now.hour == 2 and now.minute == 0:
                    with self.app.app_context():
                        logger.info("Executing cleanup job (simple scheduler)")
                        # cleanup_expired_files_job.delay()  # Commented out - Celery dependency
                        cleanup_expired_files_job()  # Direct execution
                    
                    # Sleep for 60 seconds to avoid running multiple times
                    time_module.sleep(60)
                
                time_module.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")
                time_module.sleep(300)

# Legacy Redis scheduler code (commented out)
"""
from apscheduler.jobstores.redis import RedisJobStore
# ... all Redis-related scheduler code commented out ...
""" 