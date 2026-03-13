"""
QR-based phishing email generator.
Converts PhishTank URLs into QR codes that can be embedded in the email body
and/or placed into a simple PDF attachment.
"""
import logging
import tempfile
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Any

import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from backend.config import get_email_generation_config
from backend.generators.phishing import PhishingGenerator

logger = logging.getLogger(__name__)


class QRPhishingGenerator:
    """Generate QR-based phishing emails using PhishTank URLs."""

    def __init__(self):
        self.config = get_email_generation_config()
        self.phishing_gen = PhishingGenerator()

    def _normalise_qr_mode(self, qr_mode: str) -> str:
        mode = (qr_mode or "body").lower()
        if mode not in ("body", "pdf", "both"):
            return "body"
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

    def _build_html_body(self, cid: str) -> str:
        """Build a simple HTML body that references the QR image by Content-ID without exposing the raw URL."""
        return f"""<html>
  <body>
    <p>This email contains a QR code that encodes a phishing URL from PhishTank for testing purposes.</p>
    <p>Scan the QR code below (in a controlled test environment only).</p>
    <p><img src="cid:{cid}" alt="Phishing QR Code" style="max-width: 300px; height: auto;"></p>
    <p>The underlying URL is intentionally not shown in clear text.</p>
  </body>
</html>"""

    def _create_qr_pdf(self, png_bytes: bytes) -> Path:
        """Create a simple one-page PDF containing the QR code without exposing the raw URL."""
        temp_dir = Path(tempfile.gettempdir())
        pdf_path = temp_dir / "qr_phishing.pdf"

        try:
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            width, height = letter

            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, height - 72, "QR Phishing Test Email")

            # Description text (no raw URL)
            c.setFont("Helvetica", 10)
            text_obj = c.beginText(72, height - 110)
            text_obj.textLine("This PDF contains a QR code that encodes a phishing URL for testing.")
            text_obj.textLine("The actual URL is intentionally not shown in clear text.")
            c.drawText(text_obj)

            # QR image
            img_reader = ImageReader(BytesIO(png_bytes))
            qr_size = 250
            x = 72
            y = height - 380
            c.drawImage(img_reader, x, y, width=qr_size, height=qr_size, preserveAspectRatio=True, mask="auto")

            c.showPage()
            c.save()
            logger.info(f"Created QR phishing PDF: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Failed to create QR PDF: {e}")
            raise

    def generate_emails(
        self,
        count: int = 1,
        recipients: List[str] = None,
        qr_mode: str = "body",
        template_type: str = "warning",
    ) -> List[Dict[str, Any]]:
        """
        Generate QR phishing emails.

        Args:
            count: Number of emails to generate
            recipients: List of recipient email addresses
            qr_mode: 'body', 'pdf', or 'both'
            template_type: Reserved for future template variants

        Returns:
            List of email dicts with subject, body, html_body/inline_images, attachments, and metadata.
        """
        if not recipients:
            recipients = self.config.get("default_recipients", [])

        if not recipients:
            raise ValueError("No recipients specified")

        mode = self._normalise_qr_mode(qr_mode)
        mode_label = mode.upper()

        # Reuse PhishTank URL fetching from the existing phishing generator
        if not self.phishing_gen.phishing_urls:
            self.phishing_gen.fetch_phishtank_data(limit=count * 2)

        if not self.phishing_gen.phishing_urls:
            raise ValueError("No phishing URLs available for QR phishing")

        emails: List[Dict[str, Any]] = []
        subject_template = (
            self.config.get("subject_templates", {}).get("qr_phishing")
            or "QR Phishing Test Email"
        )

        for i in range(count):
            url = self.phishing_gen.phishing_urls[i % len(self.phishing_gen.phishing_urls)]

            # Always include a plain-text body for compatibility
            text_body = """QR Phishing Test Email

This email encodes a phishing URL from PhishTank into a QR code for testing.

Depending on configuration, the QR code is included either inline in the email body,
inside an attached PDF, or both.

For safety, the underlying URL is only present inside the QR code and is not shown in clear text.

This email is generated for security testing purposes."""

            if count > 1:
                subject = f"{subject_template} [{mode_label}] - {i+1}"
            else:
                subject = f"{subject_template} [{mode_label}]"

            email_data: Dict[str, Any] = {
                "subject": subject,
                "body": text_body,
                "recipients": recipients,
                "type": "qr_phishing",
                "attachments": [],
            }

            # Generate QR PNG once and reuse for HTML and PDF variants
            png_bytes = self._generate_qr_png_bytes(url)

            if mode in ("body", "both"):
                cid = f"qr-{i}"
                email_data["html_body"] = self._build_html_body(cid)
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

            emails.append(email_data)

        return emails

