"""
Email generator coordinator.
Orchestrates the generation and sending of different types of test emails.
"""
import logging
from backend.smtp_client import SMTPClient
from backend.generators.phishing import PhishingGenerator
from backend.generators.eicar import EICARGenerator
from backend.generators.cynic import CynicGenerator
from backend.generators.gtube import GTUBEGenerator
from backend.generators.custom import CustomEmailGenerator
from backend.config import add_history_entry, get_smtp_config

logger = logging.getLogger(__name__)


class EmailGenerator:
    """Main email generator coordinator."""
    
    def __init__(self):
        """Initialize email generator."""
        self.phishing_gen = PhishingGenerator()
        self.eicar_gen = EICARGenerator()
        self.cynic_gen = CynicGenerator()
        self.custom_gen = CustomEmailGenerator()
        self.gtube_gen = GTUBEGenerator()
    
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

    def send_gtube_emails(self, count=1, recipients=None):
        """
        Generate and send GTUBE spam-test emails.

        Args:
            count: Number of emails to send
            recipients: List of recipient email addresses

        Returns:
            Dictionary with results
        """
        try:
            emails = self.gtube_gen.generate_emails(count, recipients)
            results = self._send_emails(emails, "gtube")
            return results
        except Exception as e:
            logger.error(f"Failed to send GTUBE emails: {e}")
            return {"success": False, "error": str(e), "sent": 0}
    
    def send_custom_emails(self, count=1, recipients=None, subject=None, body=None,
                           display_name=None, attachment_type=None):
        """
        Generate and send custom emails with configurable fields.

        Args:
            count: Number of emails to send
            recipients: List of recipient email addresses
            subject: Email subject line
            body: Email body text
            display_name: Sender display name (optional)
            attachment_type: Attachment extension (.zip, .com, .scr, .pdf, .bat) or None

        Returns:
            Dictionary with results
        """
        try:
            emails = self.custom_gen.generate_emails(
                count, recipients, subject, body, display_name, attachment_type
            )
            results = self._send_emails(emails, "custom")
            return results
        except Exception as e:
            logger.error(f"Failed to send custom emails: {e}")
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
            elif "office365.com" in imap_server:
                smtp_config["server"] = "smtp.office365.com"
                smtp_config["port"] = 587
            elif "outlook.com" in imap_server or "imap-mail.outlook.com" in imap_server:
                smtp_config["server"] = "smtp-mail.outlook.com"
                smtp_config["port"] = 587
            elif "yahoo.com" in imap_server:
                smtp_config["server"] = "smtp.mail.yahoo.com"
                smtp_config["port"] = 587
            elif "mail.me.com" in imap_server:
                smtp_config["server"] = "smtp.mail.me.com"
                smtp_config["port"] = 587
            elif "zoho.com" in imap_server:
                smtp_config["server"] = "smtp.zoho.com"
                smtp_config["port"] = 587
        
        # Build connection info and connection attempt details
        connection_info = {
            "smtp_server": smtp_config["server"],
            "smtp_port": smtp_config["port"],
            "username": smtp_config["username"],
            "use_tls": smtp_config["use_tls"],
            "use_ssl": smtp_config["use_ssl"],
            "imap_server": email_client_config.get("imap_server", ""),
            "imap_port": email_client_config.get("imap_port", 993),
            "imap_use_ssl": email_client_config.get("use_ssl", True),
            "imap_use_starttls": email_client_config.get("use_starttls", False)
        }
        
        connection_attempt = {
            "attempted_server": f"{smtp_config['server']}:{smtp_config['port']}",
            "attempted_username": smtp_config.get("username", ""),
            "attempted_encryption": "SSL" if smtp_config.get("use_ssl") else ("TLS" if smtp_config.get("use_tls") else "None"),
            "connection_method": "SMTP_SSL" if smtp_config.get("use_ssl") else "SMTP with STARTTLS" if smtp_config.get("use_tls") else "SMTP (no encryption)"
        }
        
        sent_count = 0
        failed_count = 0
        errors = []
        connection_error = None
        # For Cynic emails, track MD5 checksums of the underlying VBS scripts
        cynic_vbs_md5_list = [] if email_type == "cynic" else None
        
        try:
            smtp_client = SMTPClient(smtp_config)
            with smtp_client as smtp:
                if not smtp.connected:
                    connection_error = smtp.last_error or "Failed to establish connection to SMTP server"
                    error_details = f"""Connection Attempt Failed:
Server: {connection_attempt['attempted_server']}
Username: {connection_attempt['attempted_username'] or 'N/A'}
Encryption: {connection_attempt['attempted_encryption']}
Method: {connection_attempt['connection_method']}

Error: {connection_error}

Possible Causes:
- Incorrect server address or port
- Network connectivity issues
- Firewall blocking the connection
- SSL/TLS configuration mismatch
- Authentication credentials are invalid
- Server is down or unreachable"""
                    
                    return {
                        "success": False,
                        "sent": 0,
                        "failed": len(emails),
                        "total": len(emails),
                        "errors": [connection_error],
                        "connection_info": connection_info,
                        "connection_attempt": connection_attempt,
                        "error_details": error_details
                    }
                
                for email_data in emails:
                    try:
                        attachments = email_data.get("attachments", [])
                        display_name = email_data.get("display_name")
                        success = smtp.send_email(
                            to_addresses=email_data["recipients"],
                            subject=email_data["subject"],
                            body=email_data["body"],
                            attachments=attachments if attachments else None,
                            display_name=display_name
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
                            # Capture Cynic VBS MD5 checksums for reporting
                            if cynic_vbs_md5_list is not None:
                                vbs_md5 = email_data.get("vbs_md5")
                                if vbs_md5:
                                    cynic_vbs_md5_list.append(vbs_md5)
                        else:
                            failed_count += 1
                            errors.append(f"Failed to send: {email_data['subject']}")
                    except Exception as e:
                        failed_count += 1
                        error_msg = f"Error sending {email_data.get('subject', 'email')}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
        
        except Exception as e:
            error_msg = str(e)
            error_details = f"""Connection Attempt Failed:
Server: {connection_attempt['attempted_server']}
Username: {connection_attempt['attempted_username'] or 'N/A'}
Encryption: {connection_attempt['attempted_encryption']}
Method: {connection_attempt['connection_method']}

Error Details:
{error_msg}

Possible Causes:
- Incorrect server address, port, or encryption settings
- Authentication credentials are invalid
- Network connectivity issues
- Firewall or security software blocking the connection
- SSL/TLS certificate validation failure
- Server is down or unreachable"""
            
            logger.error(f"Error sending {email_type} emails: {e}")
            return {
                "success": False,
                "sent": sent_count,
                "failed": len(emails) - sent_count,
                "total": len(emails),
                "errors": [error_msg] + errors[:9],
                "connection_info": connection_info,
                "connection_attempt": connection_attempt,
                "error_details": error_details
            }
        
        # Build result with connection info
        result = {
            "success": failed_count == 0,
            "sent": sent_count,
            "failed": failed_count,
            "total": len(emails),
            "errors": errors[:10],  # Limit errors to first 10
            "connection_info": connection_info,
            "connection_attempt": connection_attempt
        }

        # Include Cynic VBS MD5 checksums (if any) in the result payload
        if cynic_vbs_md5_list:
            result["cynic_vbs_md5"] = cynic_vbs_md5_list
        
        # Add success details if all emails sent successfully
        if result["success"]:
            connection_details = f"""Connection Successful:
Server: {connection_attempt['attempted_server']}
Username: {connection_attempt['attempted_username'] or 'N/A'}
Encryption: {connection_attempt['attempted_encryption']}
Method: {connection_attempt['connection_method']}
        
Successfully sent {sent_count} email(s) of type: {email_type}"""

            # Append Cynic VBS MD5 info into the human-readable details so it
            # appears directly in the success notification / modal.
            if cynic_vbs_md5_list:
                md5_lines = "\n".join(f"- {md5}" for md5 in cynic_vbs_md5_list)
                connection_details += f"""

Cynic VBS MD5 checksums:
{md5_lines}"""

            result["connection_details"] = connection_details
        
        return result
    
    def _get_timestamp(self):
        """Get current timestamp as ISO string."""
        from datetime import datetime
        return datetime.now().isoformat()

