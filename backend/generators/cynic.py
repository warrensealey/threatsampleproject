"""
Cynic test email generator.
Generates VBS files and password-protected 7z archives based on cynictest scripts.
"""
import tempfile
from pathlib import Path
import subprocess
import time
import logging
import secrets
import hashlib
from backend.config import get_email_generation_config

logger = logging.getLogger(__name__)

# VBS template based on cynictestmaster.vbs
VBS_TEMPLATE = """' v2019.06.18
' This is a test sample to exercise behavioural detection in Symantec Cynic Dynamic Malware Analysis Service
' For any questions about this sample please contact: xxxx@symantec.com
' For more documentation about this sample please refer to this: https://*.symantec.com/location

messageText = "This is a test sample to exercise behavioural detection in Symantec Cynic Dynamic Malware Analysis Service"

Set fileSystemObject=CreateObject("Scripting.FileSystemObject")
fileName="C:\\Windows\\Temp\\cynic_test_sample.txt"
Set file = fileSystemObject.CreateTextFile(fileName,True)
file.Write messageText
file.Close

Set wscriptShell = CreateObject( "WScript.Shell" )
wscriptShell.RegWrite "HKCU\\cynic_test\\", ""
wscriptShell.RegWrite "HKCU\\cynic_test\\cynic_test_sample", messageText, "REG_SZ"

'This is the addition of some stuff to change the hash
' -
'cynictest{timestamp}.vbs
"""


class CynicGenerator:
    """Generate Cynic test emails with VBS files and password-protected 7z archives."""

    def __init__(self):
        """Initialize Cynic generator."""
        self.config = get_email_generation_config()
        self.password = "password"  # Default password from cynictest

    def create_vbs_file(self, output_path=None, timestamp=None):
        """
        Create VBS test file.

        Args:
            output_path: Path to save VBS file (optional)
            timestamp: Timestamp to include in VBS file (optional)

        Returns:
            Path to created VBS file
        """
        if timestamp is None:
            timestamp = int(time.time())

        if output_path is None:
            temp_dir = Path(tempfile.gettempdir())
            output_path = temp_dir / f"cynictest{timestamp}.vbs"
        else:
            output_path = Path(output_path)

        try:
            # Append timestamp and random-id comments to VBS file so each file has a unique hash
            random_id = secrets.randbits(64)
            vbs_content = VBS_TEMPLATE + f"\n'cynictest{timestamp}.vbs\n' random_id={random_id}"
            with open(output_path, 'w') as f:
                f.write(vbs_content)
            logger.info(f"Created VBS file: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to create VBS file: {e}")
            raise

    def create_7z_archive(self, vbs_file, output_path=None, password=None):
        """
        Create password-protected 7z archive.

        Args:
            vbs_file: Path to VBS file to archive
            output_path: Path to save 7z archive (optional)
            password: Archive password (default: "password")

        Returns:
            Path to created 7z archive
        """
        if password is None:
            password = self.password

        vbs_file = Path(vbs_file)

        # Default archive path is derived from the VBS file name so that each
        # generated sample gets its own 7z file (avoids reusing a single archive
        # across multiple emails and ensures differing hashes per sample).
        if output_path is None:
            output_path = vbs_file.with_suffix(".7z")
        else:
            output_path = Path(output_path)
        if not vbs_file.exists():
            raise FileNotFoundError(f"VBS file not found: {vbs_file}")

        try:
            # Use 7z command line tool (same as cynictest script)
            # 7z a -t7z -mhe=on -ppassword output.7z input.vbs
            cmd = [
                "7z", "a",
                "-t7z",
                "-mhe=on",  # Header encryption
                f"-p{password}",
                str(output_path),
                str(vbs_file)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"Created 7z archive: {output_path}")
                return output_path
            else:
                raise Exception(f"7z command failed: {result.stderr}")
        except FileNotFoundError:
            # Try py7zr as fallback
            try:
                import py7zr  # pyright: ignore[reportMissingImports]
                with py7zr.SevenZipFile(output_path, 'w', password=password) as archive:
                    archive.write(vbs_file, vbs_file.name)
                logger.info(f"Created 7z archive (py7zr): {output_path}")
                return output_path
            except ImportError:
                raise Exception("7z command not found and py7zr not available")
        except Exception as e:
            logger.error(f"Failed to create 7z archive: {e}")
            raise

    def generate_email_body(self, timestamp):
        """
        Generate email body for Cynic test email.

        Args:
            timestamp: Timestamp to include in body

        Returns:
            Email body text
        """
        return f"""The contents of this attachment are so important I had to password protect it! The password is password
{timestamp}"""

    def generate_emails(self, count=1, recipients=None):
        """
        Generate Cynic test emails.

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
        subject_template = self.config.get("subject_templates", {}).get("cynic", "This is a important top secret email!")

        for i in range(count):
            timestamp = int(time.time()) + i
            vbs_file = self.create_vbs_file(timestamp=timestamp)
            archive_file = self.create_7z_archive(vbs_file)

            # Compute MD5 checksum of the VBS script so each sample can be
            # uniquely identified in logs and UI notifications.
            try:
                with open(vbs_file, "rb") as f:
                    vbs_data = f.read()
                vbs_md5 = hashlib.md5(vbs_data).hexdigest()
                logger.info(f"Cynic VBS file {vbs_file} MD5: {vbs_md5}")
            except Exception as e:
                vbs_md5 = None
                logger.error(f"Failed to compute MD5 for Cynic VBS file {vbs_file}: {e}")

            body = self.generate_email_body(timestamp)
            subject = f"{subject_template} {timestamp}"

            emails.append({
                "subject": subject,
                "body": body,
                "recipients": recipients,
                "type": "cynic",
                "attachments": [str(archive_file)],
                "temp_files": [str(vbs_file)],  # Track temp files for cleanup
                "vbs_md5": vbs_md5,
                "vbs_path": str(vbs_file),
            })

        return emails

