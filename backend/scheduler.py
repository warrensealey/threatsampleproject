"""
Background scheduler for running scheduled email jobs.

This module evaluates the schedules stored in the central config and
invokes the existing EmailGenerator flows when jobs become due.

It is designed to run inside the Docker container as a lightweight
in-process scheduler. A simple file lock is used so that, under
Gunicorn, only ONE worker process will actually execute the loop.
"""

import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import fcntl
from zoneinfo import ZoneInfo

from backend.config import (
    get_schedules,
    upsert_schedule,
    delete_schedule,
    get_timezone,
    get_current_email_client_name,
    set_current_email_client,
)
from backend.email_generator import EmailGenerator

logger = logging.getLogger(__name__)

_scheduler_thread: Optional[threading.Thread] = None
_scheduler_started = False

LOCK_FILE = Path(__file__).parent.parent / "data" / ".scheduler.lock"
SCHEDULER_INTERVAL_SECONDS = 30


def _parse_iso_utc(value: Optional[str]) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            # Assume UTC if naive
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _format_iso_utc(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _compute_next_run(schedule: Dict[str, Any], now_utc: datetime) -> Optional[datetime]:
    """Compute the next run time in UTC for a schedule after a successful run.

    Returns None for one-off schedules which should not run again.
    """
    schedule_type = schedule.get("schedule_type", "one_off")

    if schedule_type == "one_off":
        # One-off schedules do not repeat; caller should disable them.
        return None

    if schedule_type == "interval":
        hours = schedule.get("interval_hours") or 24
        try:
            hours = float(hours)
        except (TypeError, ValueError):
            hours = 24
        return now_utc + timedelta(hours=hours)

    if schedule_type == "weekly":
        weekly_days = schedule.get("weekly_days") or []
        if not isinstance(weekly_days, list):
            weekly_days = []
        weekly_days = [str(d).upper() for d in weekly_days]
        time_str = schedule.get("time_of_day_local") or "09:00"

        tz = ZoneInfo(get_timezone())
        now_local = now_utc.astimezone(tz)

        try:
            hour, minute = [int(p) for p in time_str.split(":", 1)]
        except Exception:
            hour, minute = 9, 0

        # Map Python weekday (0=Mon) to our labels
        weekday_labels = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

        for offset in range(0, 8):
            candidate_local = now_local + timedelta(days=offset)
            label = weekday_labels[candidate_local.weekday()]
            if label not in weekly_days:
                continue
            candidate_local = candidate_local.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            if candidate_local <= now_local:
                # For today, ensure time is in the future
                continue
            return candidate_local.astimezone(timezone.utc)

        # If nothing matched (e.g. misconfiguration), fall back to 7 days from now
        return now_utc + timedelta(days=7)

    # Unknown type – do not reschedule.
    return None


def _run_scheduled_job(email_generator: EmailGenerator, schedule: Dict[str, Any]) -> None:
    """Execute a single scheduled job and update its metadata."""
    schedule_id = schedule.get("id", "<unknown>")
    email_type = schedule.get("email_type", "phishing")
    recipients = schedule.get("recipients") or []
    count = schedule.get("count") or 1

    if not recipients:
        logger.warning("Schedule %s has no recipients, skipping", schedule_id)
        # Mark as failed but still compute next run to avoid tight loops
        schedule["last_status"] = "error"
        schedule["last_error"] = "No recipients configured"
        schedule["last_run_utc"] = _format_iso_utc(datetime.now(timezone.utc))
        schedule["failure_count"] = int(schedule.get("failure_count") or 0) + 1
        upsert_schedule(schedule)
        return

    logger.info(
        "Running scheduled job %s: type=%s, recipients=%s, count=%s",
        schedule_id,
        email_type,
        recipients,
        count,
    )

    # Optionally bind to a specific email client configuration
    target_config = schedule.get("config_name")
    previous_config = get_current_email_client_name()
    if target_config and target_config != previous_config:
        set_current_email_client(target_config)

    now_utc = datetime.now(timezone.utc)
    success = False
    error_message = None

    try:
        if email_type == "phishing":
            template_type = schedule.get("template_type", "warning")
            result = email_generator.send_phishing_emails(
                count=count, recipients=recipients, template_type=template_type
            )
        elif email_type == "eicar":
            result = email_generator.send_eicar_emails(count=count, recipients=recipients)
        elif email_type == "cynic":
            result = email_generator.send_cynic_emails(count=count, recipients=recipients)
        elif email_type == "gtube":
            result = email_generator.send_gtube_emails(count=count, recipients=recipients)
        elif email_type == "custom":
            result = email_generator.send_custom_emails(
                count=count,
                recipients=recipients,
                subject=schedule.get("subject"),
                body=schedule.get("body"),
                display_name=schedule.get("display_name"),
                attachment_type=schedule.get("attachment_type"),
            )
        else:
            raise ValueError(f"Unsupported email_type for schedule: {email_type}")

        success = bool(result.get("success"))
        if not success:
            error_message = result.get("error") or "Send operation reported failure"
    except Exception as exc:
        logger.exception("Error while running scheduled job %s: %s", schedule_id, exc)
        success = False
        error_message = str(exc)
    finally:
        # Restore previous email client configuration if it changed
        if previous_config and previous_config != target_config:
            set_current_email_client(previous_config)

    # Update schedule metadata
    schedule["last_run_utc"] = _format_iso_utc(now_utc)
    if success:
        schedule["last_status"] = "success"
        schedule["failure_count"] = 0
        next_run = _compute_next_run(schedule, now_utc)
        if next_run is None:
            # One-off completed – disable further runs
            schedule["enabled"] = False
            schedule["next_run_utc"] = None
        else:
            schedule["next_run_utc"] = _format_iso_utc(next_run)
        logger.info("Scheduled job %s completed successfully", schedule_id)
    else:
        schedule["last_status"] = "error"
        schedule["last_error"] = error_message or "Unknown scheduling error"
        failures = int(schedule.get("failure_count") or 0) + 1
        schedule["failure_count"] = failures
        logger.warning(
            "Scheduled job %s failed (failure_count=%s): %s",
            schedule_id,
            failures,
            error_message,
        )
        # If a schedule fails repeatedly, automatically disable it
        if failures >= 3:
            schedule["enabled"] = False
            logger.error(
                "Schedule %s disabled after %s consecutive failures",
                schedule_id,
                failures,
            )

    upsert_schedule(schedule)


def run_due_schedules() -> None:
    """Evaluate all schedules and run any that are due."""
    schedules = get_schedules()
    if not schedules:
        return

    now_utc = datetime.now(timezone.utc)
    email_generator = EmailGenerator()

    for schedule in schedules:
        if not isinstance(schedule, dict):
            continue
        if not schedule.get("enabled", True):
            continue

        next_run_utc_str = schedule.get("next_run_utc")
        next_run_utc = _parse_iso_utc(next_run_utc_str)
        if next_run_utc is None:
            # If next_run is missing for repeating schedules, compute from now
            if schedule.get("schedule_type") in ("interval", "weekly"):
                next_run = _compute_next_run(schedule, now_utc)
                if next_run is not None:
                    schedule["next_run_utc"] = _format_iso_utc(next_run)
                    upsert_schedule(schedule)
            continue

        if next_run_utc <= now_utc:
            _run_scheduled_job(email_generator, schedule)


def _scheduler_loop() -> None:
    """Main loop that acquires a file lock and periodically runs due jobs."""
    logger.info("Scheduler thread starting")
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOCK_FILE, "w") as lock_fp:
        try:
            fcntl.flock(lock_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            # Another process holds the lock; do not start a second scheduler.
            logger.info("Another scheduler instance is already running; exiting thread")
            return

        logger.info("Scheduler acquired lock; entering run loop")
        while True:
            try:
                run_due_schedules()
            except Exception as exc:
                logger.exception("Error in scheduler loop: %s", exc)
            time.sleep(SCHEDULER_INTERVAL_SECONDS)


def start_scheduler() -> None:
    """Start the background scheduler thread (idempotent)."""
    global _scheduler_thread, _scheduler_started
    if _scheduler_started and _scheduler_thread and _scheduler_thread.is_alive():
        return

    _scheduler_started = True
    _scheduler_thread = threading.Thread(
        target=_scheduler_loop, name="email-scheduler", daemon=True
    )
    _scheduler_thread.start()
    logger.info("Scheduler thread started")


