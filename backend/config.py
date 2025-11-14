"""
Configuration management for Email Data Generation project.
Stores SMTP settings, email client settings, and email generation parameters.
"""
import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "data" / "config.json"

DEFAULT_CONFIG = {
    "smtp": {
        "server": "",
        "port": 587,
        "username": "",
        "password": "",
        "use_tls": True,
        "use_ssl": False
    },
    "email_client": {
        "imap_server": "",
        "imap_port": 993,
        "username": "",
        "password": "",
        "use_ssl": True,
        "use_starttls": False,
        "smtp_server": "",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "smtp_use_ssl": False
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


def load_config():
    """Load configuration from JSON file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged = DEFAULT_CONFIG.copy()
                merged.update(config)
                return merged
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    else:
        # Create directory if it doesn't exist
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG.copy())
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save configuration to JSON file."""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving config: {e}")
        return False


def get_smtp_config():
    """Get SMTP configuration."""
    config = load_config()
    return config.get("smtp", {})


def get_email_client_config():
    """Get email client configuration."""
    config = load_config()
    return config.get("email_client", {})


def get_email_generation_config():
    """Get email generation configuration."""
    config = load_config()
    return config.get("email_generation", {})


def update_smtp_config(smtp_config):
    """Update SMTP configuration."""
    config = load_config()
    config["smtp"] = smtp_config
    return save_config(config)


def update_email_client_config(email_client_config):
    """Update email client configuration."""
    config = load_config()
    config["email_client"] = email_client_config
    return save_config(config)


def update_email_generation_config(email_gen_config):
    """Update email generation configuration."""
    config = load_config()
    config["email_generation"] = email_gen_config
    return save_config(config)


def add_history_entry(entry):
    """Add an entry to the email sending history."""
    config = load_config()
    if "history" not in config:
        config["history"] = []
    config["history"].insert(0, entry)
    # Keep only last 100 entries
    config["history"] = config["history"][:100]
    return save_config(config)


def get_history():
    """Get email sending history."""
    config = load_config()
    return config.get("history", [])

