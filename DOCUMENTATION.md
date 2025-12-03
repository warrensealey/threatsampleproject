# Project Documentation

**Version 1.1.0**

Comprehensive documentation for the Email Data Generation application.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [Email Providers](#email-providers)
5. [Email Types](#email-types)
6. [Configuration](#configuration)
7. [Usage Guide](#usage-guide)
8. [Docker Deployment](#docker-deployment)
9. [Troubleshooting](#troubleshooting)
10. [Security Considerations](#security-considerations)

## Project Overview

The Email Data Generation application is a full-stack web application designed for generating and sending test emails for security testing purposes. It supports multiple email providers and can generate several types of test emails:

- **Phishing Emails**: Test emails with PhishTank URLs
- **EICAR Test Emails**: Standard antivirus test files
- **Cynic Test Emails**: Password-protected VBS archives
- **GTUBE Spam-Test Emails**: Single-message spam detector tests that embed the canonical GTUBE string `XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X` ([spec](https://en.wikipedia.org/wiki/GTUBE))
- **Custom Emails**: Fully configurable emails with custom subject, body, display name, and optional attachments

### Key Features

- Multi-provider email support (GMX, Gmail, Yahoo, iCloud, Zoho, Outlook.com, AOL, Office365)
- Web-based configuration interface
- Detailed connection information display
- Email sending history tracking
- Test email configuration validation
- GTUBE spam-test workflow for validating anti-spam controls

## Architecture

### Project Structure

```
threatsampleproject/
├── backend/                 # Python backend
│   ├── api/                # API routes
│   │   └── routes.py       # REST API endpoints
│   ├── generators/         # Email generators
│   │   ├── phishing.py    # Phishing email generator
│   │   ├── eicar.py       # EICAR test generator
│   │   ├── cynic.py       # Cynic test generator
│   │   └── gtube.py       # GTUBE spam-test generator
│   ├── app.py             # Flask application
│   ├── config.py          # Configuration management
│   ├── email_generator.py # Email generation coordinator
│   ├── smtp_client.py     # SMTP client
│   └── email_client.py    # IMAP client (legacy)
├── frontend/              # Web frontend
│   ├── index.html         # Dashboard
│   ├── config.html        # Configuration page
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript
│       ├── app.js         # Application logic
│       └── api.js         # API client
├── data/                  # Runtime data (auto-created)
│   ├── config.json        # Configuration file
│   └── logs/              # Log files
└── requirements.txt       # Python dependencies
```

### Technology Stack

- **Backend**: Python 3.8+, Flask 3.0.0
- **Frontend**: HTML5, JavaScript (ES6+), CSS3
- **Email**: SMTP (smtplib), IMAP (imaplib)
- **Dependencies**: Flask-CORS, requests, python-dotenv

## API Reference

### Configuration Endpoints

#### GET `/api/config`
Get current application configuration.

**Response**:
```json
{
  "smtp": { ... },
  "email_client": { ... },
  "email_generation": { ... },
  "history": [ ... ]
}
```

#### POST `/api/config`
Update application configuration.

**Request Body**:
```json
{
  "smtp": { ... },
  "email_client": { ... },
  "email_generation": { ... }
}
```

#### GET `/api/email/config`
Get email client configuration.

#### POST `/api/email/config`
Update email client configuration.

### Email Sending Endpoints

#### POST `/api/send/phishing`
Send phishing test emails.

**Request Body**:
```json
{
  "count": 1,
  "recipients": ["email@example.com"],
  "template_type": "warning"
}
```

**Response**:
```json
{
  "success": true,
  "sent": 1,
  "failed": 0,
  "total": 1,
  "connection_info": { ... },
  "connection_attempt": { ... }
}
```

#### POST `/api/send/eicar`
Send EICAR test emails.

**Request Body**:
```json
{
  "count": 1,
  "recipients": ["email@example.com"]
}
```

**Response** mirrors the other send endpoints and contains `success`, `sent`, `failed`, `total`, `connection_info`, `connection_attempt`, and (on success) `connection_details`.

#### POST `/api/send/cynic`
Send Cynic test emails.

**Request Body**:
```json
{
  "count": 1,
  "recipients": ["email@example.com"]
}
```

#### POST `/api/send/gtube`
Send GTUBE spam-test emails.

**Request Body**:
```json
{
  "count": 1,
  "recipients": ["email@example.com"]
}
```

#### POST `/api/send/custom`
Send custom emails with configurable fields.

**Request Body**:
```json
{
  "count": 1,
  "recipients": ["email@example.com"],
  "subject": "Custom Email Subject",
  "body": "Custom email body text",
  "display_name": "John Doe",
  "attachment_type": ".zip"
}
```

**Parameters**:
- `count` (number): Number of emails to send
- `recipients` (array): List of recipient email addresses
- `subject` (string, required): Email subject line
- `body` (string, required): Email body text
- `display_name` (string, optional): Sender display name
- `attachment_type` (string, optional): Attachment file extension - one of: `.zip`, `.com`, `.scr`, `.pdf`, `.bat`, or `null` for no attachment

### Test Endpoints

#### POST `/api/test/email`
Test email service configuration.

**Request Body**:
```json
{
  "recipient": "test@example.com",
  "email_client_config": { ... }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Test email sent successfully",
  "connection_info": { ... },
  "connection_attempt": { ... },
  "error_details": "...",
  "subject": "..."
}
```

### History Endpoint

#### GET `/api/history`
Get email sending history.

**Response**:
```json
{
  "history": [
    {
      "type": "phishing",
      "subject": "...",
      "recipients": ["..."],
      "timestamp": "2024-01-01T00:00:00",
      "status": "sent"
    }
  ]
}
```

## Email Providers

The application supports the following email providers:

| Provider | IMAP Server | IMAP Port | SMTP Server | SMTP Port | Encryption |
|----------|-------------|-----------|-------------|-----------|------------|
| GMX | imap.gmx.com | 993 | mail.gmx.com | 587 | TLS |
| Gmail | imap.gmail.com | 993 | smtp.gmail.com | 587 | TLS |
| Yahoo | imap.mail.yahoo.com | 993 | smtp.mail.yahoo.com | 587 | TLS |
| iCloud | imap.mail.me.com | 993 | smtp.mail.me.com | 587 | TLS |
| Zoho | imap.zoho.com | 993 | smtp.zoho.com | 587 | TLS |
| Outlook.com | imap-mail.outlook.com | 993 | smtp-mail.outlook.com | 587 | TLS |
| Office365 | outlook.office365.com | 993 | smtp.office365.com | 587 | TLS |
| AOL | imap.aol.com | 993 | smtp.aol.com | 465 | SSL |

> **Gmail-specific behavior**
> - Gmail requires an **app-specific password** generated in Google Account → Security → App Passwords before IMAP/SMTP access will succeed.
> - With that credential, Gmail can successfully deliver phishing URL tests and GTUBE spam-test emails from this application.
> - Gmail currently blocks EICAR and Cynic payloads during outbound scanning, so those templates will fail when attempting to send via Gmail.

> **Yahoo-specific behavior**
> - Yahoo requires an **app-specific password** generated in Yahoo Account → Account Security → Generate app password before IMAP/SMTP access will succeed. Without it, connections will fail with "Connection unexpectedly closed" errors.
> - With that credential, Yahoo can successfully deliver phishing URL tests and GTUBE spam-test emails from this application.
> - Yahoo may block EICAR and Cynic payloads during outbound scanning similar to Gmail, so those templates may fail when attempting to send via Yahoo.

### Provider Auto-Detection

The backend automatically detects the email provider from the IMAP server address and configures the appropriate SMTP server settings.

## Email Types

### Phishing Emails

Phishing test emails contain URLs from PhishTank database. These are used to test email security filters and user awareness.

**Features**:
- PhishTank URL integration
- Multiple template types
- Customizable subject lines

### EICAR Test Emails

EICAR (European Institute for Computer Antivirus Research) test files are standard test files used to verify antivirus software is working correctly.

**Features**:
- Standard EICAR test file attachment
- Recognized by all major antivirus software
- Safe for testing
- Gmail-specific note: Google actively blocks outbound delivery of the EICAR attachment, so EICAR sends via Gmail will fail even with an app-specific password.
- Yahoo-specific note: Yahoo may block outbound delivery of the EICAR attachment similar to Gmail, so EICAR sends via Yahoo may fail even with an app-specific password.

### Cynic Test Emails

Cynic test emails contain password-protected VBS archives. These test emails are used for advanced security testing.

**Features**:
- Password-protected 7z archives
- VBS script attachments
- Each generated VBS script includes a unique random-number comment (for example `' random_id=...`) so that the file hash changes on every sample while the behaviour remains identical
- Requires 7z command-line tool or py7zr library
- Gmail-specific note: Google currently rejects the Cynic payload during outbound scanning, so Cynic sends via Gmail will fail.
- Yahoo-specific note: Yahoo may reject the Cynic payload during outbound scanning similar to Gmail, so Cynic sends via Yahoo may fail.

### GTUBE Spam-Test Emails

GTUBE (Generic Test for Unsolicited Bulk Email) is a standard 68-byte string recognized by many anti-spam engines (see [GTUBE specification](https://en.wikipedia.org/wiki/GTUBE)). Sending this string inside an email body should reliably trigger spam filtering without sending malicious content.

**Features**:
- Standard GTUBE test string in email body
- Single email per send operation
- Recognized by SpamAssassin and other anti-spam systems

### Custom Emails

Custom emails allow full control over email content and appearance for flexible testing scenarios.

**Features**:
- Configurable subject line (required)
- Configurable body text (required)
- Optional sender display name (appears as "Display Name <email@example.com>")
- Optional harmless dummy attachments:
  - `.zip`: Minimal ZIP archive
  - `.com`: Text file with .com extension
  - `.scr`: Text file with .scr extension
  - `.pdf`: Minimal valid PDF document
  - `.bat`: Harmless batch script file
- Multiple recipients support
- Configurable email count

## Configuration

> **⚠️ STRONGLY RECOMMENDED: GMX Email Account**
>
> We strongly recommend using a GMX email account for this application. GMX server settings have been thoroughly tested and verified to work reliably. All other email provider settings are still in development and may require additional configuration or troubleshooting.
>
> To create a free GMX account, visit https://www.gmx.com/

### Configuration File Location

Configuration is stored in: `data/config.json`

### Configuration Structure

```json
{
  "smtp": {
    "server": "",
    "port": 587,
    "username": "",
    "password": "",
    "use_tls": true,
    "use_ssl": false
  },
  "email_client": {
    "imap_server": "",
    "imap_port": 993,
    "username": "",
    "password": "",
    "use_ssl": true,
    "use_starttls": false,
    "smtp_server": "",
    "smtp_port": 587,
    "smtp_use_tls": true,
    "smtp_use_ssl": false
  },
  "email_generation": {
    "default_recipients": [],
    "default_count": 1,
    "subject_templates": {
      "phishing": "Warning - Potentially Hazardous URL",
      "eicar": "EICAR Test File",
        "cynic": "This is a important top secret email!",
        "gtube": "GTUBE Spam Test Email"
    }
  },
  "history": []
}
```

### Environment Variables

The application supports `.env` file for environment-specific configuration (via python-dotenv).

## Usage Guide

### Sending Test Emails

1. **Navigate to Dashboard**: http://localhost:5000

2. **Select Email Type**:
   - Click "Send Phishing Emails" for phishing tests
   - Click "Send EICAR Emails" for antivirus tests
   - Click "Send Cynic Emails" for advanced tests
   - Click "Send GTUBE Email" for spam filter tests
   - Click "Send Custom Email" for fully customizable emails
   - Click "Send GTUBE Email" to send the canonical GTUBE spam-test string (single message)

3. **Enter Details**:
   - Number of emails to send (GTUBE is fixed to a single message)
   - Recipient email addresses (comma-separated)

4. **Review Results**:
   - Connection details modal shows full connection information
   - Success/failure status displayed
   - Email history updated automatically

### Testing Email Configuration

1. **Navigate to Configuration**: http://localhost:5000/config

2. **Configure Email Provider**:
   - **⚠️ STRONGLY RECOMMENDED: Select GMX** from the dropdown (pre-selected by default)
   - GMX settings have been tested and verified to work
   - Enter your GMX email address as username
   - Enter your GMX account password
   - Server settings will auto-populate for GMX:
     - IMAP: `imap.gmx.com:993`
     - SMTP: `mail.gmx.com:587`

   **Note**: Other providers (Gmail, Yahoo, etc.) are still in development and may require troubleshooting.

3. **Test Configuration**:
   - Click "Test Email Configuration"
   - Enter test recipient email
   - Review connection details and test results

### Viewing Email History

Email sending history is displayed on the Dashboard page, showing:
- Email type
- Subject line
- Recipients
- Timestamp
- Status

## Troubleshooting

### Common Issues

#### Connection Failures

**Problem**: "Failed to connect to SMTP server"

**Solutions**:
1. Verify server address and port are correct
2. Check firewall settings
3. Verify SSL/TLS configuration matches provider requirements
4. Ensure credentials are correct
5. Check if provider requires app-specific passwords

#### Authentication Errors

**Problem**: "Authentication failed"

**Solutions**:
1. Verify username and password are correct
2. For Gmail/Yahoo: Use app-specific passwords if 2FA is enabled
3. Check if account requires "Less secure app access" to be enabled
4. Verify account is not locked or suspended

#### Module Import Errors

**Problem**: "ModuleNotFoundError: No module named 'backend'"

**Solutions**:
1. Ensure PYTHONPATH is set: `export PYTHONPATH=.:$PYTHONPATH`
2. Run from project root directory
3. Use the provided `start.sh` script

#### Port Already in Use

**Problem**: "Address already in use"

**Solutions**:
1. Find and kill process using port 5000
2. Change port in `backend/app.py` (line 45)
3. Use a different port: `app.run(debug=True, host='0.0.0.0', port=5001)`

### Error Messages

The application provides detailed error messages with connection attempt information:

- **Connection Attempt Failed**: Shows server, username, encryption method, and possible causes
- **Authentication Failed**: Indicates credential issues
- **Send Failed**: Connection successful but email sending failed

All error messages include troubleshooting suggestions.

## Docker Deployment

The application is containerized and available via Docker.

### GitHub Container Registry

- **Image**: `ghcr.io/warrensealey/threatsampleproject:latest`
- **Version Tags**: Available for each version (e.g., `1.0.0`)
- **Automated Builds**: On push to main branch via GitHub Actions

### Running with Docker

```bash
# Pull the latest image
docker pull ghcr.io/warrensealey/threatsampleproject:latest

# Run the container
docker run -d \
  --name email-data-gen \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  ghcr.io/warrensealey/threatsampleproject:latest

# Or use docker-compose
docker-compose up -d
```

### Docker Configuration

- **Port**: 5000 (configurable via `-p` flag)
- **Data Persistence**: `data/` directory mounted as volume
- **User**: Runs as non-root user for security
- **Health Checks**: Included in docker-compose configuration

See [INSTALLATION.md](INSTALLATION.md) for detailed Docker setup instructions.

## Security Considerations

1. **Credentials Storage**:
   - Only password fields are encrypted at rest using symmetric encryption (Fernet) before being written to `data/config.json`.
   - The encryption key is loaded from the `ENCRYPTION_KEY` environment variable when set, or from `data/.encryption_key` (auto-generated on first use and git-ignored).
   - Non-sensitive fields (such as usernames, server names, and ports) remain in plain text for easier troubleshooting.
   - Ensure proper file permissions on the data directory:
   ```bash
   chmod 600 data/config.json
   chmod 600 data/.encryption_key  # if using the key file
   ```

2. **Network Security**: The application runs on HTTP by default. For production, use HTTPS with a reverse proxy.

3. **Firewall**: Restrict access to the application port (5000) to trusted networks only.

4. **Email Provider Security**: Use app-specific passwords when available. Enable 2FA on email accounts.

## Development

### Running in Development Mode

```bash
# Development mode with auto-reload
export FLASK_ENV=development
export PYTHONPATH=.:$PYTHONPATH
python3 backend/app.py
```

### Adding New Email Providers

1. Add provider configuration to `frontend/js/app.js` (`emailProviderConfigs`)
2. Add provider option to `frontend/config.html` dropdown
3. Add SMTP derivation logic to `backend/api/routes.py` and `backend/email_generator.py`

### Logging

Application logs are written to:
- Console output (development)
- `data/logs/` directory (if configured)

Log level can be adjusted in `backend/app.py`:
```python
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for more detail
```

## Support

For issues, questions, or contributions:
- GitHub Repository: https://github.com/warrensealey/threatsampleproject
- Check existing issues before creating new ones
- Provide detailed error messages and connection details when reporting issues

