# Email Data Generation Project - Complete Plan

**Version:** 1.0.0  
**Repository:** `/Users/warrensealey/threatsampleproject/`  
**GitHub:** https://github.com/warrensealey/threatsampleproject

## Project Overview

Full-stack Python web application for generating and sending test emails (phishing, EICAR malware, Cynic test emails, GTUBE spam-test messages, and custom emails) through SMTP, with a web-based configuration interface supporting multiple email providers.

## Project Structure

```
threatsampleproject/
├── backend/                 # Python Flask backend
│   ├── api/                 # REST API routes
│   │   └── routes.py        # API endpoints
│   ├── generators/         # Email generators
│   │   ├── phishing.py     # Phishing email generator
│   │   ├── eicar.py        # EICAR test generator
│   │   ├── cynic.py        # Cynic test generator
│   │   ├── gtube.py        # GTUBE spam-test generator
│   │   └── custom.py       # Custom email generator
│   ├── app.py              # Flask main application
│   ├── config.py           # Configuration management
│   ├── email_generator.py  # Email generation coordinator
│   ├── smtp_client.py      # SMTP client
│   └── email_client.py     # IMAP client (for reading emails)
├── frontend/               # Web frontend
│   ├── index.html          # Main dashboard
│   ├── config.html         # Configuration page
│   ├── js/
│   │   ├── app.js          # Main application logic
│   │   └── api.js          # API client
│   └── css/
│       └── style.css       # Styling
├── data/                   # Data storage (auto-created)
│   └── config.json         # Application configuration
├── .github/
│   └── workflows/
│       └── docker.yml      # GitHub Actions Docker build
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Docker ignore patterns
├── requirements.txt        # Python dependencies
├── VERSION                 # Version information
├── start.sh                # Startup script
├── README.md               # Project overview
├── INSTALLATION.md         # Installation guide
├── DOCUMENTATION.md        # Complete documentation
└── PROJECT_PLAN.md         # This file
```

## Current Features (Version 1.0.0)

### Email Types
- **Phishing Emails**: Test emails with PhishTank URLs
- **EICAR Test Emails**: Standard antivirus test files
- **Cynic Test Emails**: Password-protected VBS archives
- **GTUBE Spam-Test Emails**: Single-message spam detector tests using canonical GTUBE string
- **Custom Emails**: Fully configurable emails with custom subject, body, display name, and optional attachments (.zip, .com, .scr, .pdf, .bat)

### Email Providers
- GMX (recommended, tested and verified)
- Gmail (requires app-specific password)
- Yahoo (requires app-specific password)
- iCloud
- Zoho
- Outlook.com
- Office365
- AOL

### Configuration Management
- Multiple email client configurations (save, edit, delete, switch)
- Current active configuration tracking
- Default recipients and email count settings
- Email sending history (last 100 entries)

### User Interface
- Dashboard with email sending options
- Configuration page with provider selection
- Detailed connection information display
- Email sending history view
- Test email configuration validation

### Docker Support
- Dockerfile for containerization
- Docker Compose for easy deployment
- GitHub Actions automated builds
- GitHub Container Registry integration

## Implementation Details

### Backend Components

1. **SMTP Client (`smtp_client.py`)**:
   - Python smtplib implementation
   - Support for multiple email providers
   - Configurable server, port, authentication (TLS/SSL)
   - Support for email attachments
   - Display name support for sender
   - Detailed error reporting

2. **Email Client (`email_client.py`)**:
   - IMAP client for reading emails
   - Support for SSL/TLS connections
   - Read inbox, folders, messages
   - Configurable through UI

3. **Email Generators**:
   - **Phishing Generator**: Integrates with PhishTank API
   - **EICAR Generator**: Creates standard antivirus test files
   - **Cynic Generator**: Generates password-protected VBS archives
   - **GTUBE Generator**: Creates spam-test emails with GTUBE string
   - **Custom Generator**: Fully configurable email generation

4. **Email Generator Coordinator (`email_generator.py`)**:
   - Orchestrates email generation and sending
   - Derives SMTP settings from email client configuration
   - Handles email sending with error tracking
   - Maintains email sending history
   - Provides detailed connection information

5. **Configuration Management (`config.py`)**:
   - JSON-based configuration storage
   - Multiple email client configurations
   - Current active configuration tracking
   - Email generation parameters
   - Email sending history
   - Auto-creates config file with defaults

6. **REST API (`api/routes.py`)**:
   - Configuration endpoints
   - Email client configuration management
   - Email sending endpoints (phishing, EICAR, Cynic, GTUBE, custom)
   - Test email configuration
   - History retrieval

### Frontend Components

1. **Dashboard (`index.html`)**:
   - Email sending interface for all email types
   - Email history display
   - Connection details modal
   - Status indicators

2. **Configuration Page (`config.html`)**:
   - Email provider selector with presets
   - Multiple configuration management
   - Test email configuration
   - Default recipients and count settings

## API Endpoints

### Configuration
- `GET /api/config` - Get all configuration
- `POST /api/config` - Update configuration
- `GET /api/email/config` - Get email client config (with optional name parameter)
- `POST /api/email/config` - Update email client config (requires config_name)
- `GET /api/email/configs` - Get all saved configurations
- `DELETE /api/email/config/<config_name>` - Delete a configuration
- `GET /api/email/config/current` - Get current active configuration name
- `POST /api/email/config/current` - Set current active configuration

### Email Operations
- `POST /api/test/email` - Test email configuration
- `POST /api/send/phishing` - Send phishing emails
- `POST /api/send/eicar` - Send EICAR test emails
- `POST /api/send/cynic` - Send Cynic test emails
- `POST /api/send/gtube` - Send GTUBE spam-test email
- `POST /api/send/custom` - Send custom emails
- `GET /api/history` - Get email sending history

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
- 7z command-line tool (optional, for Cynic test emails - py7zr used as fallback)

## Installation Methods

### Docker (Recommended)
- Pre-built images available from GitHub Container Registry
- Docker Compose for easy deployment
- Automated builds via GitHub Actions

### Manual Installation
- Python 3.8+ required
- Virtual environment recommended
- Install dependencies via pip

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

## Security Considerations

### Current Security Measures
- Passwords masked in API responses
- Configuration file excluded from git
- Non-root user in Docker containers
- File permissions for sensitive data

### Planned Security Enhancements

1. **Configuration Encryption** (Planned)
   - Encrypt password fields in configuration file
   - Use Fernet symmetric encryption
   - Key management via environment variable or key file
   - Automatic migration from plain text
   - Scope: Encrypt passwords only (not usernames)

2. **Credential Management** (Completed)
   - Removed hardcoded credentials from code
   - Git history cleaned using BFG Repo-Cleaner
   - Credentials stored only in local config file

## Future Enhancements

### High Priority
1. **Configuration Encryption**
   - Implement Fernet encryption for password fields
   - Add encryption key management
   - Update documentation

### Medium Priority
2. **Email Template Customization**
   - User-defined email templates
   - Template library
   - Template sharing

3. **Scheduled Email Sending**
   - Cron-like scheduling
   - Recurring email sends
   - Schedule management UI

4. **Email Statistics and Reporting**
   - Success/failure rates
   - Provider performance metrics
   - Historical trends

### Low Priority
5. **Email Search Functionality**
   - Search sent emails
   - Filter by type, date, status
   - Export capabilities

6. **Attachment Download Support**
   - Download sent attachments
   - Attachment library
   - Attachment preview

7. **Advanced Configuration Options**
   - Email rate limiting
   - Retry policies
   - Custom SMTP headers

## Development Server References

- **SSH Access**: `wsealey@192.168.1.177`
- **PhishTank Automation**: `~/phishtank-automation`
- **Cynic Test**: `~/cynictest`
- **Application Location**: `~/email-data-generation`

## Docker Deployment

### GitHub Container Registry
- **Image**: `ghcr.io/warrensealey/threatsampleproject:latest`
- **Version Tags**: `ghcr.io/warrensealey/threatsampleproject:1.0.0`
- **Automated Builds**: On push to main branch
- **Workflow**: `.github/workflows/docker.yml`

### Local Docker Usage
```bash
# Pull and run
docker pull ghcr.io/warrensealey/threatsampleproject:latest
docker run -p 5000:5000 -v $(pwd)/data:/app/data ghcr.io/warrensealey/threatsampleproject:latest

# Or use docker-compose
docker-compose up
```

## Version History

### Version 1.0.0 (Current)
- Initial release
- All email types implemented (Phishing, EICAR, Cynic, GTUBE, Custom)
- Multiple email provider support
- Multiple configuration management
- Docker containerization
- GitHub Actions automated builds
- Comprehensive documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See repository for license information.
