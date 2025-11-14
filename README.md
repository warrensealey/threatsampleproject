# Email Data Generation Project

Full-stack Python web application for generating and sending test emails (phishing, EICAR malware, and Cynic test emails) through Symantec Email Security Cloud via SMTP, with a web-based configuration interface and email client functionality.

## Project Overview

This project provides:
- **Test Email Generation**: Create and send phishing, EICAR, and Cynic test emails
- **SMTP Integration**: Send emails through Symantec Email Security Cloud
- **Email Client**: Connect to web-based email accounts (IMAP) for reading emails
- **Web Interface**: Full configuration and management through HTML/JavaScript frontend

## Project Structure

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed implementation plan.

## Development Server References

- **SSH Access**: `wsealey@192.168.1.177`
- **PhishTank Automation**: `~/phishtank-automation`
- **Cynic Test**: `~/cynictest`
- **Mutt Config**: `~/.muttrc`

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/warrensealey/threatsampleproject.git
cd threatsampleproject
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure you have the `7z` command-line tool installed (for Cynic test email generation):
   - macOS: `brew install p7zip`
   - Linux: `sudo apt-get install p7zip-full` or `sudo yum install p7zip`
   - Windows: Download from https://www.7-zip.org/

### Configuration

1. Start the application:
```bash
python backend/app.py
```

2. Open your browser and navigate to:
   - Dashboard: http://localhost:5000
   - Configuration: http://localhost:5000/config
   - Email Client: http://localhost:5000/email

3. Configure the application:
   - Go to the Configuration page
   - Enter your SMTP settings (Symantec Email Security Cloud)
   - Enter your email client settings (IMAP for reading emails)
   - Set default email generation parameters

### Usage

#### Sending Test Emails

1. Go to the Dashboard
2. Click on the type of test email you want to send:
   - **Phishing Emails**: Generates emails with PhishTank URLs
   - **EICAR Test Emails**: Sends EICAR test file attachments
   - **Cynic Test Emails**: Sends password-protected VBS archives
3. Enter the number of emails and recipient addresses when prompted

#### Reading Emails

1. Go to the Email Client page
2. Ensure your email client is configured in the Configuration page
3. Select a folder from the left panel
4. Click on messages to view them in the right panel

### Project Structure

The project follows the structure defined in [PROJECT_PLAN.md](PROJECT_PLAN.md):
- `backend/` - Python backend application
- `frontend/` - HTML/JavaScript frontend
- `data/` - Configuration and log files (created automatically)
- `templates/` - Email templates (for future use)

## Contributing

To push code to this repository:

```bash
git add .
git commit -m "Your commit message"
git push -u origin main
```

## Repository

GitHub: https://github.com/warrensealey/threatsampleproject

