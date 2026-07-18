# Threat Model

Primary risks are malicious job HTML/prompt injection, leaked API keys, unauthorized LAN access, accidental submission, sensitive logs/backups, and platform-policy drift. Defaults bind locally, redact secrets, sanitize HTML, and disable live writes.
