"""
GTUBE spam-test email generator.
Creates RFC-compliant emails containing the GTUBE test string to trigger anti-spam systems.
"""
import logging
from backend.config import get_email_generation_config

logger = logging.getLogger(__name__)

# Canonical GTUBE string per https://en.wikipedia.org/wiki/GTUBE
GTUBE_STRING = "XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X"


class GTUBEGenerator:
    """Generate GTUBE spam-test emails."""

    def __init__(self):
        """Initialize GTUBE generator with config."""
        self.config = get_email_generation_config()

    def generate_email_body(self):
        """
        Build the GTUBE email body.

        Returns:
            Email body text containing the GTUBE string.
        """
        return f"""This email contains the GTUBE spam-test string.

The GTUBE string is used to verify spam detection pipelines. It is safe and not malicious.

GTUBE Test String:
{GTUBE_STRING}

If this message is received, your outgoing mail controls are functioning as expected."""

    def generate_emails(self, count=1, recipients=None):
        """
        Generate GTUBE test emails.

        Args:
            count: Number of emails to generate
            recipients: List of recipient email addresses

        Returns:
            List of email dictionaries to send.
        """
        if not recipients:
            recipients = self.config.get("default_recipients", [])

        if not recipients:
            raise ValueError("No recipients specified")

        subject_template = self.config.get("subject_templates", {}).get(
            "gtube", "GTUBE Spam Test Email"
        )
        body = self.generate_email_body()
        emails = []

        for i in range(count):
            subject = f"{subject_template} - {i+1}" if count > 1 else subject_template
            emails.append(
                {
                    "subject": subject,
                    "body": body,
                    "recipients": recipients,
                    "type": "gtube",
                    "attachments": [],
                }
            )

        return emails

