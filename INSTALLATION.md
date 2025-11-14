# Installation Guide

This guide provides step-by-step instructions for installing and setting up the Email Data Generation application.

## Prerequisites

Before installing the application, ensure you have the following:

### Required Software

1. **Python 3.8 or higher**
   - Check your version: `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **pip** (Python package manager)
   - Usually included with Python
   - Verify: `pip3 --version`

3. **Git** (for cloning the repository)
   - Check: `git --version`
   - Download from: https://git-scm.com/downloads

### Optional Software

1. **7z command-line tool** (required for Cynic test email generation)
   - **macOS**: `brew install p7zip`
   - **Linux (Debian/Ubuntu)**: `sudo apt-get install p7zip-full`
   - **Linux (RHEL/CentOS)**: `sudo yum install p7zip`
   - **Windows**: Download from https://www.7-zip.org/

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/warrensealey/threatsampleproject.git
cd threatsampleproject
```

### 2. Create a Virtual Environment (Recommended)

Creating a virtual environment isolates the project dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

**Note**: If you encounter issues with `py7zr`, you can install the other dependencies separately:
```bash
pip install Flask==3.0.0 Flask-CORS==4.0.0 requests python-dotenv==1.0.0
```

The `py7zr` package is optional if you have the `7z` command-line tool installed.

### 4. Verify Installation

Check that Flask is installed correctly:

```bash
python3 -c "import flask; print(flask.__version__)"
```

You should see: `3.0.0`

## Running the Application

### Method 1: Using the Start Script

```bash
# Make the script executable (first time only)
chmod +x start.sh

# Run the application
./start.sh
```

### Method 2: Direct Python Execution

```bash
# Set PYTHONPATH and run
export PYTHONPATH=.:$PYTHONPATH
python3 backend/app.py
```

### Method 3: Using Python Module

```bash
# From project root
PYTHONPATH=. python3 -m backend.app
```

## Accessing the Application

Once the server is running, open your web browser and navigate to:

- **Dashboard**: http://localhost:5000
- **Configuration**: http://localhost:5000/config

The application will be accessible on:
- **Local machine**: http://localhost:5000
- **Network access**: http://YOUR_IP_ADDRESS:5000 (if firewall allows)

## Initial Configuration

1. Open the Configuration page: http://localhost:5000/config

2. **Configure Email Provider Settings**:
   - Select your email provider from the dropdown (GMX, Gmail, Yahoo, iCloud, Zoho, Outlook.com, etc.)
   - The form will auto-populate with the correct server settings
   - Enter your email username and password
   - Verify IMAP and SMTP settings are correct

3. **Configure Email Generation Defaults**:
   - Set default recipient email addresses (comma-separated)
   - Set default email count

4. **Test Your Configuration**:
   - Click "Test Email Configuration" button
   - Enter a test recipient email address
   - Verify the connection details and test email delivery

## Troubleshooting

### Port Already in Use

If port 5000 is already in use:

```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process or change the port in backend/app.py
```

### Module Not Found Errors

If you see `ModuleNotFoundError: No module named 'backend'`:

```bash
# Make sure PYTHONPATH is set
export PYTHONPATH=.:$PYTHONPATH

# Or run from project root directory
cd /path/to/threatsampleproject
python3 backend/app.py
```

### Dependencies Installation Issues

If `pip install -r requirements.txt` fails:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install packages individually
pip install Flask==3.0.0
pip install Flask-CORS==4.0.0
pip install requests
pip install python-dotenv==1.0.0
```

### SSL/TLS Connection Errors

If you encounter SSL/TLS errors when sending emails:

1. Verify your email provider's SMTP settings
2. Check that the correct port is used (587 for TLS, 465 for SSL)
3. Ensure "Use TLS" or "Use SSL" is correctly configured
4. Some providers require app-specific passwords instead of regular passwords

## Production Deployment

For production deployment:

1. **Use a production WSGI server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
   ```

2. **Set up a reverse proxy** (e.g., Nginx) for HTTPS

3. **Configure firewall rules** to allow traffic on port 5000

4. **Set up process management** (e.g., systemd, supervisor) for auto-restart

5. **Configure logging** to a dedicated log directory

## Development Server Setup

For deployment to a development server:

1. **SSH to the server**:
   ```bash
   ssh user@server-ip
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/warrensealey/threatsampleproject.git
   cd threatsampleproject
   ```

3. **Install dependencies**:
   ```bash
   pip3 install --user -r requirements.txt
   ```

4. **Run in background**:
   ```bash
   nohup python3 backend/app.py > /tmp/flask_server.log 2>&1 &
   ```

5. **Verify it's running**:
   ```bash
   curl http://localhost:5000
   ```

## Next Steps

After installation, see:
- [README.md](README.md) for project overview and usage
- [DOCUMENTATION.md](DOCUMENTATION.md) for detailed API and feature documentation

