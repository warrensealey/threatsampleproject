"""
Custom email generator.
Creates emails with configurable subject, body, display name, optional attachments,
and (optionally) a QR code generated from a user-specified URL, either inline in
the email body or inside a PDF attachment, or both.
"""
import tempfile
import zipfile
import uuid
from io import BytesIO
from pathlib import Path
import logging

import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

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
            unique_id = uuid.uuid4().hex
            output_path = temp_dir / f"dummy_{unique_id}{extension}"
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

    def _normalise_qr_mode(self, qr_mode: str) -> str:
        """Normalise QR mode for custom emails."""
        mode = (qr_mode or "none").lower()
        if mode not in ("none", "body", "pdf", "both"):
            return "none"
        return mode

    def _generate_qr_png_bytes(self, url: str) -> bytes:
        """Generate QR code PNG bytes for the given URL."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def _build_qr_html_body(self, body: str, cid: str) -> str:
        """
        Wrap the plain-text body into a simple HTML layout and include the QR
        image (referenced by CID) without exposing the raw URL.
        """
        escaped_body = body.replace("\n", "<br>")
        return f"""<html>
  <body>
    <p>{escaped_body}</p>
    <hr>
    <p>A QR code has been generated for this email.</p>
    <p>Scan the QR code below (in a controlled test environment only).</p>
    <p><img src="cid:{cid}" alt="Custom QR Code" style="max-width: 300px; height: auto;"></p>
    <p>The underlying URL is intentionally not shown in clear text.</p>
  </body>
</html>"""

    def _create_qr_pdf(
        self, png_bytes: bytes, title: str = "Custom Email QR Code"
    ) -> Path:
        """Create a simple one-page PDF containing the QR code without exposing the raw URL.

        A random UUID is used to make the filename unique per email so that
        parallel or repeated sends do not overwrite each other's PDF files.
        """
        temp_dir = Path(tempfile.gettempdir())
        unique_id = uuid.uuid4().hex
        pdf_path = temp_dir / f"custom_qr_{unique_id}.pdf"

        try:
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            width, height = letter

            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, height - 72, title)

            # Description text (no raw URL)
            c.setFont("Helvetica", 10)
            text_obj = c.beginText(72, height - 110)
            text_obj.textLine("This PDF contains a QR code generated from a URL.")
            text_obj.textLine("The actual URL is intentionally not shown in clear text.")
            c.drawText(text_obj)

            # QR image
            img_reader = ImageReader(BytesIO(png_bytes))
            qr_size = 250
            x = 72
            y = height - 380
            c.drawImage(
                img_reader,
                x,
                y,
                width=qr_size,
                height=qr_size,
                preserveAspectRatio=True,
                mask="auto",
            )

            c.showPage()
            c.save()
            logger.info(f"Created custom QR PDF: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Failed to create custom QR PDF: {e}")
            raise

    def generate_emails(
        self,
        count=1,
        recipients=None,
        subject=None,
        body=None,
        display_name=None,
        attachment_type=None,
        qr_url=None,
        qr_mode="none",
    ):
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

        mode = self._normalise_qr_mode(qr_mode)
        use_qr = bool(qr_url) and mode != "none"
        
        for i in range(count):
            email_data = {
                "subject": f"{subject} - {i+1}" if count > 1 else subject,
                "body": body,
                "recipients": recipients,
                "type": "custom",
                "display_name": display_name,
                "attachments": [],
            }
            
            # Add attachment if specified
            if attachment_type:
                attachment_file = self.create_dummy_attachment(attachment_type)
                email_data["attachments"] = [str(attachment_file)]

            # Optionally add QR-generated content from a user-provided URL
            if use_qr:
                try:
                    png_bytes = self._generate_qr_png_bytes(qr_url)

                    if mode in ("body", "both"):
                        cid = f"custom-qr-{i}"
                        email_data["html_body"] = self._build_qr_html_body(body, cid)
                        email_data["inline_images"] = [
                            {
                                "cid": cid,
                                "data": png_bytes,
                                "subtype": "png",
                            }
                        ]

                    if mode in ("pdf", "both"):
                        pdf_path = self._create_qr_pdf(png_bytes)
                        email_data.setdefault("attachments", []).append(str(pdf_path))
                except Exception as e:
                    logger.error("Failed to add QR content to custom email", exc_info=True)
                    raise
            
            emails.append(email_data)
        
        return emails

