# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.7.x   | :white_check_mark: |
| 1.6.x   | :white_check_mark: |
| 1.5.x   | :x:                |
| < 1.5   | :x:                |

## Reporting a Vulnerability

Please email **woz@wozwasere.com** with any security issues. Do not open public issues for undisclosed vulnerabilities.

## Security Model

This application is a **security testing tool**. It is designed to generate and send phishing samples, malware test attachments (EICAR, Cynic), spam-test (GTUBE) messages, and other controlled test content. Deploy and use it only in isolated lab environments with explicit authorization.

### Deployment considerations

| Area | Risk | Mitigation |
|------|------|------------|
| **No API authentication** | Anyone who can reach the web UI can trigger email sends if SMTP is configured. | Bind to localhost, use a firewall, or place behind an authenticated reverse proxy. Do not expose port 8080 to the public internet. |
| **Open CORS** | `CORS(app)` allows any origin. | Acceptable only on trusted networks; restrict at the reverse proxy if needed. |
| **Configuration secrets** | SMTP/IMAP passwords stored in `data/config.json`. | Password fields encrypted at rest (Fernet). Protect `data/.encryption_key` and set `ENCRYPTION_KEY` in production. Never commit `data/` to git. |
| **Debug mode** | `app.run(debug=True)` when started via `python backend/app.py` directly. | Production Docker image uses Gunicorn without Flask debug. Prefer Docker or Gunicorn for deployments. |
| **Custom email HTML** | Operators can embed arbitrary `http`/`https` links in email bodies. | Intended for authorized testing. Custom URL input rejects non-HTTP(S) schemes client-side. |
| **QR + HTML body** | Plain-text parts are derived from HTML when links are present. | QR HTML builder escapes plain-text bodies; pre-built HTML link blocks are treated as trusted operator content. |

### Secrets and data

- `data/config.json` — email credentials and schedules (passwords encrypted).
- `data/.encryption_key` — local Fernet key if `ENCRYPTION_KEY` is unset (gitignored).
- Email history in config — metadata only, no message bodies stored long-term in API responses.

### Dependency hygiene

Review `requirements.txt` periodically and rebuild Docker images after updates. GitHub Actions publishes images to `ghcr.io/warrensealey/threatsampleproject` on pushes to `main`.
