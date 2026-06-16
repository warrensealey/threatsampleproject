"""Shared pytest fixtures for NRD tests."""

import json
from datetime import datetime, timedelta, timezone

import pytest

import backend.config as config_module
import backend.nrd_cache as nrd_cache_module

SAMPLE_CSV = """domain1.test

  domain2.test
domain3.test
domain4.test
domain5.test
domain6.test
domain7.test
domain8.test
domain9.test
domain10.test
domain11.test
"""


@pytest.fixture
def tmp_data_dir(tmp_path, monkeypatch):
    """Isolated data directory with patched config and NRD CSV paths."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    config_file = data_dir / "config.json"
    csv_file = data_dir / "nrd-1w.csv"
    eml_dir = data_dir / "eml_exports"
    eml_dir.mkdir()

    default_config = json.loads(json.dumps(config_module.DEFAULT_CONFIG))
    default_config["nrd"] = {"last_download_utc": None, "next_index": 0}
    default_config["email_generation"]["default_recipients"] = ["test@example.com"]
    config_file.write_text(json.dumps(default_config))

    monkeypatch.setattr(config_module, "CONFIG_FILE", config_file)
    monkeypatch.setattr(nrd_cache_module, "NRD_CSV_FILE", csv_file)

    return {
        "data_dir": data_dir,
        "config_file": config_file,
        "csv_file": csv_file,
        "eml_dir": eml_dir,
    }


@pytest.fixture
def sample_nrd_csv(tmp_data_dir):
    """Pre-populate the NRD cache file without downloading."""
    tmp_data_dir["csv_file"].write_text(SAMPLE_CSV)
    now = datetime.now(timezone.utc).isoformat()
    config = json.loads(tmp_data_dir["config_file"].read_text())
    config["nrd"] = {"last_download_utc": now, "next_index": 0}
    tmp_data_dir["config_file"].write_text(json.dumps(config))
    return tmp_data_dir


@pytest.fixture
def mock_nrd_download(monkeypatch):
    """Patch requests.get to return fixture CSV content."""

    class MockResponse:
        text = SAMPLE_CSV

        def raise_for_status(self):
            return None

    def mock_get(url, timeout=60):
        return MockResponse()

    monkeypatch.setattr("backend.nrd_cache.requests.get", mock_get)


@pytest.fixture
def frozen_time(monkeypatch):
    """Patch NRD cache UTC clock for TTL boundary tests."""
    fixed = datetime(2026, 6, 16, 12, 0, 0, tzinfo=timezone.utc)

    def mock_utc_now():
        return fixed

    monkeypatch.setattr(nrd_cache_module, "_utc_now", mock_utc_now)
    return fixed


@pytest.fixture
def flask_client(tmp_data_dir, mock_nrd_download, monkeypatch):
    """Flask test client with isolated data paths."""
    from backend.app import app

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
