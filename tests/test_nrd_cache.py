"""Unit tests for NRD cache and cursor logic."""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

import backend.nrd_cache as nrd_cache
from backend.nrd_cache import (
    InsufficientDomainsError,
    NRDDownloadError,
    advance_nrd_cursor,
    build_nrd_url,
    cache_is_expired,
    download_nrd_list,
    ensure_nrd_list,
    get_nrd_state,
    parse_domains_from_text,
    peek_next_domains,
    save_nrd_state,
)
from tests.conftest import SAMPLE_CSV


def test_parse_domains_skips_blanks():
    domains = parse_domains_from_text(SAMPLE_CSV)
    assert domains == [f"domain{i}.test" for i in range(1, 12)]


def test_build_nrd_url():
    assert build_nrd_url("vilfredo.sk") == "https://www.vilfredo.sk"
    assert build_nrd_url("  example.com  ") == "https://www.example.com"


def test_download_writes_cache_and_resets_cursor(tmp_data_dir, mock_nrd_download):
    domains = download_nrd_list(tmp_data_dir["csv_file"])
    assert len(domains) == 11
    assert tmp_data_dir["csv_file"].exists()
    state = get_nrd_state()
    assert state["next_index"] == 0
    assert state["last_download_utc"] is not None


def test_ensure_nrd_list_reuses_cache_within_24h(
    sample_nrd_csv, mock_nrd_download, monkeypatch
):
    calls = {"count": 0}

    def mock_get(url, timeout=60):
        calls["count"] += 1
        response = MagicMock()
        response.text = "should-not-download.test\n"
        response.raise_for_status = MagicMock()
        return response

    monkeypatch.setattr("backend.nrd_cache.requests.get", mock_get)
    domains = ensure_nrd_list(sample_nrd_csv["csv_file"])
    assert len(domains) == 11
    assert calls["count"] == 0


def test_cache_expired_at_24h_boundary(sample_nrd_csv):
    state = get_nrd_state()
    last = state["last_download_utc"]
    downloaded_at = datetime.fromisoformat(last)
    if downloaded_at.tzinfo is None:
        downloaded_at = downloaded_at.replace(tzinfo=timezone.utc)

    assert not cache_is_expired(last, now=downloaded_at + timedelta(hours=23, minutes=59))
    assert cache_is_expired(last, now=downloaded_at + timedelta(hours=24))
    assert cache_is_expired(last, now=downloaded_at + timedelta(hours=25))


def test_redownload_after_expiry_resets_cursor(
    sample_nrd_csv, mock_nrd_download, monkeypatch
):
    save_nrd_state(next_index=5)
    state = get_nrd_state()
    last = state["last_download_utc"]
    downloaded_at = datetime.fromisoformat(last)
    if downloaded_at.tzinfo is None:
        downloaded_at = downloaded_at.replace(tzinfo=timezone.utc)

    expired_now = downloaded_at + timedelta(hours=25)
    monkeypatch.setattr(
        "backend.nrd_cache._utc_now",
        lambda: expired_now,
    )
    ensure_nrd_list(sample_nrd_csv["csv_file"])
    assert get_nrd_state()["next_index"] == 0


def test_download_http_failure_preserves_cursor(sample_nrd_csv, monkeypatch):
    save_nrd_state(next_index=4)
    original_content = sample_nrd_csv["csv_file"].read_text()

    def mock_get(url, timeout=60):
        raise ConnectionError("network down")

    monkeypatch.setattr("backend.nrd_cache.requests.get", mock_get)
    monkeypatch.setattr(
        "backend.nrd_cache.cache_is_expired",
        lambda last_download_utc, now=None: True,
    )

    with pytest.raises(NRDDownloadError):
        download_nrd_list(sample_nrd_csv["csv_file"])

    assert get_nrd_state()["next_index"] == 4
    assert sample_nrd_csv["csv_file"].read_text() == original_content


def test_download_empty_body_raises(sample_nrd_csv, monkeypatch):
    def mock_get(url, timeout=60):
        response = MagicMock()
        response.text = "   \n  "
        response.raise_for_status = MagicMock()
        return response

    monkeypatch.setattr("backend.nrd_cache.requests.get", mock_get)
    with pytest.raises(NRDDownloadError, match="empty"):
        download_nrd_list(sample_nrd_csv["csv_file"])


def test_peek_next_domains_and_advance(sample_nrd_csv):
    domains = peek_next_domains(3, sample_nrd_csv["csv_file"])
    assert domains == ["domain1.test", "domain2.test", "domain3.test"]
    assert get_nrd_state()["next_index"] == 0

    advance_nrd_cursor(3)
    assert get_nrd_state()["next_index"] == 3

    domains = peek_next_domains(2, sample_nrd_csv["csv_file"])
    assert domains == ["domain4.test", "domain5.test"]


def test_insufficient_domains_error(sample_nrd_csv):
    save_nrd_state(next_index=10)
    with pytest.raises(InsufficientDomainsError) as exc:
        peek_next_domains(3, sample_nrd_csv["csv_file"])
    assert exc.value.remaining == 1
    assert get_nrd_state()["next_index"] == 10


def test_peek_invalid_count(sample_nrd_csv):
    with pytest.raises(ValueError):
        peek_next_domains(0, sample_nrd_csv["csv_file"])
    with pytest.raises(ValueError):
        peek_next_domains(11, sample_nrd_csv["csv_file"])
