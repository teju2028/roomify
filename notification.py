import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SendMail:
    def __init__(self, recipients, subject, body, sender=None):
        """Initialize email notification object"""
        self.recipients = recipients if isinstance(recipients, list) else [recipients]
        self.subject = subject
        self.body = body
        self.sender = sender or config.EMAIL_FROM
        
    def send(self, password=None):
        """Send email notification"""
        password = password or config.EMAIL_PASSWORD
        
        if not password:
            logger.error("Email password not provided")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = ", ".join(self.recipients)
            msg['Subject'] = self.subject
            
            # Add body
            msg.attach(MIMEText(self.body, 'html'))
            
            # Connect to server and send
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender, password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {self.recipients}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

def send_roommate_request_notification(sender_username, receiver_email, receiver_name, sender_note):
    """Send notification when a roommate request is received"""
    subject = "New Roommate Request"
    
    body = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #4682b4; padding: 20px; color: white; text-align: center;">
                <h1>Roommate Finder</h1>
            </div>
            <div style="padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd;">
                <h2>Hello {receiver_name},</h2>
                <p>You have received a new roommate request from <b>{sender_username}</b>.</p>
                <p><b>Note from {sender_username}:</b></p>
                <p style="margin-left: 20px; font-style: italic;">"{sender_note}"</p>
                <p>Please log in to your Roommate Finder account to view the request and take action.</p>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{config.APP_URL}" style="background-color: #4682b4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Check Request
                    </a>
                </div>
            </div>
            <div style="padding: 10px; background-color: #f1f1f1; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    notification = SendMail(receiver_email, subject, body)
    return notification.send()

def send_request_status_notification(request_status, sender_email, sender_name, receiver_username, receiver_note):
    """Send notification when a roommate request status changes"""
    status_text = "approved" if request_status == "approved" else "declined"
    
    subject = f"Roommate Request {status_text.capitalize()}"
    
    body = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #4682b4; padding: 20px; color: white; text-align: center;">
                <h1>Roommate Finder</h1>
            </div>
            <div style="padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd;">
                <h2>Hello {sender_name},</h2>
                <p>Your roommate request to <b>{receiver_username}</b> has been <b>{status_text}</b>.</p>
                
                {"<p>Congratulations! You can now contact your new roommate to discuss further arrangements.</p>" 
                if request_status == "approved" else 
                "<p>Don't worry, there are other potential roommates available. You can find more matches in your dashboard.</p>"}
                
                <p><b>Note from {receiver_username}:</b></p>
                <p style="margin-left: 20px; font-style: italic;">"{receiver_note}"</p>

                <div style="text-align: center; margin-top: 30px;">
                    <a href="{config.APP_URL}" style="background-color: #4682b4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Go to Dashboard
                    </a>
                </div>
            </div>
            <div style="padding: 10px; background-color: #f1f1f1; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    notification = SendMail(sender_email, subject, body)
    return notification.send()
