"""
IMAP email client for reading emails from web-based email accounts.
"""
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import logging
from backend.config import get_email_client_config

logger = logging.getLogger(__name__)


class EmailClient:
    """IMAP client for reading emails."""
    
    def __init__(self, email_client_config=None):
        """Initialize email client with configuration."""
        if email_client_config is None:
            email_client_config = get_email_client_config()
        self.email_client_config = email_client_config
        self.imap = None
        self.connected = False
    
    def connect(self):
        """Connect to IMAP server."""
        try:
            imap_server = self.email_client_config.get("imap_server", "")
            imap_port = self.email_client_config.get("imap_port", 993)
            use_ssl = self.email_client_config.get("use_ssl", True)
            use_starttls = self.email_client_config.get("use_starttls", False)
            
            if not imap_server:
                raise ValueError("IMAP server not configured")
            
            if use_ssl:
                self.imap = imaplib.IMAP4_SSL(imap_server, imap_port)
            else:
                self.imap = imaplib.IMAP4(imap_server, imap_port)
                if use_starttls:
                    self.imap.starttls()
            
            username = self.email_client_config.get("username", "")
            password = self.email_client_config.get("password", "")
            
            if username and password:
                self.imap.login(username, password)
            
            self.connected = True
            logger.info(f"Connected to IMAP server {imap_server}:{imap_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from IMAP server."""
        if self.imap and self.connected:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass
            self.connected = False
    
    def list_folders(self):
        """List all available folders."""
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            status, folders = self.imap.list()
            if status == 'OK':
                folder_list = []
                for folder in folders:
                    # Parse folder name from IMAP response
                    folder_str = folder.decode()
                    # Extract folder name (format: '(\HasNoChildren) "/" "INBOX"')
                    parts = folder_str.split('"')
                    if len(parts) >= 3:
                        folder_name = parts[-2]
                        folder_list.append(folder_name)
                return folder_list
            return []
        except Exception as e:
            logger.error(f"Failed to list folders: {e}")
            return []
    
    def get_messages(self, folder='INBOX', limit=50):
        """
        Get messages from a folder.
        
        Args:
            folder: Folder name (default: 'INBOX')
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of message dictionaries with headers and metadata
        """
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            # Select folder
            status, messages = self.imap.select(folder)
            if status != 'OK':
                logger.error(f"Failed to select folder {folder}")
                return []
            
            # Search for all messages
            status, message_ids = self.imap.search(None, 'ALL')
            if status != 'OK':
                logger.error("Failed to search messages")
                return []
            
            message_id_list = message_ids[0].split()
            # Reverse to get newest first, then limit
            message_id_list = message_id_list[-limit:] if len(message_id_list) > limit else message_id_list
            message_id_list.reverse()
            
            messages_data = []
            for msg_id in message_id_list:
                try:
                    status, msg_data = self.imap.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        msg = email.message_from_bytes(msg_data[0][1])
                        message_info = self._parse_message(msg, msg_id.decode())
                        messages_data.append(message_info)
                except Exception as e:
                    logger.error(f"Error parsing message {msg_id}: {e}")
                    continue
            
            return messages_data
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []
    
    def get_message(self, folder, msg_id):
        """
        Get a specific message by ID.
        
        Args:
            folder: Folder name
            msg_id: Message ID
        
        Returns:
            Dictionary with full message data including body and attachments
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            status, _ = self.imap.select(folder)
            if status != 'OK':
                return None
            
            status, msg_data = self.imap.fetch(msg_id.encode(), '(RFC822)')
            if status == 'OK':
                msg = email.message_from_bytes(msg_data[0][1])
                return self._parse_message_full(msg, msg_id)
            return None
        except Exception as e:
            logger.error(f"Failed to get message {msg_id}: {e}")
            return None
    
    def _parse_message(self, msg, msg_id):
        """Parse message headers and basic info."""
        subject = self._decode_header(msg.get('Subject', ''))
        from_addr = self._decode_header(msg.get('From', ''))
        to_addr = self._decode_header(msg.get('To', ''))
        date_str = msg.get('Date', '')
        
        try:
            date = parsedate_to_datetime(date_str) if date_str else None
        except:
            date = None
        
        return {
            'id': msg_id,
            'subject': subject,
            'from': from_addr,
            'to': to_addr,
            'date': date.isoformat() if date else None,
            'has_attachments': self._has_attachments(msg)
        }
    
    def _parse_message_full(self, msg, msg_id):
        """Parse full message including body and attachments."""
        info = self._parse_message(msg, msg_id)
        
        # Get body
        body = self._get_body(msg)
        info['body'] = body
        
        # Get attachments
        attachments = self._get_attachments(msg)
        info['attachments'] = attachments
        
        return info
    
    def _decode_header(self, header):
        """Decode email header."""
        if not header:
            return ""
        decoded_parts = decode_header(header)
        decoded_str = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_str += part.decode(encoding or 'utf-8')
                except:
                    decoded_str += part.decode('utf-8', errors='ignore')
            else:
                decoded_str += part
        return decoded_str
    
    def _get_body(self, msg):
        """Extract body from email message."""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
        return body
    
    def _has_attachments(self, msg):
        """Check if message has attachments."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    return True
        return False
    
    def _get_attachments(self, msg):
        """Extract attachment information."""
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_header(filename)
                        attachments.append({
                            'filename': filename,
                            'content_type': part.get_content_type(),
                            'size': len(part.get_payload(decode=True))
                        })
        return attachments
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

