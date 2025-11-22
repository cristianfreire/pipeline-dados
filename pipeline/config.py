from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "pipeline.log"


@dataclass
class EmailConfig:
    enabled: bool = False
    sender: str | None = None
    recipients: List[str] = field(default_factory=list)
    smtp_server: str | None = None
    smtp_port: int = 587
    username: str | None = None
    password: str | None = None
    use_tls: bool = True


@dataclass
class AppConfig:
    api_url: str = ""
    database_path: str = "crypto_prices.db"
    csv_path: str = "crypto_prices.csv"
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    email: EmailConfig = field(default_factory=EmailConfig)


def _str_to_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_recipients(raw_recipients: str | None) -> List[str]:
    if not raw_recipients:
        return []
    return [recipient.strip() for recipient in raw_recipients.split(",") if recipient.strip()]


def load_config() -> AppConfig:
    """Carrega a configuração do pipeline a partir das variáveis de ambiente."""
    dotenv_path = PROJECT_ROOT / ".env"
    load_dotenv(dotenv_path=dotenv_path, override=False)

    api_url = os.getenv("API", "").strip()
    logging_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging_file = os.getenv("LOG_FILE", "pipeline.log").strip() or "pipeline.log"

    email_enabled = _str_to_bool(os.getenv("EMAIL_ALERTS_ENABLED", "false"))
    email_sender = os.getenv("EMAIL_ALERT_SENDER")
    email_recipients = _parse_recipients(os.getenv("EMAIL_ALERT_RECIPIENTS"))
    email_smtp_server = os.getenv("EMAIL_ALERT_SMTP_SERVER")
    email_smtp_port = os.getenv("EMAIL_ALERT_SMTP_PORT", "587")
    email_username = os.getenv("EMAIL_ALERT_USERNAME")
    email_password = os.getenv("EMAIL_ALERT_PASSWORD")
    email_use_tls = _str_to_bool(os.getenv("EMAIL_ALERT_USE_TLS", "true"))

    try:
        smtp_port = int(email_smtp_port)
    except (TypeError, ValueError):
        smtp_port = 587

    config = AppConfig(
        api_url=api_url,
        logging=LoggingConfig(level=logging_level, file=logging_file),
        email=EmailConfig(
            enabled=email_enabled,
            sender=email_sender,
            recipients=email_recipients,
            smtp_server=email_smtp_server,
            smtp_port=smtp_port,
            username=email_username,
            password=email_password,
            use_tls=email_use_tls,
        ),
    )

    if not config.api_url:
        raise RuntimeError("Variável de ambiente API não configurada.")

    return config
