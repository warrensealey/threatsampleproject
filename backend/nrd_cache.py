"""
Cache and cursor management for newly registered domain (NRD) lists.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

import requests

from backend.config import load_config, save_config

logger = logging.getLogger(__name__)

NRD_CSV_URL = (
    "https://raw.githubusercontent.com/shreshta-labs/newly-registered-domains/main/nrd-1w.csv"
)
NRD_CACHE_HOURS = 24
NRD_CSV_FILE = Path(__file__).resolve().parent.parent / "data" / "nrd-1w.csv"


class InsufficientDomainsError(Exception):
    """Raised when fewer domains remain than requested."""

    def __init__(self, requested: int, remaining: int):
        self.requested = requested
        self.remaining = remaining
        super().__init__(
            f"Only {remaining} domain(s) left in the current cached list; "
            f"{requested} requested."
        )


class NRDDownloadError(Exception):
    """Raised when the remote NRD list cannot be downloaded."""


def parse_domains_from_text(content: str) -> List[str]:
    """Parse one domain per line, skipping blanks."""
    domains: List[str] = []
    for line in content.splitlines():
        domain = line.strip()
        if domain:
            domains.append(domain)
    return domains


def build_nrd_url(domain: str) -> str:
    """Build test URL for a newly registered domain."""
    return f"https://www.{domain.strip()}"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_utc_timestamp(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def get_nrd_state() -> dict:
    """Return NRD cache metadata from config."""
    config = load_config()
    nrd = config.get("nrd") or {}
    return {
        "last_download_utc": nrd.get("last_download_utc"),
        "next_index": int(nrd.get("next_index", 0)),
    }


def save_nrd_state(
    last_download_utc: Optional[str] = None,
    next_index: Optional[int] = None,
) -> None:
    """Persist NRD cache metadata to config."""
    config = load_config()
    nrd = dict(config.get("nrd") or {})
    if last_download_utc is not None:
        nrd["last_download_utc"] = last_download_utc
    if next_index is not None:
        nrd["next_index"] = int(next_index)
    config["nrd"] = nrd
    save_config(config)


def cache_is_expired(
    last_download_utc: Optional[str], now: Optional[datetime] = None
) -> bool:
    """Return True if cache is missing or older than NRD_CACHE_HOURS."""
    if not last_download_utc or not NRD_CSV_FILE.exists():
        return True
    downloaded_at = _parse_utc_timestamp(last_download_utc)
    if downloaded_at is None:
        return True
    current = now or _utc_now()
    return current - downloaded_at >= timedelta(hours=NRD_CACHE_HOURS)


def download_nrd_list(csv_path: Optional[Path] = None) -> List[str]:
    """Download the NRD CSV and persist it locally."""
    target = csv_path or NRD_CSV_FILE
    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("Downloading NRD list from %s", NRD_CSV_URL)
        response = requests.get(NRD_CSV_URL, timeout=60)
        response.raise_for_status()
        content = response.text
        if not content.strip():
            raise NRDDownloadError("Downloaded NRD list is empty")
        domains = parse_domains_from_text(content)
        if not domains:
            raise NRDDownloadError("Downloaded NRD list contains no valid domains")

        temp_path = target.with_suffix(".csv.tmp")
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(target)

        now_iso = _utc_now().isoformat()
        save_nrd_state(last_download_utc=now_iso, next_index=0)
        logger.info("Cached %s domains to %s", len(domains), target)
        return domains
    except NRDDownloadError:
        raise
    except Exception as exc:
        raise NRDDownloadError(f"Failed to download NRD list: {exc}") from exc


def load_cached_domains(csv_path: Optional[Path] = None) -> List[str]:
    """Load domains from the local cache file."""
    target = csv_path or NRD_CSV_FILE
    if not target.exists():
        return []
    content = target.read_text(encoding="utf-8")
    return parse_domains_from_text(content)


def ensure_nrd_list(csv_path: Optional[Path] = None) -> List[str]:
    """Ensure a fresh-enough local NRD list exists and return all domains."""
    state = get_nrd_state()
    target = csv_path or NRD_CSV_FILE
    if cache_is_expired(state.get("last_download_utc")):
        return download_nrd_list(target)
    domains = load_cached_domains(target)
    if not domains:
        return download_nrd_list(target)
    return domains


def peek_next_domains(count: int, csv_path: Optional[Path] = None) -> List[str]:
    """
    Return the next `count` domains without advancing the cursor.
    Caller must call advance_nrd_cursor after a successful send.
    """
    if count < 1 or count > 10:
        raise ValueError("count must be between 1 and 10")

    domains = ensure_nrd_list(csv_path)
    state = get_nrd_state()
    start = state["next_index"]
    available = domains[start:]
    if len(available) < count:
        raise InsufficientDomainsError(count, len(available))
    return available[:count]


def advance_nrd_cursor(count: int) -> None:
    """Advance the domain cursor after successful delivery."""
    if count <= 0:
        return
    state = get_nrd_state()
    save_nrd_state(next_index=state["next_index"] + count)


def remaining_domain_count(csv_path: Optional[Path] = None) -> int:
    """Return how many unused domains remain in the current cached list."""
    domains = ensure_nrd_list(csv_path)
    state = get_nrd_state()
    return max(0, len(domains) - state["next_index"])
