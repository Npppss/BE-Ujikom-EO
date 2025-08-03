import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL

    def send_email_verification(self, to_email: str, verification_token: str, user_name: str = None):
        """Send email verification email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = "Email Verification - Event Organizer"

            # Create verification URL
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
            
            html_body = f"""
            <html>
            <body>
                <h2>Email Verification</h2>
                <p>Hello {user_name or 'there'},</p>
                <p>Thank you for registering with Event Organizer. Please verify your email address to complete your registration.</p>
                <p>Click the link below to verify your email:</p>
                <p><a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px;">Verify Email</a></p>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p>{verification_url}</p>
                <p>This verification link will expire in 24 hours for security reasons.</p>
                <p>If you didn't create an account with Event Organizer, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Event Organizer Team</p>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email verification sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email verification to {to_email}: {str(e)}")
            return False

    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str = None):
        """Send password reset email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = "Password Reset Request - Event Organizer"

            # Create HTML body
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            html_body = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello {user_name or 'there'},</p>
                <p>You have requested to reset your password for your Event Organizer account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px;">Reset Password</a></p>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p>{reset_url}</p>
                <p>This link will expire in 1 hour for security reasons.</p>
                <p>If you didn't request this password reset, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Event Organizer Team</p>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Password reset email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password reset email to {to_email}: {str(e)}")
            return False

    def send_welcome_email(self, to_email: str, user_name: str = None):
        """Send welcome email to new users"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = "Welcome to Event Organizer!"

            html_body = f"""
            <html>
            <body>
                <h2>Welcome to Event Organizer!</h2>
                <p>Hello {user_name or 'there'},</p>
                <p>Thank you for registering with Event Organizer. Your account has been created successfully!</p>
                <p>You can now log in to your account and start organizing amazing events.</p>
                <br>
                <p>Best regards,<br>Event Organizer Team</p>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Welcome email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send welcome email to {to_email}: {str(e)}")
            return False

email_service = EmailService() 