"""
Custom email generator.
Creates emails with configurable subject, body, display name, and optional attachments.
"""
import tempfile
import zipfile
from pathlib import Path
import logging
from backend.config import get_email_generation_config

logger = logging.getLogger(__name__)


class CustomEmailGenerator:
    """Generate custom emails with configurable fields."""
    
    def __init__(self):
        """Initialize custom email generator."""
        self.config = get_email_generation_config()
    
    def create_dummy_attachment(self, extension, output_path=None):
        """
        Create a harmless dummy file with the specified extension.
        
        Args:
            extension: File extension (.zip, .com, .scr, .pdf, .bat)
            output_path: Path to save file (optional, uses temp file if not provided)
        
        Returns:
            Path to created file
        """
        if output_path is None:
            temp_dir = Path(tempfile.gettempdir())
            output_path = temp_dir / f"dummy{extension}"
        else:
            output_path = Path(output_path)
        
        try:
            extension_lower = extension.lower()
            
            if extension_lower == '.zip':
                # Create a minimal ZIP file
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr('readme.txt', 'This is a harmless test ZIP file.\nCreated for email testing purposes.')
            
            elif extension_lower == '.com':
                # Create a harmless .com file (text file)
                with open(output_path, 'w') as f:
                    f.write('REM This is a harmless test file with .com extension\n')
                    f.write('REM Created for email testing purposes.\n')
                    f.write('ECHO This file is safe and contains no executable code.\n')
            
            elif extension_lower == '.scr':
                # Create a harmless .scr file (text file)
                with open(output_path, 'w') as f:
                    f.write('REM This is a harmless test file with .scr extension\n')
                    f.write('REM Created for email testing purposes.\n')
                    f.write('REM Screen saver files (.scr) are executable, but this is just a text file.\n')
            
            elif extension_lower == '.pdf':
                # Create a minimal valid PDF file
                pdf_content = b'''%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Harmless test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000317 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
410
%%EOF'''
                with open(output_path, 'wb') as f:
                    f.write(pdf_content)
            
            elif extension_lower == '.bat':
                # Create a harmless .bat file
                with open(output_path, 'w') as f:
                    f.write('@echo off\n')
                    f.write('REM This is a harmless test batch file\n')
                    f.write('REM Created for email testing purposes.\n')
                    f.write('echo This file is safe and contains no malicious code.\n')
                    f.write('pause\n')
            
            else:
                # Default: create a simple text file
                with open(output_path, 'w') as f:
                    f.write(f'This is a harmless test file with {extension} extension.\n')
                    f.write('Created for email testing purposes.\n')
            
            logger.info(f"Created dummy attachment: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to create dummy attachment: {e}")
            raise
    
    def generate_emails(self, count=1, recipients=None, subject=None, body=None, 
                       display_name=None, attachment_type=None):
        """
        Generate custom emails with configurable fields.
        
        Args:
            count: Number of emails to generate
            recipients: List of recipient email addresses
            subject: Email subject line
            body: Email body text
            display_name: Sender display name (optional)
            attachment_type: Attachment extension (.zip, .com, .scr, .pdf, .bat) or None
        
        Returns:
            List of email dictionaries with subject, body, recipients, display_name, and attachment path
        """
        if not recipients:
            recipients = self.config.get("default_recipients", [])
        
        if not recipients:
            raise ValueError("No recipients specified")
        
        if not subject:
            raise ValueError("Subject is required")
        
        if not body:
            raise ValueError("Body is required")
        
        emails = []
        
        for i in range(count):
            email_data = {
                "subject": f"{subject} - {i+1}" if count > 1 else subject,
                "body": body,
                "recipients": recipients,
                "type": "custom",
                "display_name": display_name,
                "attachments": []
            }
            
            # Add attachment if specified
            if attachment_type:
                attachment_file = self.create_dummy_attachment(attachment_type)
                email_data["attachments"] = [str(attachment_file)]
            
            emails.append(email_data)
        
        return emails

