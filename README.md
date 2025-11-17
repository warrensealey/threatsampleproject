# Email Data Generation Project

**Version 1.0.0**

Full-stack Python web application for generating and sending test emails (phishing, EICAR malware, Cynic test emails, GTUBE spam-test messages, and custom emails) through SMTP, with a web-based configuration interface supporting multiple email providers.

## Features

- **Multi-Provider Support**: GMX, Gmail, Yahoo, iCloud, Zoho, Outlook.com, AOL, Office365
- **Test Email Generation**: Create and send phishing, EICAR, Cynic, GTUBE, and custom test emails
- **GTUBE Spam Test**: Fire a single spam-test message containing the canonical GTUBE string ([spec](https://en.wikipedia.org/wiki/GTUBE)) to validate anti-spam controls
- **Custom Emails**: Fully configurable emails with custom subject, body, display name, and optional attachments
- **Multiple Email Configurations**: Save and manage multiple email client configurations (GMX, Gmail, Yahoo, etc.)
- **SMTP Integration**: Send emails through configured SMTP servers
- **Web Interface**: Full configuration and management through HTML/JavaScript frontend
- **Connection Details**: Detailed connection information for troubleshooting
- **Email History**: Track all sent emails with timestamps and status

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/warrensealey/threatsampleproject.git
cd threatsampleproject

# Install dependencies
pip install -r requirements.txt

# Run the application
./start.sh
```

Or see [INSTALLATION.md](INSTALLATION.md) for detailed installation instructions.

### Access the Application

- **Dashboard**: http://localhost:5000
- **Configuration**: http://localhost:5000/config

## Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation and setup guide
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete API reference and usage documentation
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Implementation plan and architecture details

## Supported Email Providers

> **Note**: GMX server settings are known to work and have been tested. All other hosted mail provider settings are still in development and may require additional configuration or troubleshooting.

| Provider | IMAP | SMTP | Port | Encryption |
|----------|------|------|------|------------|
| GMX | imap.gmx.com | mail.gmx.com | 587 | TLS |
| Gmail | imap.gmail.com | smtp.gmail.com | 587 | TLS |
| Yahoo | imap.mail.yahoo.com | smtp.mail.yahoo.com | 587 | TLS |
| iCloud | imap.mail.me.com | smtp.mail.me.com | 587 | TLS |
| Zoho | imap.zoho.com | smtp.zoho.com | 587 | TLS |
| Outlook.com | imap-mail.outlook.com | smtp-mail.outlook.com | 587 | TLS |
| Office365 | outlook.office365.com | smtp.office365.com | 587 | TLS |
| AOL | imap.aol.com | smtp.aol.com | 465 | SSL |

> **Gmail-specific notes**
> - Gmail requires an **app-specific password** (generate it under Google Account → Security) for IMAP/SMTP access; regular passwords are rejected when 2FA or advanced security is enabled.
> - With the app password configured, Gmail can successfully send phishing URL tests and GTUBE spam-test emails. Google currently blocks the EICAR and Cynic payloads at send time, so those templates will fail when routed through Gmail.

> **Yahoo-specific notes**
> - Yahoo requires an **app-specific password** (generate it under Yahoo Account → Account Security → Generate app password) for IMAP/SMTP access; regular passwords will cause "Connection unexpectedly closed" errors when 2FA or modern account security is enabled.
> - With the app password configured, Yahoo can successfully send phishing URL tests and GTUBE spam-test emails. Yahoo may block EICAR and Cynic payloads similar to Gmail, so those templates may fail when routed through Yahoo.

## Usage

### Sending Test Emails

1. Navigate to the Dashboard
2. Select the type of test email:
   - **Phishing Emails**: Test emails with PhishTank URLs
   - **EICAR Test Emails**: Standard antivirus test files
   - **Cynic Test Emails**: Password-protected VBS archives
   - **GTUBE Spam Test**: Single-message spam detector test using the GTUBE string `XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X`
   - **Custom Email**: Fully configurable emails with custom subject, body, display name, and optional attachments (.zip, .com, .scr, .pdf, .bat)
3. Enter recipient addresses and count (for custom emails, fill in the form fields)
4. Review connection details in the results modal

### Configuration

> **⚠️ STRONGLY RECOMMENDED: Use a GMX email account** - GMX settings have been tested and verified to work. Other providers are still in development.

1. Go to the Configuration page
2. **Select GMX** from the email provider dropdown (pre-selected by default)
3. Enter your GMX email address and password
4. Test the configuration using the "Test Email Configuration" button

**To create a free GMX account**: Visit https://www.gmx.com/ and sign up for a free account.

## Project Structure

```
threatsampleproject/
├── backend/          # Python Flask backend
│   ├── api/          # REST API routes
│   ├── generators/   # Email generators
│   └── *.py         # Core modules
├── frontend/         # Web frontend
│   ├── *.html       # Pages
│   ├── css/         # Stylesheets
│   └── js/          # JavaScript
├── data/            # Configuration (auto-created)
├── VERSION          # Version information
├── requirements.txt # Dependencies
├── start.sh         # Startup script
├── README.md        # Project overview
├── INSTALLATION.md  # Installation guide
└── DOCUMENTATION.md # Complete documentation
```

## Requirements

- Python 3.8+
- Flask 3.0.0
- 7z command-line tool (optional, for Cynic emails)

## Version

Current version: **1.0.0**

See `VERSION` file for version information.

## Contributing

```bash
git add .
git commit -m "Your commit message"
git push -u origin main
```

## Repository

GitHub: https://github.com/warrensealey/threatsampleproject

## License

See repository for license information.

