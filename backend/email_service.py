from flask import current_app, render_template_string
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import logging
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mail = Mail()

class EmailService:
    """Service class for handling email operations"""
    
    @staticmethod
    def send_daily_reminder(user, parking_lots_count=0):
        """Send daily reminder email to inactive users"""
        try:
            subject = "🚗 Don't Forget to Book Your Parking Spot!"
            
            # Email template
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #007bff; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f8f9fa; }
                    .button { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚗 Vehicle Parking App</h1>
                    </div>
                    <div class="content">
                        <h2>Hi {{ username }}!</h2>
                        <p>We noticed you haven't booked a parking spot recently. Don't miss out on securing your parking!</p>
                        
                        {% if parking_lots_count > 0 %}
                        <p>We currently have <strong>{{ parking_lots_count }}</strong> parking locations available for booking.</p>
                        <p>Book now to ensure you have a guaranteed parking spot when you need it!</p>
                        {% else %}
                        <p>Our admin team is working on adding new parking locations. Check back soon!</p>
                        {% endif %}
                        
                        <a href="http://localhost:3000/user/booking" class="button">Book Parking Spot</a>
                        
                        <p>Benefits of booking with us:</p>
                        <ul>
                            <li>✅ Guaranteed parking spots</li>
                            <li>✅ Competitive pricing</li>
                            <li>✅ Prime locations</li>
                            <li>✅ Easy online booking</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p>This is an automated reminder. If you don't want to receive these emails, please contact support.</p>
                        <p>© 2024 Vehicle Parking App. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_content = render_template_string(template, 
                                                username=user.username,
                                                parking_lots_count=parking_lots_count)
            
            msg = Message(
                subject=subject,
                recipients=[user.email] if user.email else [],
                html=html_content
            )
            
            if user.email:
                mail.send(msg)
                logger.info(f"Daily reminder sent to {user.email}")
                return True
            else:
                logger.warning(f"No email address for user {user.username}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send daily reminder to {user.username}: {str(e)}")
            return False
    
    @staticmethod
    def send_monthly_report(user, report_data):
        """Send monthly activity report to user"""
        try:
            subject = f"📊 Your Monthly Parking Report - {report_data['month_year']}"
            
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #28a745; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f8f9fa; }
                    .stat-box { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #28a745; }
                    .stat-number { font-size: 24px; font-weight: bold; color: #28a745; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                    table { width: 100%; border-collapse: collapse; margin: 15px 0; }
                    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Monthly Parking Report</h1>
                        <p>{{ month_year }}</p>
                    </div>
                    <div class="content">
                        <h2>Hi {{ username }}!</h2>
                        <p>Here's your parking activity summary for {{ month_year }}:</p>
                        
                        <div class="stat-box">
                            <div class="stat-number">{{ total_bookings }}</div>
                            <div>Total Parking Spots Booked</div>
                        </div>
                        
                        <div class="stat-box">
                            <div class="stat-number">${{ total_spent }}</div>
                            <div>Total Amount Spent</div>
                        </div>
                        
                        {% if most_used_lot %}
                        <div class="stat-box">
                            <div class="stat-number">{{ most_used_lot }}</div>
                            <div>Most Used Parking Lot</div>
                        </div>
                        {% endif %}
                        
                        <div class="stat-box">
                            <div class="stat-number">{{ total_hours }}</div>
                            <div>Total Hours Parked</div>
                        </div>
                        
                        {% if recent_bookings %}
                        <h3>Recent Bookings</h3>
                        <table>
                            <tr>
                                <th>Date</th>
                                <th>Location</th>
                                <th>Spot</th>
                                <th>Cost</th>
                            </tr>
                            {% for booking in recent_bookings %}
                            <tr>
                                <td>{{ booking.date }}</td>
                                <td>{{ booking.location }}</td>
                                <td>{{ booking.spot }}</td>
                                <td>${{ booking.cost }}</td>
                            </tr>
                            {% endfor %}
                        </table>
                        {% endif %}
                        
                        <p>Thank you for using our parking service! 🚗</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Vehicle Parking App. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_content = render_template_string(template, 
                                                username=user.username,
                                                **report_data)
            
            msg = Message(
                subject=subject,
                recipients=[user.email] if user.email else [],
                html=html_content
            )
            
            if user.email:
                mail.send(msg)
                logger.info(f"Monthly report sent to {user.email}")
                return True
            else:
                logger.warning(f"No email address for user {user.username}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send monthly report to {user.username}: {str(e)}")
            return False
    
    @staticmethod
    def send_csv_export_notification(user, job):
        """Send notification when CSV export is ready"""
        try:
            if job.status == 'completed':
                subject = "✅ Your Parking History Export is Ready!"
                message = f"""
                Hi {user.username}!
                
                Your parking history CSV export has been generated successfully.
                
                Download Link: {job.download_url}
                
                Note: This link will expire in 24 hours for security reasons.
                
                Best regards,
                Vehicle Parking App Team
                """
            else:
                subject = "❌ CSV Export Failed"
                message = f"""
                Hi {user.username}!
                
                Unfortunately, your parking history CSV export failed to generate.
                
                Error: {job.error_message}
                
                Please try again or contact support if the issue persists.
                
                Best regards,
                Vehicle Parking App Team
                """
            
            msg = Message(
                subject=subject,
                recipients=[user.email] if user.email else [],
                body=message
            )
            
            if user.email:
                mail.send(msg)
                logger.info(f"CSV export notification sent to {user.email}")
                return True
            else:
                logger.warning(f"No email address for user {user.username}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send CSV notification to {user.username}: {str(e)}")
            return False

class NotificationService:
    """Service for sending notifications via various channels"""
    
    @staticmethod
    def send_google_chat_notification(message, webhook_url=None):
        """Send notification to Google Chat via webhook"""
        try:
            webhook_url = webhook_url or current_app.config.get('GOOGLE_CHAT_WEBHOOK_URL')
            if not webhook_url:
                logger.warning("Google Chat webhook URL not configured")
                return False
            
            payload = {
                "text": message
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Google Chat notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Google Chat notification: {str(e)}")
            return False
    
    @staticmethod
    def send_sms_notification(phone_number, message):
        """Send SMS notification (example using Twilio)"""
        try:
            # This is a placeholder for SMS integration
            # You would need to implement actual SMS service integration
            logger.info(f"SMS notification would be sent to {phone_number}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {str(e)}")
            return False 