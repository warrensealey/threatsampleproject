# Email Data Generation Project - Complete Plan

**Repository:** `/Users/warrensealey/threatsampleproject/`  
**GitHub:** https://github.com/warrensealey/threatsampleproject

## Project Overview

Full-stack Python web application for generating and sending test emails (phishing, EICAR malware, and Cynic test emails) through Symantec Email Security Cloud via SMTP, with a web-based configuration interface and email client functionality.

## Project Structure

```
threatsampleproject/
├── backend/
│   ├── app.py                 # Flask main application
│   ├── config.py              # Configuration management
│   ├── email_generator.py     # Email generation coordinator
│   ├── smtp_client.py         # SMTP client for Symantec
│   ├── email_client.py        # IMAP client for reading emails
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── phishing.py        # Phishing email generator (based on phishtank-automation)
│   │   ├── eicar.py           # EICAR test email generator
│   │   └── cynic.py           # Cynic test email generator (based on cynictest)
│   └── api/
│       ├── __init__.py
│       └── routes.py          # REST API endpoints
├── frontend/
│   ├── index.html             # Main dashboard
│   ├── config.html            # Configuration page
│   ├── email.html             # Email client page
│   ├── js/
│   │   ├── app.js             # Main application logic
│   │   └── api.js             # API client
│   └── css/
│       └── style.css          # Styling
├── templates/                 # Email templates
├── data/                      # Data storage (config, logs)
│   ├── config.json            # Application configuration
│   └── logs/                  # Application logs
├── requirements.txt
├── README.md
├── PROJECT_PLAN.md
└── start.sh                   # Startup script
```

## Implementation Details

### Backend Components

1. **SMTP Client (`smtp_client.py`)**:
   - Python smtplib implementation
   - Support for Symantec Email Security Cloud SMTP
   - Configurable server, port, authentication (TLS/SSL)
   - Support for email attachments (7z, EICAR files)
   - Context manager support for connection handling

2. **Email Client (`email_client.py`)**:
   - IMAP client for reading emails from web-based email accounts
   - Based on mutt configuration structure
   - Support for SSL/TLS connections
   - Read inbox, folders, messages
   - Display email headers, body, attachments
   - Configurable through UI (IMAP server, port, username, password, SSL settings)

3. **Email Generators**:
   - **Phishing Generator (`generators/phishing.py`)**:
     - Integrates with PhishTank online-valid dataset
     - Fetches phishing URLs from PhishTank API
     - Generates realistic phishing email templates
     - Includes phishing URLs in email body
     - Multiple template types (warning, urgent, notification)
   - **EICAR Generator (`generators/eicar.py`)**:
     - Generates EICAR test file (standard antivirus test file)
     - Creates temporary EICAR.com file
     - Attaches to email for antivirus testing
   - **Cynic Generator (`generators/cynic.py`)**:
     - Generates VBS test files based on cynictestmaster.vbs
     - Creates password-protected 7z archives (password: "password")
     - Uses same body template as cynictest scripts
     - Supports both 7z command-line tool and py7zr library

4. **Email Generator Coordinator (`email_generator.py`)**:
   - Orchestrates email generation and sending
   - Derives SMTP settings from email client configuration
   - Handles email sending with error tracking
   - Maintains email sending history

5. **Configuration Management (`config.py`)**:
   - JSON-based configuration storage
   - Stores SMTP settings (server, port, username, password, TLS/SSL)
   - Stores email client settings (IMAP/SMTP server, port, username, password, SSL)
   - Email generation parameters (count, recipients, templates)
   - Email sending history (last 100 entries)
   - Auto-creates config file with defaults if not exists

6. **REST API (`api/routes.py`)**:
   - `GET /api/config` - Retrieve current configuration
   - `POST /api/config` - Update configuration
   - `GET /api/email/config` - Get email client configuration
   - `POST /api/email/config` - Update email client configuration
   - `GET /api/email/folders` - List email folders
   - `GET /api/email/messages` - Get messages from folder
   - `GET /api/email/message/{id}` - Get specific message
   - `POST /api/test/email` - Test email service configuration (send test email with connection info)
   - `GET /api/mutt/status` - Check if mutt is installed and get version
   - `POST /api/mutt/install` - Install mutt using hands-off installation script
   - `POST /api/send/phishing` - Send phishing test emails
   - `POST /api/send/eicar` - Send EICAR test emails
   - `POST /api/send/cynic` - Send Cynic test emails
   - `GET /api/history` - Get email sending history

### Frontend Components

1. **Configuration Page (`config.html`)**:
   - Email provider dropdown selector (AOL, Gmail, MS Outlook, GMX)
     - Auto-populates IMAP and SMTP settings based on provider
     - GMX pre-populated with mutt settings from development server
   - Email client settings form:
     - IMAP server, port, username, password
     - SSL/TLS options
   - SMTP settings form:
     - SMTP server, port
     - TLS/SSL options
   - Mutt installation status module:
     - Displays mutt installation status and version
     - Install button if mutt not available
     - Refresh status button
   - Email generation configuration:
     - Default recipients (comma-separated)
     - Default count
   - Test email service configuration button:
     - Sends test email with connection info popup
     - Prompts for receipt confirmation
   - Save/load configuration functionality

2. **Dashboard (`index.html`)**:
   - Send email interface:
     - Phishing emails button
     - EICAR test emails button
     - Cynic test emails button
     - Pre-populates recipients from default configuration
   - Email history/logs:
     - Table view of sent emails
     - Shows type, subject, recipients, time, status
   - Status indicators for email sending operations

3. **Email Client Page (`email.html`)**:
   - Three-panel layout:
     - Folder list sidebar
     - Message list view
     - Message reading pane
   - Email account connection status
   - Folder navigation
   - Message viewing with headers and body
   - Attachment information display
   - Refresh functionality

### Key Features

1. **Email Provider Presets**:
   - AOL: imap.aol.com:993, smtp.aol.com:465
   - Gmail: imap.gmail.com:993, smtp.gmail.com:587
   - MS Outlook: outlook.office365.com:993, smtp.office365.com:587
   - GMX: imap.gmx.com:993, mail.gmx.com:587 (pre-populated with user's mutt settings)

2. **Email Testing**:
   - Test email configuration with connection status popup
   - Uses default recipient or prompts if not configured
   - Shows SMTP connection details
   - Confirms receipt with user

3. **Mutt Installation**:
   - Automatic mutt status checking
   - OS detection (Ubuntu/Debian, RHEL/CentOS, macOS)
   - Hands-off installation via web UI
   - Installation progress feedback

4. **Default Recipients**:
   - Configurable default recipients
   - Auto-populates in send dialogs
   - Can be overridden per send operation

### Integration Points

- **PhishTank Integration**: 
  - Reference: `~/phishtank-automation` on development server (wsealey@192.168.1.177)
  - Fetches online-valid dataset from PhishTank API
  - Uses PhishTank URLs for phishing email generation

- **Cynic Test Integration**: 
  - Reference: `~/cynictest` on development server
  - Uses cynictestmaster.vbs as template for VBS file generation
  - Uses same 7z packaging method (password-protected archives)
  - Uses same email body template

- **Mutt Configuration**: 
  - Reference: `~/.muttrc` on development server
  - Email client settings based on mutt configuration structure
  - SMTP settings derived from mutt config

- **Email Sending**: 
  - Uses Python SMTP instead of mutt command-line
  - Maintains same attachment/body structure as mutt-based scripts

## Dependencies

- Flask 3.0.0 (web framework)
- Flask-CORS 4.0.0 (CORS support)
- requests >= 2.28.0 (for PhishTank API)
- py7zr 0.21.0 (for 7z archive creation, fallback if 7z command not available)
- python-dotenv 1.0.0 (environment variable support)
- smtplib (built-in, for SMTP)
- imaplib (built-in, for IMAP email reading)
- email (built-in, for email construction and parsing)
- json (built-in, for configuration storage)
- mutt (optional, for reference configuration - can be installed via UI)
- 7z command-line tool (optional, for Cynic test emails - py7zr used as fallback)

## Development Server References

- **SSH Access**: `wsealey@192.168.1.177`
- **PhishTank Automation**: `~/phishtank-automation`
- **Cynic Test**: `~/cynictest`
- **Mutt Config**: `~/.muttrc`
- **Application Location**: `~/email-data-generation`

## Installation and Setup

### Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install 7z tool (optional, for Cynic emails)
4. Run: `python backend/app.py`
5. Access at http://localhost:5000

### Development Server

The application is installed at `~/email-data-generation` on the development server.

**Start the application:**
```bash
cd ~/email-data-generation
./start.sh
```

Or manually:
```bash
cd ~/email-data-generation
export PYTHONPATH=.:$PYTHONPATH
python3 backend/app.py
```

## Configuration Flow

1. **Initial Setup**:
   - Access configuration page
   - Select email provider (GMX pre-selected with mutt settings)
   - Configure email client (IMAP) and SMTP settings
   - Set default recipients for email generation
   - Test email configuration

2. **Mutt Installation** (if needed):
   - Check mutt status on configuration page
   - Click "Install Mutt" if not installed
   - Installation runs automatically based on OS

3. **Sending Test Emails**:
   - Go to dashboard
   - Select email type (Phishing, EICAR, Cynic)
   - Recipients pre-populated from defaults
   - Emails sent through configured SMTP server

4. **Reading Emails**:
   - Configure email client settings
   - Access Email Client page
   - Browse folders and read messages

## API Endpoints Summary

### Configuration
- `GET /api/config` - Get all configuration
- `POST /api/config` - Update configuration
- `GET /api/email/config` - Get email client config
- `POST /api/email/config` - Update email client config

### Email Client
- `GET /api/email/folders` - List folders
- `GET /api/email/messages?folder=INBOX&limit=50` - Get messages
- `GET /api/email/message/{id}?folder=INBOX` - Get message details

### Email Operations
- `POST /api/test/email` - Test email configuration
- `POST /api/send/phishing` - Send phishing emails
- `POST /api/send/eicar` - Send EICAR test emails
- `POST /api/send/cynic` - Send Cynic test emails
- `GET /api/history` - Get email history

### System
- `GET /api/mutt/status` - Check mutt installation
- `POST /api/mutt/install` - Install mutt

## Security Considerations

- Passwords stored in configuration file (consider encryption for production)
- SMTP credentials used for sending emails
- IMAP credentials used for reading emails
- Test emails sent through configured SMTP server
- EICAR and Cynic test files are safe test samples, not actual malware

## Future Enhancements

- Email template customization
- Scheduled email sending
- Email statistics and reporting
- Multiple email account support
- Email search functionality
- Attachment download support
- Configuration encryption
