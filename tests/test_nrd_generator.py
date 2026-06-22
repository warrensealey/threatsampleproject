"""Unit tests for NRD email generator."""

import pytest

from backend.generators.nrd import NRDGenerator
from backend.nrd_cache import advance_nrd_cursor, peek_next_domains


def test_generate_single_email(sample_nrd_csv):
    gen = NRDGenerator()
    emails = gen.generate_emails(count=1, recipients=["a@example.com"])
    assert len(emails) == 1
    email = emails[0]
    assert email["type"] == "nrd"
    assert email["domain"] == "domain1.test"
    assert email["url"] == "https://www.domain1.test"
    assert email["subject"] == "Newly Registered Domain Test - domain1.test"
    assert "https://www.domain1.test" in email["body"]
    assert "List of domains downloaded on" in email["body"]
    assert email["recipients"] == ["a@example.com"]


def test_generate_ten_distinct_emails(sample_nrd_csv):
    gen = NRDGenerator()
    emails = gen.generate_emails(count=10, recipients=["a@example.com"])
    assert len(emails) == 10
    domains = [e["domain"] for e in emails]
    assert len(set(domains)) == 10
    assert domains[0] == "domain1.test"
    assert domains[-1] == "domain10.test"


def test_whitespace_domain_stripped_in_url(sample_nrd_csv):
    sample_nrd_csv["csv_file"].write_text("  spaced.test  \n")
    gen = NRDGenerator()
    emails = gen.generate_emails(count=1, recipients=["a@example.com"])
    assert emails[0]["url"] == "https://www.spaced.test"


def test_no_recipients_raises(sample_nrd_csv, monkeypatch):
    import backend.config as config_module

    config = config_module.load_config()
    config["email_generation"]["default_recipients"] = []
    config_module.save_config(config)

    gen = NRDGenerator()
    with pytest.raises(ValueError, match="No recipients"):
        gen.generate_emails(count=1, recipients=None)


def test_peek_does_not_advance_cursor(sample_nrd_csv):
    gen = NRDGenerator()
    gen.generate_emails(count=2, recipients=["a@example.com"])
    from backend.nrd_cache import get_nrd_state

    assert get_nrd_state()["next_index"] == 0

    advance_nrd_cursor(2)
    assert get_nrd_state()["next_index"] == 2
