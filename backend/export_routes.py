from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, ExportJob, UserActivity
from background_jobs import export_user_csv_job
from datetime import datetime, timedelta
import os
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
export_bp = Blueprint('export', __name__, url_prefix='/api/export')

@export_bp.route('/csv/request', methods=['POST'])
@jwt_required()
def request_csv_export():
    """
    Request CSV export of user's parking history
    
    This endpoint creates a sync job to generate CSV export
    """
    try:
        user_id = get_jwt_identity()
        user_id = str(user_id)  # Convert to string for MongoDB
        user = User.objects(id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has a pending export job - MongoDB query
        pending_job = ExportJob.objects(
            user_id=user_id,
            status='pending'
        ).first()
        
        if pending_job:
            return jsonify({
                'error': 'You already have a pending export request',
                'job_id': pending_job.job_id,
                'status': pending_job.status
            }), 400
        
        # Create new export job
        export_job = ExportJob(user_id=user_id)
        export_job.save()
        
        # Queue the background job (now synchronous)
        try:
            # task = export_user_csv_job.delay(user_id, export_job.job_id)  # Commented out - Celery
            result = export_user_csv_job(user_id, export_job.job_id)  # Direct execution
            logger.info(f"CSV export job completed for user {user_id}, job_id: {export_job.job_id}")
        except Exception as e:
            # If job fails, update job status
            export_job.status = 'failed'
            export_job.error_message = f"Failed to process job: {str(e)}"
            export_job.save()
            
            return jsonify({
                'error': 'Failed to process export job',
                'details': str(e)
            }), 500
        
        # Log activity
        activity = UserActivity(
            user_id=user_id,
            activity_type='csv_export_requested',
            activity_data=json.dumps({
                'job_id': export_job.job_id
            })
        )
        activity.save()
        
        return jsonify({
            'message': 'CSV export completed successfully',
            'job_id': export_job.job_id,
            'status': 'completed',  # Since it's synchronous now
            'estimated_completion': 'completed'
        }), 200
        
    except Exception as e:
        logger.error(f"Error requesting CSV export: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@export_bp.route('/csv/status/<job_id>', methods=['GET'])
@jwt_required()
def get_export_status(job_id):
    """
    Get status of CSV export job
    
    Args:
        job_id (str): Job ID to check status for
    """
    try:
        user_id = get_jwt_identity()
        user_id = str(user_id)  # Convert to string for MongoDB
        
        # Find the export job - MongoDB query
        export_job = ExportJob.objects(
            job_id=job_id,
            user_id=user_id
        ).first()
        
        if not export_job:
            return jsonify({'error': 'Export job not found'}), 404
        
        response_data = {
            'job_id': export_job.job_id,
            'status': export_job.status,
            'created_at': export_job.created_at.isoformat(),
            'completed_at': export_job.completed_at.isoformat() if export_job.completed_at else None,
            'expires_at': export_job.expires_at.isoformat() if export_job.expires_at else None
        }
        
        if export_job.status == 'completed':
            response_data['download_url'] = export_job.download_url
        elif export_job.status == 'failed':
            response_data['error_message'] = export_job.error_message
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error getting export status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@export_bp.route('/download/<job_id>', methods=['GET'])
@jwt_required()
def download_csv_export(job_id):
    """
    Download CSV export file
    
    Args:
        job_id (str): Job ID to download file for
    """
    try:
        user_id = get_jwt_identity()
        user_id = str(user_id)  # Convert to string for MongoDB
        
        # Find the export job - MongoDB query
        export_job = ExportJob.objects(
            job_id=job_id,
            user_id=user_id
        ).first()
        
        if not export_job:
            return jsonify({'error': 'Export job not found'}), 404
        
        if export_job.status != 'completed':
            return jsonify({
                'error': 'Export not completed',
                'status': export_job.status
            }), 400
        
        # Check if file has expired
        if export_job.expires_at and export_job.expires_at < datetime.utcnow():
            return jsonify({'error': 'Download link has expired'}), 410
        
        # Check if file exists
        if not export_job.file_path or not os.path.exists(export_job.file_path):
            return jsonify({'error': 'Export file not found'}), 404
        
        # Log download activity
        activity = UserActivity(
            user_id=user_id,
            activity_type='csv_export_downloaded',
            activity_data=json.dumps({
                'job_id': export_job.job_id,
                'filename': os.path.basename(export_job.file_path)
            })
        )
        activity.save()
        
        # Send file
        return send_file(
            export_job.file_path,
            as_attachment=True,
            download_name=os.path.basename(export_job.file_path),
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Error downloading CSV export: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@export_bp.route('/csv/history', methods=['GET'])
@jwt_required()
def get_export_history():
    """
    Get user's export job history
    """
    try:
        user_id = get_jwt_identity()
        user_id = str(user_id)  # Convert to string for MongoDB
        
        # Get user's export jobs (last 10) - MongoDB query
        export_jobs = ExportJob.objects(user_id=user_id).order_by('-created_at').limit(10)
        
        jobs_data = []
        for job in export_jobs:
            job_data = job.to_dict()
            
            # Add additional info
            if job.status == 'completed' and job.expires_at:
                job_data['is_expired'] = job.expires_at < datetime.utcnow()
            
            jobs_data.append(job_data)
        
        return jsonify({
            'export_jobs': jobs_data,
            'total_count': len(jobs_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting export history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@export_bp.route('/csv/cancel/<job_id>', methods=['POST'])
@jwt_required()
def cancel_export_job(job_id):
    """
    Cancel a pending export job
    
    Args:
        job_id (str): Job ID to cancel
    """
    try:
        user_id = get_jwt_identity()
        user_id = str(user_id)  # Convert to string for MongoDB
        
        # Find the export job - MongoDB query
        export_job = ExportJob.objects(
            job_id=job_id,
            user_id=user_id
        ).first()
        
        if not export_job:
            return jsonify({'error': 'Export job not found'}), 404
        
        if export_job.status not in ['pending', 'processing']:
            return jsonify({
                'error': 'Cannot cancel job',
                'reason': f'Job is already {export_job.status}'
            }), 400
        
        # Update job status
        export_job.status = 'cancelled'
        export_job.completed_at = datetime.utcnow()
        export_job.error_message = 'Cancelled by user'
        
        export_job.save()
        
        # Log activity
        activity = UserActivity(
            user_id=user_id,
            activity_type='csv_export_cancelled',
            activity_data=json.dumps({
                'job_id': export_job.job_id
            })
        )
        activity.save()
        
        return jsonify({
            'message': 'Export job cancelled successfully',
            'job_id': export_job.job_id,
            'status': export_job.status
        }), 200
        
    except Exception as e:
        logger.error(f"Error cancelling export job: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Admin routes for managing export jobs
@export_bp.route('/admin/jobs', methods=['GET'])
@jwt_required()
def admin_get_all_export_jobs():
    """
    Admin endpoint to get all export jobs
    """
    try:
        user_id = get_jwt_identity()
        user_id = str(user_id)  # Convert to string for MongoDB
        user = User.objects(id=user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status_filter = request.args.get('status')
        
        # Build MongoDB query
        query_filter = {}
        if status_filter:
            query_filter['status'] = status_filter
        
        # MongoDB pagination
        skip = (page - 1) * per_page
        export_jobs = ExportJob.objects(**query_filter).order_by('-created_at').skip(skip).limit(per_page)
        total_count = ExportJob.objects(**query_filter).count()
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        jobs_data = []
        for job in export_jobs:
            job_data = job.to_dict()
            # Get username
            job_user = User.objects(id=job.user_id).first()
            job_data['username'] = job_user.username if job_user else 'Unknown'
            jobs_data.append(job_data)
        
        return jsonify({
            'export_jobs': jobs_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting admin export jobs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@export_bp.route('/admin/cleanup', methods=['POST'])
@jwt_required()
def admin_cleanup_expired_exports():
    """
    Admin endpoint to manually trigger cleanup of expired exports
    """
    try:
        user_id = get_jwt_identity()
        user_id = str(user_id)  # Convert to string for MongoDB
        user = User.objects(id=user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Find expired jobs - MongoDB query
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
                
                # Update job record
                job.file_path = None
                job.download_url = None
                job.save()
                cleaned_count += 1
                
            except Exception as e:
                logger.error(f"Failed to clean up file for job {job.job_id}: {str(e)}")
        
        return jsonify({
            'message': 'Cleanup completed',
            'cleaned_count': cleaned_count,
            'total_expired': len(expired_jobs)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in admin cleanup: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 