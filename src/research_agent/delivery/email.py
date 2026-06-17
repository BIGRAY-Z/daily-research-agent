from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from mimetypes import guess_type
from pathlib import Path


@dataclass(slots=True)
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    use_ssl: bool = True
    starttls: bool = False


def build_email_message(
    *,
    subject: str,
    body_markdown: str,
    sender: str,
    recipients: list[str],
    attachments: list[Path] | None = None,
) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(body_markdown, subtype="plain", charset="utf-8")
    for path in attachments or []:
        data = path.read_bytes()
        content_type = guess_type(path.name)[0] or "application/octet-stream"
        maintype, subtype = content_type.split("/", 1)
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=path.name)
    return msg


def send_email(
    *,
    smtp: SMTPConfig,
    subject: str,
    body_markdown: str,
    sender: str,
    recipients: list[str],
    attachments: list[Path] | None = None,
) -> None:
    msg = build_email_message(
        subject=subject,
        body_markdown=body_markdown,
        sender=sender,
        recipients=recipients,
        attachments=attachments,
    )
    if smtp.use_ssl:
        with smtplib.SMTP_SSL(smtp.host, smtp.port, timeout=60) as server:
            server.login(smtp.username, smtp.password)
            server.send_message(msg)
        return
    with smtplib.SMTP(smtp.host, smtp.port, timeout=60) as server:
        if smtp.starttls:
            server.starttls()
        server.login(smtp.username, smtp.password)
        server.send_message(msg)
