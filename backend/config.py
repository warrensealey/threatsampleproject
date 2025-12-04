"""
Configuration management for Email Data Generation project.
Stores SMTP settings, email client settings, and email generation parameters.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from backend.encryption import encrypt_value, decrypt_value, is_encrypted

CONFIG_FILE = Path(__file__).parent.parent / "data" / "config.json"

# Default configuration structure for the application.
DEFAULT_CONFIG: Dict[str, Any] = {
    "smtp": {
        "server": "",
        "port": 587,
        "username": "",
        "password": "",
        "use_tls": True,
        "use_ssl": False,
    },
    "email_clients": {},
    "current_email_client": None,
    "email_generation": {
        "default_recipients": [],
        "default_count": 1,
        "subject_templates": {
            "phishing": "Warning - Potentially Hazardous URL",
            "eicar": "EICAR Test File",
            "cynic": "This is a important top secret email!",
            "gtube": "GTUBE Spam Test Email",
        },
    },
    # Named email templates grouped by type, e.g.:
    # "templates": {
    #   "custom": {
    #       "My Template": { "subject": "...", "body": "...", ... }
    #   }
    # }
    "templates": {},
    # App-wide local timezone identifier for scheduled jobs and display.
    # All canonical timestamps are stored in UTC; this is used for
    # converting to/from local time when presenting to users.
    "timezone": "Europe/London",
    # List of scheduled send definitions. Each item is a dict with at least:
    #   id, name, enabled, email_type, recipients, count, schedule_type,
    #   next_run_utc, config_name
    # and optionally:
    #   interval_hours, weekly_days, time_of_day_local, created_at, history, etc.
    "schedules": [],
    "history": [],
}


def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)

                # Migration: Convert old single email_client to new structure
                if "email_client" in config and "email_clients" not in config:
                    old_client = config.get("email_client", {})
                    if old_client and any(old_client.values()):  # Only migrate if not empty
                        config["email_clients"] = {"default": old_client}
                        config["current_email_client"] = "default"
                    else:
                        config["email_clients"] = {}
                        config["current_email_client"] = None
                    # Remove old email_client key
                    if "email_client" in config:
                        del config["email_client"]

                # Ensure email_clients exists
                if "email_clients" not in config:
                    config["email_clients"] = {}

                # Ensure current_email_client exists
                if "current_email_client" not in config:
                    config["current_email_client"] = None

                # Ensure templates exists
                if "templates" not in config:
                    config["templates"] = {}

                # Ensure timezone exists
                if "timezone" not in config or not isinstance(
                    config.get("timezone"), str
                ):
                    config["timezone"] = DEFAULT_CONFIG["timezone"]

                # Ensure schedules exists and is a list
                schedules = config.get("schedules")
                if not isinstance(schedules, list):
                    schedules = []
                # Normalise basic schedule structure and ensure IDs
                normalised_schedules: List[Dict[str, Any]] = []
                for item in schedules:
                    if not isinstance(item, dict):
                        continue
                    sched = item.copy()
                    if not sched.get("id"):
                        sched["id"] = str(uuid.uuid4())
                    # Basic required keys with sane defaults
                    sched.setdefault("enabled", True)
                    sched.setdefault("email_type", "phishing")
                    sched.setdefault("recipients", [])
                    sched.setdefault("count", 1)
                    sched.setdefault("schedule_type", "one_off")
                    normalised_schedules.append(sched)
                config["schedules"] = normalised_schedules

                # Decrypt password fields (backward compatible with plain text)
                smtp_cfg = config.get("smtp") or {}
                pwd = smtp_cfg.get("password")
                if is_encrypted(pwd):
                    smtp_cfg["password"] = decrypt_value(pwd)
                    config["smtp"] = smtp_cfg

                email_clients = config.get("email_clients") or {}
                for name, client_cfg in email_clients.items():
                    if not isinstance(client_cfg, dict):
                        continue
                    c_pwd = client_cfg.get("password")
                    if is_encrypted(c_pwd):
                        client_cfg["password"] = decrypt_value(c_pwd)
                config["email_clients"] = email_clients

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


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to JSON file."""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        # Work on a deep copy so callers keep decrypted values in memory
        to_save = json.loads(json.dumps(config))

        # Encrypt SMTP password if present
        smtp_cfg = to_save.get("smtp") or {}
        pwd = smtp_cfg.get("password")
        if isinstance(pwd, str) and pwd and not is_encrypted(pwd):
            smtp_cfg["password"] = encrypt_value(pwd)
            to_save["smtp"] = smtp_cfg

        # Encrypt email client passwords if present
        email_clients = to_save.get("email_clients") or {}
        for name, client_cfg in email_clients.items():
            if not isinstance(client_cfg, dict):
                continue
            c_pwd = client_cfg.get("password")
            if isinstance(c_pwd, str) and c_pwd and not is_encrypted(c_pwd):
                client_cfg["password"] = encrypt_value(c_pwd)
        to_save["email_clients"] = email_clients

        with open(CONFIG_FILE, 'w') as f:
            json.dump(to_save, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving config: {e}")
        return False


def get_smtp_config() -> Dict[str, Any]:
    """Get SMTP configuration."""
    config = load_config()
    return config.get("smtp", {})


def get_email_client_config(config_name: Optional[str] = None) -> Dict[str, Any]:
    """Get email client configuration.

    Args:
        config_name: Name of the config to retrieve. If None, returns current active config.

    Returns:
        Dictionary with email client configuration, or empty dict if not found.
    """
    config = load_config()
    email_clients = config.get("email_clients", {})

    if config_name is None:
        config_name = config.get("current_email_client")

    if config_name and config_name in email_clients:
        return email_clients[config_name].copy()

    return {}


def get_email_generation_config() -> Dict[str, Any]:
    """Get email generation configuration."""
    config = load_config()
    return config.get("email_generation", {})


def get_templates(template_type: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Get stored email templates.

    Args:
        template_type: Optional template type (e.g. \"custom\", \"phishing\").
                       If None, returns all templates grouped by type.

    Returns:
        Dict of templates. For a specific type, returns a mapping of
        template_name -> template_data. For all, returns a mapping of
        type -> {name -> data}.
    """
    config = load_config()
    templates = config.get("templates") or {}
    if template_type:
        return (templates.get(template_type) or {}).copy()
    # Shallow copy per type to avoid accidental mutation
    return {t_type: (t_map or {}).copy() for t_type, t_map in templates.items()}


def save_template(template_type: str, name: str, template_data: Dict[str, Any]) -> bool:
    """Save or update a named template for a given type.

    Args:
        template_type: e.g. \"custom\", \"phishing\".
        name: Human-friendly template name (key).
        template_data: Dict of template fields.
    """
    if not template_type or not name:
        return False

    config = load_config()
    templates = config.get("templates") or {}
    if not isinstance(templates, dict):
        templates = {}

    if template_type not in templates or not isinstance(templates.get(template_type), dict):
        templates[template_type] = {}

    templates[template_type][name] = template_data or {}
    config["templates"] = templates
    return save_config(config)


def delete_template(template_type: str, name: str) -> bool:
    """Delete a named template.

    Args:
        template_type: Template type (e.g. \"custom\").
        name: Template name.

    Returns:
        bool: True if deleted, False if not found.
    """
    if not template_type or not name:
        return False

    config = load_config()
    templates = config.get("templates") or {}
    type_map = templates.get(template_type)

    if not isinstance(type_map, dict) or name not in type_map:
        return False

    del type_map[name]
    if not type_map:
        # Remove empty type bucket
        del templates[template_type]

    config["templates"] = templates
    return save_config(config)


def update_smtp_config(smtp_config: Dict[str, Any]) -> bool:
    """Update SMTP configuration."""
    config = load_config()
    config["smtp"] = smtp_config
    return save_config(config)


def update_email_client_config(
    email_client_config: Dict[str, Any], config_name: Optional[str] = None
) -> bool:
    """Update email client configuration.

    Args:
        email_client_config: Configuration data to save
        config_name: Name of the config to update. If None, uses current_email_client.
                    If current_email_client is None, creates "default" config.

    Returns:
        bool: True if saved successfully
    """
    config = load_config()

    if "email_clients" not in config:
        config["email_clients"] = {}

    if config_name is None:
        config_name = config.get("current_email_client")
        if config_name is None:
            config_name = "default"
            config["current_email_client"] = "default"

    config["email_clients"][config_name] = email_client_config
    return save_config(config)


def get_all_email_client_configs() -> Dict[str, Dict[str, Any]]:
    """Get all email client configurations (without passwords).

    Returns:
        Dictionary mapping config names to config data (passwords masked)
    """
    config = load_config()
    email_clients = config.get("email_clients", {})

    result = {}
    for name, client_config in email_clients.items():
        safe_config = client_config.copy()
        if 'password' in safe_config:
            safe_config['password'] = '***' if safe_config['password'] else ''
        result[name] = safe_config

    return result


def save_email_client_config(
    config_name: str, email_client_config: Dict[str, Any]
) -> bool:
    """Save a named email client configuration.

    Args:
        config_name: Name/ID for this configuration
        email_client_config: Configuration data to save

    Returns:
        bool: True if saved successfully
    """
    config = load_config()

    if "email_clients" not in config:
        config["email_clients"] = {}

    config["email_clients"][config_name] = email_client_config

    # If this is the first config, set it as current
    if config.get("current_email_client") is None:
        config["current_email_client"] = config_name

    return save_config(config)


def delete_email_client_config(config_name: str) -> bool:
    """Delete an email client configuration.

    Args:
        config_name: Name of the config to delete

    Returns:
        bool: True if deleted successfully, False if config not found
    """
    config = load_config()
    email_clients = config.get("email_clients", {})

    if config_name not in email_clients:
        return False

    del email_clients[config_name]

    # If deleted config was current, set current to None or first available
    if config.get("current_email_client") == config_name:
        if email_clients:
            config["current_email_client"] = list(email_clients.keys())[0]
        else:
            config["current_email_client"] = None

    return save_config(config)


def set_current_email_client(config_name: str) -> bool:
    """Set the current active email client configuration.

    Args:
        config_name: Name of the config to set as active

    Returns:
        bool: True if set successfully, False if config not found
    """
    config = load_config()
    email_clients = config.get("email_clients", {})

    if config_name not in email_clients:
        return False

    config["current_email_client"] = config_name
    return save_config(config)


def get_current_email_client_name() -> Optional[str]:
    """Get the name of the current active email client configuration.

    Returns:
        str: Name of current config, or None if no config is active
    """
    config = load_config()
    return config.get("current_email_client")


def update_email_generation_config(email_gen_config: Dict[str, Any]) -> bool:
    """Update email generation configuration."""
    config = load_config()
    config["email_generation"] = email_gen_config
    return save_config(config)


def add_history_entry(entry: Dict[str, Any]) -> bool:
    """Add an entry to the email sending history."""
    config = load_config()
    if "history" not in config:
        config["history"] = []
    config["history"].insert(0, entry)
    # Keep only last 100 entries
    config["history"] = config["history"][:100]
    return save_config(config)


def get_history() -> List[Dict[str, Any]]:
    """Get email sending history."""
    config = load_config()
    return config.get("history", [])


# ---------------------------------------------------------------------------
# Schedule helpers
# ---------------------------------------------------------------------------

def get_timezone() -> str:
    """Return the configured application timezone identifier."""
    config = load_config()
    tz = config.get("timezone")
    if isinstance(tz, str) and tz:
        return tz
    return DEFAULT_CONFIG["timezone"]


def set_timezone(tz: str) -> bool:
    """Update the application timezone identifier."""
    if not isinstance(tz, str) or not tz:
        return False
    config = load_config()
    config["timezone"] = tz
    return save_config(config)


def get_schedules() -> List[Dict[str, Any]]:
    """Return the list of configured schedules."""
    config = load_config()
    schedules = config.get("schedules") or []
    if not isinstance(schedules, list):
        return []
    # Return shallow copies so callers don't accidentally mutate in-memory config
    return [s.copy() for s in schedules if isinstance(s, dict)]


def _find_schedule_index(schedules: List[Dict[str, Any]], schedule_id: str) -> int:
    for idx, sched in enumerate(schedules):
        if not isinstance(sched, dict):
            continue
        if sched.get("id") == schedule_id:
            return idx
    return -1


def upsert_schedule(schedule: Dict[str, Any]) -> Dict[str, Any]:
    """Create or update a schedule.

    If schedule['id'] is missing, a new schedule is created.
    Returns the stored schedule (with id).
    """
    if not isinstance(schedule, dict):
        raise ValueError("schedule must be a dict")

    config = load_config()
    schedules = config.get("schedules")
    if not isinstance(schedules, list):
        schedules = []

    sched = schedule.copy()
    if not sched.get("id"):
        sched["id"] = str(uuid.uuid4())

    # Ensure some required keys exist to keep data shape predictable
    sched.setdefault("enabled", True)
    sched.setdefault("email_type", "phishing")
    sched.setdefault("recipients", [])
    sched.setdefault("count", 1)
    sched.setdefault("schedule_type", "one_off")

    idx = _find_schedule_index(schedules, sched["id"])
    if idx >= 0:
        schedules[idx] = sched
    else:
        schedules.append(sched)

    config["schedules"] = schedules
    save_config(config)
    return sched


def delete_schedule(schedule_id: str) -> bool:
    """Delete a schedule by id."""
    if not schedule_id:
        return False
    config = load_config()
    schedules = config.get("schedules")
    if not isinstance(schedules, list):
        return False
    idx = _find_schedule_index(schedules, schedule_id)
    if idx < 0:
        return False
    del schedules[idx]
    config["schedules"] = schedules
    return save_config(config)


def set_schedule_enabled(schedule_id: str, enabled: bool) -> bool:
    """Enable or disable a schedule by id."""
    if not schedule_id:
        return False
    config = load_config()
    schedules = config.get("schedules")
    if not isinstance(schedules, list):
        return False
    idx = _find_schedule_index(schedules, schedule_id)
    if idx < 0:
        return False
    sched = schedules[idx]
    if not isinstance(sched, dict):
        return False
    sched["enabled"] = bool(enabled)
    schedules[idx] = sched
    config["schedules"] = schedules
    return save_config(config)

