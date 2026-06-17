from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from research_agent.delivery.email import SMTPConfig


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return int(raw)


def env_list(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(slots=True)
class AppConfig:
    openai_base_url: str = ""
    openai_api_key: str = ""
    stage1_model: str = ""
    stage2_model: str = ""
    report_model: str = ""
    report_fallback_model: str = ""
    lookback_days: int = 3
    max_reports: int = 8
    stage1_confidence_threshold: int = 7
    llm_timeout_seconds: int = 90
    report_timeout_seconds: int = 420
    report_max_chars: int = 90000
    report_fallback_max_chars: int = 25000
    report_max_retries: int = 1
    report_consecutive_failure_limit: int = 2
    report_language: str = "zh"
    send_email: bool = True
    state_path: Path = Path("data/state.json")
    report_dir: Path = Path("reports")
    skip_sources: bool = False
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_ssl: bool = True
    smtp_starttls: bool = False
    email_from: str = ""
    email_to: list[str] = field(default_factory=list)
    anthropic_urls: list[str] = field(default_factory=lambda: ["https://www.anthropic.com/research"])
    transformer_circuits_urls: list[str] = field(default_factory=lambda: ["https://transformer-circuits.pub/"])
    alignment_forum_urls: list[str] = field(default_factory=lambda: ["https://www.alignmentforum.org/"])

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            openai_base_url=os.getenv("OPENAI_BASE_URL", "").strip(),
            openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            stage1_model=os.getenv("STAGE1_MODEL", "").strip(),
            stage2_model=os.getenv("STAGE2_MODEL", "").strip(),
            report_model=os.getenv("REPORT_MODEL", "").strip(),
            report_fallback_model=os.getenv("REPORT_FALLBACK_MODEL", "").strip(),
            lookback_days=env_int("LOOKBACK_DAYS", 3),
            max_reports=env_int("MAX_REPORTS", 8),
            stage1_confidence_threshold=env_int("STAGE1_CONFIDENCE_THRESHOLD", 7),
            llm_timeout_seconds=env_int("LLM_TIMEOUT_SECONDS", 90),
            report_timeout_seconds=env_int("REPORT_TIMEOUT_SECONDS", 420),
            report_max_chars=env_int("REPORT_MAX_CHARS", 90000),
            report_fallback_max_chars=env_int("REPORT_FALLBACK_MAX_CHARS", 25000),
            report_max_retries=env_int("REPORT_MAX_RETRIES", 1),
            report_consecutive_failure_limit=env_int("REPORT_CONSECUTIVE_FAILURE_LIMIT", 2),
            report_language=os.getenv("REPORT_LANGUAGE", "zh").strip() or "zh",
            send_email=env_bool("SEND_EMAIL", True),
            state_path=Path(os.getenv("STATE_PATH", "data/state.json")),
            report_dir=Path(os.getenv("REPORT_DIR", "reports")),
            skip_sources=env_bool("SKIP_SOURCES", False),
            smtp_host=os.getenv("SMTP_HOST", "").strip(),
            smtp_port=env_int("SMTP_PORT", 465),
            smtp_username=os.getenv("SMTP_USERNAME", "").strip(),
            smtp_password=os.getenv("SMTP_PASSWORD", "").strip(),
            smtp_use_ssl=env_bool("SMTP_USE_SSL", True),
            smtp_starttls=env_bool("SMTP_STARTTLS", False),
            email_from=os.getenv("EMAIL_FROM", "").strip(),
            email_to=env_list("EMAIL_TO", []),
            anthropic_urls=env_list("ANTHROPIC_URLS", ["https://www.anthropic.com/research"]),
            transformer_circuits_urls=env_list("TRANSFORMER_CIRCUITS_URLS", ["https://transformer-circuits.pub/"]),
            alignment_forum_urls=env_list("ALIGNMENT_FORUM_URLS", ["https://www.alignmentforum.org/"]),
        )

    def validate_llm(self) -> None:
        missing = [
            name
            for name, value in {
                "OPENAI_BASE_URL": self.openai_base_url,
                "OPENAI_API_KEY": self.openai_api_key,
                "STAGE1_MODEL": self.stage1_model,
                "STAGE2_MODEL": self.stage2_model,
                "REPORT_MODEL": self.report_model,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Missing LLM environment variables: {', '.join(missing)}")

    def validate_email(self) -> None:
        missing = [
            name
            for name, value in {
                "SMTP_HOST": self.smtp_host,
                "SMTP_USERNAME": self.smtp_username,
                "SMTP_PASSWORD": self.smtp_password,
                "EMAIL_FROM": self.email_from,
                "EMAIL_TO": ",".join(self.email_to),
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Missing SMTP/email environment variables: {', '.join(missing)}")

    def smtp_config(self) -> SMTPConfig:
        return SMTPConfig(
            host=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_username,
            password=self.smtp_password,
            use_ssl=self.smtp_use_ssl,
            starttls=self.smtp_starttls,
        )
