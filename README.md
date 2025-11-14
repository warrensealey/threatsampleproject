# Email Data Generation Project

Full-stack Python web application for generating and sending test emails (phishing, EICAR malware, and Cynic test emails) through SMTP, with a web-based configuration interface supporting multiple email providers.

## Features

- **Multi-Provider Support**: GMX, Gmail, Yahoo, iCloud, Zoho, Outlook.com, AOL, Office365
- **Test Email Generation**: Create and send phishing, EICAR, and Cynic test emails
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

## Usage

### Sending Test Emails

1. Navigate to the Dashboard
2. Select the type of test email:
   - **Phishing Emails**: Test emails with PhishTank URLs
   - **EICAR Test Emails**: Standard antivirus test files
   - **Cynic Test Emails**: Password-protected VBS archives
3. Enter recipient addresses and count
4. Review connection details in the results modal

### Configuration

1. Go to the Configuration page
2. Select your email provider from the dropdown
3. Enter your email credentials
4. Test the configuration using the "Test Email Configuration" button

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
└── requirements.txt # Dependencies
```

## Requirements

- Python 3.8+
- Flask 3.0.0
- 7z command-line tool (optional, for Cynic emails)

## Contributing

```bash
git add .
git commit -m "Your commit message"
git push -u origin main
```

## Repository

GitHub: https://github.com/warrensealey/threatsampleproject

