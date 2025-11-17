"""
REST API routes for Email Data Generation application.
"""
from flask import Blueprint, request, jsonify
from backend.config import (
    load_config, save_config, get_smtp_config, get_email_client_config,
    get_email_generation_config, update_smtp_config, update_email_client_config,
    update_email_generation_config, get_history, get_all_email_client_configs,
    save_email_client_config, delete_email_client_config, set_current_email_client,
    get_current_email_client_name
)
from backend.email_generator import EmailGenerator
import logging

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)
email_generator = EmailGenerator()


@api.route('/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    try:
        config = load_config()
        # Don't return passwords in response
        safe_config = config.copy()
        if 'smtp' in safe_config and 'password' in safe_config['smtp']:
            safe_config['smtp']['password'] = '***' if safe_config['smtp']['password'] else ''
        if 'email_client' in safe_config and 'password' in safe_config['email_client']:
            safe_config['email_client']['password'] = '***' if safe_config['email_client']['password'] else ''
        return jsonify(safe_config)
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/config', methods=['POST'])
def update_config():
    """Update configuration."""
    try:
        data = request.json
        config = load_config()
        
        if 'smtp' in data:
            config['smtp'].update(data['smtp'])
        if 'email_client' in data:
            config['email_client'].update(data['email_client'])
        if 'email_generation' in data:
            config['email_generation'].update(data['email_generation'])
        
        save_config(config)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/email/config', methods=['GET'])
def get_email_client_config_route():
    """Get email client configuration.
    
    Query parameters:
        name: Optional config name. If not provided, returns current active config.
    """
    try:
        config_name = request.args.get('name', None)
        config = get_email_client_config(config_name)
        # Don't return password
        safe_config = config.copy()
        if 'password' in safe_config:
            safe_config['password'] = '***' if safe_config['password'] else ''
        return jsonify(safe_config)
    except Exception as e:
        logger.error(f"Error getting email client config: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/email/config', methods=['POST'])
def update_email_client_config_route():
    """Update email client configuration.
    
    Request body must include:
        config_name: Name/ID for this configuration
        ... (other email client config fields)
    """
    try:
        data = request.json
        config_name = data.get('config_name')
        
        if not config_name:
            return jsonify({"error": "config_name is required"}), 400
        
        # Remove config_name from data before saving
        config_data = {k: v for k, v in data.items() if k != 'config_name'}
        
        save_email_client_config(config_name, config_data)
        return jsonify({"success": True, "config_name": config_name})
    except Exception as e:
        logger.error(f"Error updating email client config: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/email/configs', methods=['GET'])
def get_all_email_client_configs_route():
    """Get all email client configurations (names and metadata, no passwords)."""
    try:
        configs = get_all_email_client_configs()
        current = get_current_email_client_name()
        return jsonify({
            "configs": configs,
            "current": current
        })
    except Exception as e:
        logger.error(f"Error getting all email client configs: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/email/config/<config_name>', methods=['DELETE'])
def delete_email_client_config_route(config_name):
    """Delete an email client configuration."""
    try:
        success = delete_email_client_config(config_name)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Configuration not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting email client config: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/email/config/current', methods=['GET'])
def get_current_email_client_route():
    """Get the name of the current active email client configuration."""
    try:
        current = get_current_email_client_name()
        return jsonify({"current": current})
    except Exception as e:
        logger.error(f"Error getting current email client: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/email/config/current', methods=['POST'])
def set_current_email_client_route():
    """Set the current active email client configuration.
    
    Request body:
        {"name": "<config_name>"}
    """
    try:
        data = request.json
        config_name = data.get('name')
        
        if not config_name:
            return jsonify({"error": "name is required"}), 400
        
        success = set_current_email_client(config_name)
        if success:
            return jsonify({"success": True, "current": config_name})
        else:
            return jsonify({"error": "Configuration not found"}), 404
    except Exception as e:
        logger.error(f"Error setting current email client: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/send/phishing', methods=['POST'])
def send_phishing():
    """Send phishing test emails."""
    try:
        data = request.json
        count = data.get('count', 1)
        recipients = data.get('recipients', [])
        template_type = data.get('template_type', 'warning')
        
        if not recipients:
            return jsonify({"error": "No recipients specified"}), 400
        
        result = email_generator.send_phishing_emails(count, recipients, template_type)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error sending phishing emails: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/send/eicar', methods=['POST'])
def send_eicar():
    """Send EICAR test emails."""
    try:
        data = request.json
        count = data.get('count', 1)
        recipients = data.get('recipients', [])
        
        if not recipients:
            return jsonify({"error": "No recipients specified"}), 400
        
        result = email_generator.send_eicar_emails(count, recipients)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error sending EICAR emails: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/send/cynic', methods=['POST'])
def send_cynic():
    """Send Cynic test emails."""
    try:
        data = request.json
        count = data.get('count', 1)
        recipients = data.get('recipients', [])
        
        if not recipients:
            return jsonify({"error": "No recipients specified"}), 400
        
        result = email_generator.send_cynic_emails(count, recipients)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error sending Cynic emails: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/send/gtube', methods=['POST'])
def send_gtube():
    """Send GTUBE spam-test emails."""
    try:
        data = request.json
        count = data.get('count', 1)
        recipients = data.get('recipients', [])
        
        if not recipients:
            return jsonify({"error": "No recipients specified"}), 400
        
        result = email_generator.send_gtube_emails(count, recipients)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error sending GTUBE emails: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/send/custom', methods=['POST'])
def send_custom():
    """Send custom emails with configurable fields."""
    try:
        data = request.json
        count = data.get('count', 1)
        recipients = data.get('recipients', [])
        subject = data.get('subject')
        body = data.get('body')
        display_name = data.get('display_name')
        attachment_type = data.get('attachment_type')
        
        if not recipients:
            return jsonify({"error": "No recipients specified"}), 400
        
        if not subject:
            return jsonify({"error": "Subject is required"}), 400
        
        if not body:
            return jsonify({"error": "Body is required"}), 400
        
        # Validate attachment_type if provided
        if attachment_type and attachment_type not in ['.zip', '.com', '.scr', '.pdf', '.bat']:
            return jsonify({"error": "Invalid attachment_type. Must be one of: .zip, .com, .scr, .pdf, .bat"}), 400
        
        result = email_generator.send_custom_emails(
            count=count,
            recipients=recipients,
            subject=subject,
            body=body,
            display_name=display_name,
            attachment_type=attachment_type
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error sending custom emails: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/test/email', methods=['POST'])
def test_email_config():
    """Test email service configuration by sending a test email."""
    try:
        from backend.smtp_client import SMTPClient
        from datetime import datetime
        
        data = request.json
        recipient = data.get('recipient')
        email_client_config = data.get('email_client_config')
        
        if not recipient:
            return jsonify({"error": "No recipient specified"}), 400
        
        if not email_client_config:
            email_client_config = get_email_client_config()
        
        # Build SMTP config from email client config
        # For most email providers, SMTP uses the same credentials but different server
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
        
        connection_info = {
            "smtp_server": smtp_config["server"],
            "smtp_port": smtp_config["port"],
            "username": smtp_config["username"],
            "use_tls": smtp_config["use_tls"],
            "use_ssl": smtp_config["use_ssl"],
            "recipient": recipient,
            "imap_server": email_client_config.get("imap_server", ""),
            "imap_port": email_client_config.get("imap_port", 993),
            "imap_use_ssl": email_client_config.get("use_ssl", True),
            "imap_use_starttls": email_client_config.get("use_starttls", False)
        }
        
        # Test connection and send email
        test_subject = f"Email Data Generation - Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        test_body = f"""This is a test email from the Email Data Generation application.

If you received this email, your email service configuration is working correctly.

Test Details:
- Sent at: {datetime.now().isoformat()}
- From: {smtp_config.get('username', 'N/A')}
- To: {recipient}
- SMTP Server: {smtp_config['server']}:{smtp_config['port']}

Please confirm receipt of this email."""
        
        # Build connection attempt details
        connection_attempt = {
            "attempted_server": f"{smtp_config['server']}:{smtp_config['port']}",
            "attempted_username": smtp_config.get("username", ""),
            "attempted_encryption": "SSL" if smtp_config.get("use_ssl") else ("TLS" if smtp_config.get("use_tls") else "None"),
            "connection_method": "SMTP_SSL" if smtp_config.get("use_ssl") else "SMTP with STARTTLS" if smtp_config.get("use_tls") else "SMTP (no encryption)"
        }
        
        try:
            smtp_client = SMTPClient(smtp_config)
            with smtp_client as smtp:
                if not smtp.connected:
                    error_msg = smtp.last_error or "Failed to establish connection to SMTP server"
                    error_details = f"""Connection Attempt Failed:
Server: {connection_attempt['attempted_server']}
Username: {connection_attempt['attempted_username'] or 'N/A'}
Encryption: {connection_attempt['attempted_encryption']}
Method: {connection_attempt['connection_method']}

Error: {error_msg}

Possible Causes:
- Incorrect server address or port
- Network connectivity issues
- Firewall blocking the connection
- SSL/TLS configuration mismatch
- Authentication credentials are invalid
- Server is down or unreachable"""
                    
                    return jsonify({
                        "success": False,
                        "error": error_msg,
                        "connection_info": connection_info,
                        "connection_attempt": connection_attempt,
                        "error_details": error_details
                    }), 500
                
                # Send test email
                success = smtp.send_email(
                    to_addresses=recipient,
                    subject=test_subject,
                    body=test_body,
                    from_address=smtp_config.get("username")
                )
                
                if success:
                    return jsonify({
                        "success": True,
                        "message": "Test email sent successfully",
                        "connection_info": connection_info,
                        "subject": test_subject
                    })
                else:
                    error_details = f"""Connection Established But Send Failed:
Server: {connection_attempt['attempted_server']}
Username: {connection_attempt['attempted_username'] or 'N/A'}
Encryption: {connection_attempt['attempted_encryption']}
Method: {connection_attempt['connection_method']}

Error: Successfully connected to SMTP server but failed to send email. This could be due to:
- Authentication failure
- Invalid recipient address
- Server rejecting the email
- Quota or rate limiting"""
                    
                    return jsonify({
                        "success": False,
                        "error": "Failed to send test email",
                        "connection_info": connection_info,
                        "connection_attempt": connection_attempt,
                        "error_details": error_details
                    }), 500
                    
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
            
            logger.error(f"Error testing email config: {e}")
            return jsonify({
                "success": False,
                "error": error_msg,
                "connection_info": connection_info,
                "connection_attempt": connection_attempt,
                "error_details": error_details
            }), 500
            
    except Exception as e:
        logger.error(f"Error in test email endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@api.route('/history', methods=['GET'])
def get_history_route():
    """Get email sending history."""
    try:
        history = get_history()
        return jsonify({"history": history})
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({"error": str(e)}), 500

