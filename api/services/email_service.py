import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from api.core.config import settings


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email via SMTP.
        Returns True if successful, False otherwise.
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            # Log error but don't fail the booking
            print(f"Email send failed: {str(e)}")
            return False
    
    def send_booking_confirmation_to_customer(
        self,
        customer_email: str,
        customer_name: str,
        service_name: str,
        start_time: datetime,
        end_time: datetime,
        tenant_name: str,
        tenant_email: str,
        tenant_phone: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Send booking confirmation email to customer."""
        
        subject = f"Booking Confirmation - {service_name}"
        
        # Format datetime for display
        start_str = start_time.strftime("%A, %B %d, %Y at %I:%M %p")
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        
        # HTML body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; }}
                .detail {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Confirmed!</h1>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>
                    <p>Your booking has been confirmed. Here are the details:</p>
                    
                    <div class="detail">
                        <span class="label">Service:</span> {service_name}
                    </div>
                    <div class="detail">
                        <span class="label">Date & Time:</span> {start_str}
                    </div>
                    <div class="detail">
                        <span class="label">Duration:</span> {duration_minutes} minutes
                    </div>
                    {f'<div class="detail"><span class="label">Notes:</span> {notes}</div>' if notes else ''}
                    
                    <h3>Contact Information</h3>
                    <div class="detail">
                        <span class="label">Business:</span> {tenant_name}
                    </div>
                    <div class="detail">
                        <span class="label">Email:</span> {tenant_email}
                    </div>
                    {f'<div class="detail"><span class="label">Phone:</span> {tenant_phone}</div>' if tenant_phone else ''}
                    
                    <p style="margin-top: 20px;">If you need to cancel or reschedule, please contact us directly.</p>
                </div>
                <div class="footer">
                    <p>This is an automated confirmation email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_body = f"""
Booking Confirmed!

Hi {customer_name},

Your booking has been confirmed. Here are the details:

Service: {service_name}
Date & Time: {start_str}
Duration: {duration_minutes} minutes
{f'Notes: {notes}' if notes else ''}

Contact Information:
Business: {tenant_name}
Email: {tenant_email}
{f'Phone: {tenant_phone}' if tenant_phone else ''}

If you need to cancel or reschedule, please contact us directly.

---
This is an automated confirmation email.
        """
        
        return self._send_email(customer_email, subject, html_body, text_body)
    
    def send_booking_notification_to_business(
        self,
        business_email: str,
        business_name: str,
        customer_name: str,
        customer_email: str,
        customer_phone: Optional[str],
        service_name: str,
        start_time: datetime,
        end_time: datetime,
        notes: Optional[str] = None
    ) -> bool:
        """Send new booking notification to business."""
        
        subject = f"New Booking: {service_name} - {customer_name}"
        
        # Format datetime for display
        start_str = start_time.strftime("%A, %B %d, %Y at %I:%M %p")
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        
        # HTML body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; }}
                .detail {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Booking Received</h1>
                </div>
                <div class="content">
                    <p>Hi {business_name},</p>
                    <p>You have received a new booking:</p>
                    
                    <h3>Booking Details</h3>
                    <div class="detail">
                        <span class="label">Service:</span> {service_name}
                    </div>
                    <div class="detail">
                        <span class="label">Date & Time:</span> {start_str}
                    </div>
                    <div class="detail">
                        <span class="label">Duration:</span> {duration_minutes} minutes
                    </div>
                    {f'<div class="detail"><span class="label">Notes:</span> {notes}</div>' if notes else ''}
                    
                    <h3>Customer Information</h3>
                    <div class="detail">
                        <span class="label">Name:</span> {customer_name}
                    </div>
                    <div class="detail">
                        <span class="label">Email:</span> {customer_email}
                    </div>
                    {f'<div class="detail"><span class="label">Phone:</span> {customer_phone}</div>' if customer_phone else ''}
                    
                    <p style="margin-top: 20px;">A confirmation email has been sent to the customer.</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_body = f"""
New Booking Received

Hi {business_name},

You have received a new booking:

Booking Details:
Service: {service_name}
Date & Time: {start_str}
Duration: {duration_minutes} minutes
{f'Notes: {notes}' if notes else ''}

Customer Information:
Name: {customer_name}
Email: {customer_email}
{f'Phone: {customer_phone}' if customer_phone else ''}

A confirmation email has been sent to the customer.

---
This is an automated notification email.
        """
        
        return self._send_email(business_email, subject, html_body, text_body)


# Singleton instance
email_service = EmailService()
