"""
Newly registered domain (NRD) email generator.
"""
import logging
from typing import List, Optional

from backend.config import get_email_generation_config
from backend.nrd_cache import build_nrd_url, peek_next_domains

logger = logging.getLogger(__name__)


class NRDGenerator:
    """Generate test emails containing newly registered domain URLs."""

    def __init__(self):
        self.config = get_email_generation_config()

    def generate_email_body(self, url: str, domain: str) -> str:
        """Generate plain-text body for an NRD test email."""
        return f"""Newly Registered Domain Test

This email contains a URL for a newly registered domain:

{url}

Domain: {domain}

This is a test email generated for security testing purposes."""

    def generate_emails(
        self,
        count: int = 1,
        recipients: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        Generate NRD emails without advancing the domain cursor.

        The coordinator advances the cursor after successful delivery.
        """
        if not recipients:
            recipients = self.config.get("default_recipients", [])

        if not recipients:
            raise ValueError("No recipients specified")

        domains = peek_next_domains(count)
        subject_template = self.config.get("subject_templates", {}).get(
            "nrd", "Newly Registered Domain Test"
        )

        emails = []
        for domain in domains:
            url = build_nrd_url(domain)
            body = self.generate_email_body(url, domain)
            subject = f"{subject_template} - {domain}"
            emails.append(
                {
                    "subject": subject,
                    "body": body,
                    "recipients": recipients,
                    "type": "nrd",
                    "domain": domain,
                    "url": url,
                }
            )

        logger.info("Generated %s NRD email(s)", len(emails))
        return emails
