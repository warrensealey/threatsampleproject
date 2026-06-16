"""API tests for POST /api/send/nrd."""

import json
from unittest.mock import MagicMock

import pytest

from backend.email_generator import EmailGenerator
from backend.nrd_cache import InsufficientDomainsError, NRDDownloadError


def test_send_nrd_happy_path(flask_client, monkeypatch):
    def mock_send(count, recipients, delivery_mode="smtp"):
        return {
            "success": True,
            "sent": count,
            "total": count,
            "failed": 0,
            "domains": ["a.test"],
            "urls": ["https://www.a.test"],
        }

    monkeypatch.setattr(
        "backend.api.routes.email_generator.send_nrd_emails", mock_send
    )
    response = flask_client.post(
        "/api/send/nrd",
        data=json.dumps(
            {
                "count": 3,
                "recipients": ["user@example.com"],
                "delivery_mode": "smtp",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["sent"] == 3


def test_send_nrd_missing_recipients(flask_client):
    response = flask_client.post(
        "/api/send/nrd",
        data=json.dumps({"count": 1}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "No recipients" in response.get_json()["error"]


@pytest.mark.parametrize("count", [0, 11, -1])
def test_send_nrd_invalid_count(flask_client, count):
    response = flask_client.post(
        "/api/send/nrd",
        data=json.dumps({"count": count, "recipients": ["a@b.com"]}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_send_nrd_invalid_delivery_mode(flask_client):
    response = flask_client.post(
        "/api/send/nrd",
        data=json.dumps(
            {
                "count": 1,
                "recipients": ["a@b.com"],
                "delivery_mode": "ftp",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_send_nrd_eml_mode_passed_through(flask_client, monkeypatch):
    captured = {}

    def mock_send(count, recipients, delivery_mode="smtp"):
        captured["delivery_mode"] = delivery_mode
        return {"success": True, "sent": 1, "total": 1, "failed": 0}

    monkeypatch.setattr(
        "backend.api.routes.email_generator.send_nrd_emails", mock_send
    )
    response = flask_client.post(
        "/api/send/nrd",
        data=json.dumps(
            {
                "count": 1,
                "recipients": ["a@b.com"],
                "delivery_mode": "eml",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert captured["delivery_mode"] == "eml"


def test_send_nrd_insufficient_domains(flask_client, monkeypatch):
    def mock_send(count, recipients, delivery_mode="smtp"):
        return {
            "success": False,
            "error": "Only 1 domain(s) left",
            "sent": 0,
            "remaining": 1,
        }

    monkeypatch.setattr(
        "backend.api.routes.email_generator.send_nrd_emails", mock_send
    )
    response = flask_client.post(
        "/api/send/nrd",
        data=json.dumps({"count": 3, "recipients": ["a@b.com"]}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "Only 1" in response.get_json()["error"]


def test_send_nrd_eml_delivery(tmp_data_dir, sample_nrd_csv, monkeypatch):
    monkeypatch.setattr(
        "backend.config.get_email_client_config",
        lambda: {
            "smtp_server": "smtp.test",
            "smtp_port": 587,
            "username": "user",
            "password": "pass",
            "smtp_use_tls": True,
            "smtp_use_ssl": False,
            "imap_server": "",
            "imap_port": 993,
        },
    )

    saved_paths = []

    def fake_save(self, to_addresses, subject, body, output_dir=None, **kwargs):
        from pathlib import Path

        out = Path(output_dir or str(tmp_data_dir["eml_dir"]))
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{len(saved_paths)}.eml"
        path.write_text(f"Subject: {subject}\n\n{body}")
        saved_paths.append(path)
        return path

    monkeypatch.setattr(
        "backend.smtp_client.SMTPClient.save_email_as_eml", fake_save
    )

    gen = EmailGenerator()
    result = gen.send_nrd_emails(
        count=2, recipients=["test@example.com"], delivery_mode="eml"
    )
    assert result["success"] is True
    assert result["sent"] == 2
    assert len(saved_paths) == 2

    from email import message_from_bytes

    for path in saved_paths:
        msg = message_from_bytes(path.read_bytes())
        payload = msg.get_payload()
        if isinstance(payload, list):
            body = "".join(part.get_payload() for part in payload)
        else:
            body = payload
        assert "https://www.domain" in body


def test_send_failure_does_not_advance_cursor(sample_nrd_csv, monkeypatch):
    monkeypatch.setattr(
        "backend.config.get_email_client_config",
        lambda: {
            "smtp_server": "",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "smtp_use_tls": True,
            "smtp_use_ssl": False,
            "imap_server": "",
            "imap_port": 993,
        },
    )

    from backend.nrd_cache import get_nrd_state

    assert get_nrd_state()["next_index"] == 0
    gen = EmailGenerator()
    result = gen.send_nrd_emails(
        count=2, recipients=["test@example.com"], delivery_mode="smtp"
    )
    assert result["success"] is False
    assert get_nrd_state()["next_index"] == 0
