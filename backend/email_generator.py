"""
Email generator coordinator.
Orchestrates the generation and sending of different types of test emails.
"""
import logging
from backend.smtp_client import SMTPClient
from backend.generators.phishing import PhishingGenerator
from backend.generators.eicar import EICARGenerator
from backend.generators.cynic import CynicGenerator
from backend.config import add_history_entry, get_smtp_config

logger = logging.getLogger(__name__)


class EmailGenerator:
    """Main email generator coordinator."""
    
    def __init__(self):
        """Initialize email generator."""
        self.phishing_gen = PhishingGenerator()
        self.eicar_gen = EICARGenerator()
        self.cynic_gen = CynicGenerator()
    
    def send_phishing_emails(self, count=1, recipients=None, template_type="warning"):
        """
        Generate and send phishing emails.
        
        Args:
            count: Number of emails to send
            recipients: List of recipient email addresses
            template_type: Type of email template
        
        Returns:
            Dictionary with results
        """
        try:
            emails = self.phishing_gen.generate_emails(count, recipients, template_type)
            results = self._send_emails(emails, "phishing")
            return results
        except Exception as e:
            logger.error(f"Failed to send phishing emails: {e}")
            return {"success": False, "error": str(e), "sent": 0}
    
    def send_eicar_emails(self, count=1, recipients=None):
        """
        Generate and send EICAR test emails.
        
        Args:
            count: Number of emails to send
            recipients: List of recipient email addresses
        
        Returns:
            Dictionary with results
        """
        try:
            emails = self.eicar_gen.generate_emails(count, recipients)
            results = self._send_emails(emails, "eicar")
            return results
        except Exception as e:
            logger.error(f"Failed to send EICAR emails: {e}")
            return {"success": False, "error": str(e), "sent": 0}
    
    def send_cynic_emails(self, count=1, recipients=None):
        """
        Generate and send Cynic test emails.
        
        Args:
            count: Number of emails to send
            recipients: List of recipient email addresses
        
        Returns:
            Dictionary with results
        """
        try:
            emails = self.cynic_gen.generate_emails(count, recipients)
            results = self._send_emails(emails, "cynic")
            return results
        except Exception as e:
            logger.error(f"Failed to send Cynic emails: {e}")
            return {"success": False, "error": str(e), "sent": 0}
    
    def _send_emails(self, emails, email_type):
        """
        Send emails using SMTP client.
        
        Args:
            emails: List of email dictionaries
            email_type: Type of emails being sent
        
        Returns:
            Dictionary with results
        """
        from backend.config import get_email_client_config
        
        # Get SMTP config from email client config (SMTP settings are now stored there)
        email_client_config = get_email_client_config()
        
        # Build SMTP config from email client config
        smtp_config = {
            "server": email_client_config.get("smtp_server", ""),
            "port": email_client_config.get("smtp_port", 587),
            "username": email_client_config.get("username", ""),
            "password": email_client_config.get("password", ""),
            "use_tls": email_client_config.get("smtp_use_tls", True),
            "use_ssl": email_client_config.get("smtp_use_ssl", False)
        }
        
        # If SMTP server not in email_client_config, try to derive from IMAP server
        if not smtp_config["server"]:
            imap_server = email_client_config.get("imap_server", "")
            if "gmx.com" in imap_server:
                smtp_config["server"] = "mail.gmx.com"
                smtp_config["port"] = 587
            elif "gmail.com" in imap_server:
                smtp_config["server"] = "smtp.gmail.com"
                smtp_config["port"] = 587
            elif "aol.com" in imap_server:
                smtp_config["server"] = "smtp.aol.com"
                smtp_config["port"] = 465
                smtp_config["use_ssl"] = True
            elif "office365.com" in imap_server or "outlook.com" in imap_server:
                smtp_config["server"] = "smtp.office365.com"
                smtp_config["port"] = 587
        
        sent_count = 0
        failed_count = 0
        errors = []
        
        with SMTPClient(smtp_config) as smtp:
            for email_data in emails:
                try:
                    attachments = email_data.get("attachments", [])
                    success = smtp.send_email(
                        to_addresses=email_data["recipients"],
                        subject=email_data["subject"],
                        body=email_data["body"],
                        attachments=attachments if attachments else None
                    )
                    
                    if success:
                        sent_count += 1
                        # Add to history
                        add_history_entry({
                            "type": email_type,
                            "subject": email_data["subject"],
                            "recipients": email_data["recipients"],
                            "timestamp": self._get_timestamp(),
                            "status": "sent"
                        })
                    else:
                        failed_count += 1
                        errors.append(f"Failed to send: {email_data['subject']}")
                except Exception as e:
                    failed_count += 1
                    error_msg = f"Error sending {email_data.get('subject', 'email')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
        
        return {
            "success": failed_count == 0,
            "sent": sent_count,
            "failed": failed_count,
            "total": len(emails),
            "errors": errors[:10]  # Limit errors to first 10
        }
    
    def _get_timestamp(self):
        """Get current timestamp as ISO string."""
        from datetime import datetime
        return datetime.now().isoformat()

