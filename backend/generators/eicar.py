"""
EICAR test file generator.
Creates EICAR test files for antivirus testing.
"""
import tempfile
from pathlib import Path
import logging
from backend.config import get_email_generation_config

logger = logging.getLogger(__name__)

# EICAR test file content
EICAR_STRING = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


class EICARGenerator:
    """Generate EICAR test emails."""
    
    def __init__(self):
        """Initialize EICAR generator."""
        self.config = get_email_generation_config()
    
    def create_eicar_file(self, output_path=None):
        """
        Create EICAR test file.
        
        Args:
            output_path: Path to save EICAR file (optional, uses temp file if not provided)
        
        Returns:
            Path to created EICAR file
        """
        if output_path is None:
            temp_dir = Path(tempfile.gettempdir())
            output_path = temp_dir / "eicar.com"
        else:
            output_path = Path(output_path)
        
        try:
            with open(output_path, 'w') as f:
                f.write(EICAR_STRING)
            logger.info(f"Created EICAR file: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to create EICAR file: {e}")
            raise
    
    def generate_email_body(self):
        """
        Generate email body for EICAR test email.
        
        Returns:
            Email body text
        """
        return """This email contains an EICAR test file attachment.

The EICAR test file is a standard test file used to verify antivirus software is working correctly. It is not a real virus and is completely safe.

This is a test email generated for security testing purposes."""
    
    def generate_emails(self, count=1, recipients=None):
        """
        Generate EICAR test emails.
        
        Args:
            count: Number of emails to generate
            recipients: List of recipient email addresses
        
        Returns:
            List of email dictionaries with subject, body, recipients, and attachment path
        """
        if not recipients:
            recipients = self.config.get("default_recipients", [])
        
        if not recipients:
            raise ValueError("No recipients specified")
        
        emails = []
        subject_template = self.config.get("subject_templates", {}).get("eicar", "EICAR Test File")
        
        for i in range(count):
            # Create EICAR file for each email
            eicar_file = self.create_eicar_file()
            body = self.generate_email_body()
            subject = f"{subject_template} - {i+1}" if count > 1 else subject_template
            
            emails.append({
                "subject": subject,
                "body": body,
                "recipients": recipients,
                "type": "eicar",
                "attachments": [str(eicar_file)]
            })
        
        return emails

