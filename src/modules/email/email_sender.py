"""Email phishing module - SMTP implementation"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def invia_email_phishing(
    destinatario: str, 
    oggetto: str, 
    corpo: str,
    smtp_server: Optional[str] = None,
    smtp_port: Optional[int] = None,
    sender_email: Optional[str] = None,
    sender_password: Optional[str] = None,
    use_html: bool = True
) -> bool:
    """
    Send phishing email via SMTP
    
    Args:
        destinatario: Recipient email address
        oggetto: Email subject
        corpo: Email body (HTML or plain text)
        smtp_server: SMTP server (default from env or localhost)
        smtp_port: SMTP port (default from env or 25)
        sender_email: Sender email (default from env)
        sender_password: Sender password (optional for auth)
        use_html: Send as HTML (default True)
    
    Returns:
        bool: True if sent successfully
    """
    try:
        # Get config from environment or defaults
        smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'localhost')
        smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '25'))
        sender_email = sender_email or os.getenv('SENDER_EMAIL', 'noreply@browphish.local')
        sender_password = sender_password or os.getenv('SENDER_PASSWORD', None)
        
        # Validate
        if not destinatario or '@' not in destinatario:
            logger.error(f"Invalid email: {destinatario}")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = oggetto
        msg['From'] = sender_email
        msg['To'] = destinatario
        
        # Attach body
        mime_type = 'html' if use_html else 'plain'
        part = MIMEText(corpo, mime_type)
        msg.attach(part)
        
        # Send
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            if sender_password and smtp_server != 'localhost':
                server.starttls()
                server.login(sender_email, sender_password)
            server.sendmail(sender_email, destinatario, msg.as_string())
        
        logger.info(f"✅ Email sent to {destinatario}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sending email: {e}")
        return False


