# Project Documentation

Comprehensive documentation for the Email Data Generation application.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [Email Providers](#email-providers)
5. [Email Types](#email-types)
6. [Configuration](#configuration)
7. [Usage Guide](#usage-guide)
8. [Troubleshooting](#troubleshooting)

## Project Overview

The Email Data Generation application is a full-stack web application designed for generating and sending test emails for security testing purposes. It supports multiple email providers and can generate three types of test emails:

- **Phishing Emails**: Test emails with PhishTank URLs
- **EICAR Test Emails**: Standard antivirus test files
- **Cynic Test Emails**: Password-protected VBS archives

### Key Features

- Multi-provider email support (GMX, Gmail, Yahoo, iCloud, Zoho, Outlook.com, AOL, Office365)
- Web-based configuration interface
- Detailed connection information display
- Email sending history tracking
- Test email configuration validation

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
│   │   └── cynic.py       # Cynic test generator
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

#### POST `/api/send/cynic`
Send Cynic test emails.

**Request Body**:
```json
{
  "count": 1,
  "recipients": ["email@example.com"]
}
```

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

### Cynic Test Emails

Cynic test emails contain password-protected VBS archives. These test emails are used for advanced security testing.

**Features**:
- Password-protected 7z archives
- VBS script attachments
- Requires 7z command-line tool or py7zr library

## Configuration

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
      "cynic": "This is a important top secret email!"
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

3. **Enter Details**:
   - Number of emails to send
   - Recipient email addresses (comma-separated)

4. **Review Results**:
   - Connection details modal shows full connection information
   - Success/failure status displayed
   - Email history updated automatically

### Testing Email Configuration

1. **Navigate to Configuration**: http://localhost:5000/config

2. **Configure Email Provider**:
   - Select provider from dropdown
   - Enter username and password
   - Verify server settings are correct

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

## Security Considerations

1. **Credentials Storage**: Passwords are stored in plain text in `data/config.json`. Ensure proper file permissions:
   ```bash
   chmod 600 data/config.json
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

