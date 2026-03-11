"""
SMTP client for sending emails through SMTP servers.
Uses Python smtplib for email sending.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from pathlib import Path
import logging
from backend.config import get_smtp_config

logger = logging.getLogger(__name__)


class SMTPClient:
    """SMTP client for sending emails with attachments."""
    
    def __init__(self, smtp_config=None):
        """Initialize SMTP client with configuration."""
        if smtp_config is None:
            smtp_config = get_smtp_config()
        self.smtp_config = smtp_config
        self.server = None
        self.connected = False
        self.last_error = None
        self.last_connection_attempt = None
    
    def connect(self):
        """Connect to SMTP server."""
        try:
            server = self.smtp_config.get("server", "")
            port = self.smtp_config.get("port", 587)
            use_tls = self.smtp_config.get("use_tls", True)
            use_ssl = self.smtp_config.get("use_ssl", False)
            
            if not server:
                raise ValueError("SMTP server not configured")
            
            # Store connection details for error reporting
            self.last_connection_attempt = {
                "server": server,
                "port": port,
                "use_ssl": use_ssl,
                "use_tls": use_tls
            }
            
            if use_ssl:
                self.server = smtplib.SMTP_SSL(server, port)
            else:
                self.server = smtplib.SMTP(server, port)
                if use_tls:
                    self.server.starttls()
            
            username = self.smtp_config.get("username", "")
            password = self.smtp_config.get("password", "")
            
            if username and password:
                self.server.login(username, password)
            
            self.connected = True
            logger.info(f"Connected to SMTP server {server}:{port}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Authentication failed: {str(e)}"
            logger.error(f"Failed to connect to SMTP server: {error_msg}")
            self.last_error = error_msg
            self.connected = False
            return False
        except smtplib.SMTPConnectError as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.error(f"Failed to connect to SMTP server: {error_msg}")
            self.last_error = error_msg
            self.connected = False
            return False
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"Connection closed unexpectedly: {str(e)}. This often happens when the provider rejects the credentials (e.g., missing app-specific password or legacy IMAP/SMTP access)."
            logger.error(f"Failed to connect to SMTP server: {error_msg}")
            self.last_error = error_msg
            self.connected = False
            return False
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(f"Failed to connect to SMTP server: {error_msg}")
            self.last_error = error_msg
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from SMTP server."""
        if self.server and self.connected:
            try:
                self.server.quit()
            except:
                pass
            self.connected = False
    
    def send_email(self, to_addresses, subject, body, attachments=None, from_address=None, display_name=None, html_body=None, inline_images=None):
        """
        Send an email with optional attachments.
        
        Args:
            to_addresses: List of recipient email addresses or single string
            subject: Email subject
            body: Email body text
            attachments: List of file paths to attach
            from_address: Sender email address (optional)
            display_name: Sender display name (optional)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            # Convert single address to list
            if isinstance(to_addresses, str):
                to_addresses = [to_addresses]
            
            # Decide base message structure
            has_html = html_body is not None
            has_inline = bool(inline_images)

            if has_html or has_inline:
                # multipart/related with multipart/alternative for text+HTML and optional inline resources
                msg = MIMEMultipart("related")
                alternative = MIMEMultipart("alternative")
                # Plain-text part (always include for compatibility)
                alternative.attach(MIMEText(body, "plain"))
                if has_html:
                    alternative.attach(MIMEText(html_body, "html"))
                msg.attach(alternative)
            else:
                # Simple multipart with plain-text body only
                msg = MIMEMultipart()
            
            # Set from address with optional display name
            if from_address:
                email_address = from_address
            elif self.smtp_config.get("username"):
                email_address = self.smtp_config.get("username")
            else:
                email_address = None
            
            if email_address:
                if display_name:
                    # Format: "Display Name <email@example.com>"
                    msg['From'] = f'"{display_name}" <{email_address}>'
                else:
                    msg['From'] = email_address
            
            msg['To'] = ", ".join(to_addresses)
            msg['Subject'] = subject
            
            # If we're not in HTML/inline mode, attach the plain-text body now
            if not (has_html or has_inline):
                msg.attach(MIMEText(body, "plain"))

            # Add inline images if provided (expects list of dicts with keys: cid, data, subtype)
            if has_inline:
                for img in inline_images or []:
                    try:
                        cid = img.get("cid")
                        data = img.get("data")
                        subtype = img.get("subtype", "png")
                        if not cid or data is None:
                            continue
                        image_part = MIMEImage(data, _subtype=subtype)
                        image_part.add_header("Content-ID", f"<{cid}>")
                        image_part.add_header("Content-Disposition", "inline", filename=f"{cid}.{subtype}")
                        msg.attach(image_part)
                    except Exception as e:
                        logger.error(f"Failed to attach inline image {img!r}: {e}")
            
            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    if isinstance(attachment_path, (str, Path)):
                        attachment_path = Path(attachment_path)
                        if attachment_path.exists():
                            with open(attachment_path, 'rb') as f:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(f.read())
                                encoders.encode_base64(part)
                                part.add_header(
                                    'Content-Disposition',
                                    f'attachment; filename= {attachment_path.name}'
                                )
                                msg.attach(part)
            
            # Send email
            text = msg.as_string()
            self.server.sendmail(msg['From'], to_addresses, text)
            logger.info(f"Email sent successfully to {to_addresses}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

