"""
Phishing email generator based on PhishTank automation.
Generates realistic phishing emails with URLs from PhishTank database.
"""
import requests
import csv
import io
import gzip
import bz2
import logging
from pathlib import Path
from backend.config import get_email_generation_config

logger = logging.getLogger(__name__)

PHISHTANK_URL = "http://data.phishtank.com/data/online-valid.json.gz"


class PhishingGenerator:
    """Generate phishing emails from PhishTank data."""
    
    def __init__(self):
        """Initialize phishing generator."""
        self.config = get_email_generation_config()
        self.phishing_urls = []
    
    def fetch_phishtank_data(self, limit=20):
        """
        Fetch phishing URLs from PhishTank database.
        
        Args:
            limit: Maximum number of URLs to fetch
        
        Returns:
            List of phishing URLs
        """
        try:
            logger.info(f"Fetching PhishTank data (limit: {limit})")
            response = requests.get(PHISHTANK_URL, timeout=60)
            response.raise_for_status()
            
            # Decompress gzip data
            data = gzip.decompress(response.content)
            json_data = io.StringIO(data.decode('utf-8'))
            
            # Parse JSON
            import json
            entries = json.load(json_data)
            
            urls = []
            for entry in entries[:limit]:
                if 'url' in entry:
                    urls.append(entry['url'])
            
            self.phishing_urls = urls
            logger.info(f"Fetched {len(urls)} phishing URLs")
            return urls
        except Exception as e:
            logger.error(f"Failed to fetch PhishTank data: {e}")
            return []
    
    def generate_email_body(self, url, template_type="warning"):
        """
        Generate email body for phishing email.
        
        Args:
            url: Phishing URL to include
            template_type: Type of template to use
        
        Returns:
            Email body text
        """
        templates = {
            "warning": f"""Warning - Potentially Hazardous URL Detected

This email contains a potentially hazardous URL that has been flagged:

{url}

Please exercise caution when accessing this link.

This is a test email generated for security testing purposes.""",
            
            "urgent": f"""URGENT: Security Alert

A potentially malicious URL has been detected:

{url}

Please review this URL immediately.

This is a test email generated for security testing purposes.""",
            
            "notification": f"""Security Notification

The following URL has been identified as potentially hazardous:

{url}

This is a test email generated for security testing purposes."""
        }
        
        return templates.get(template_type, templates["warning"])
    
    def generate_emails(self, count=1, recipients=None, template_type="warning"):
        """
        Generate phishing emails.
        
        Args:
            count: Number of emails to generate
            recipients: List of recipient email addresses
            template_type: Type of email template to use
        
        Returns:
            List of email dictionaries with subject, body, and recipients
        """
        if not recipients:
            recipients = self.config.get("default_recipients", [])
        
        if not recipients:
            raise ValueError("No recipients specified")
        
        # Fetch phishing URLs if not already fetched
        if not self.phishing_urls:
            self.fetch_phishtank_data(limit=count * 2)
        
        if not self.phishing_urls:
            raise ValueError("No phishing URLs available")
        
        emails = []
        subject_template = self.config.get("subject_templates", {}).get("phishing", "Warning - Potentially Hazardous URL")
        
        for i in range(count):
            if i >= len(self.phishing_urls):
                # Refetch if needed
                self.fetch_phishtank_data(limit=(count - i) * 2)
            
            url = self.phishing_urls[i % len(self.phishing_urls)]
            body = self.generate_email_body(url, template_type)
            subject = f"{subject_template} - {i+1}"
            
            emails.append({
                "subject": subject,
                "body": body,
                "recipients": recipients,
                "type": "phishing",
                "url": url
            })
        
        return emails

