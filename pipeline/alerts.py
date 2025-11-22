from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage

from .config import EmailConfig

# Configuração do logger para o módulo de alertas
LOGGER = logging.getLogger(__name__)


def send_failure_alert(email_config: EmailConfig, error: Exception, trace: str) -> None:
    if not email_config.enabled:
        LOGGER.debug("Alertas por e-mail desativados.")
        return

    missing_fields = [
        field_name
        for field_name, value in {
            "EMAIL_ALERT_SENDER": email_config.sender,
            "EMAIL_ALERT_RECIPIENTS": email_config.recipients,
            "EMAIL_ALERT_SMTP_SERVER": email_config.smtp_server,
        }.items()
        if not value
    ]

    if missing_fields:
        LOGGER.warning(
            "Não foi possível enviar alerta por e-mail. Variáveis ausentes: %s",
            ", ".join(missing_fields),
        )
        return

    message = EmailMessage()
    message["From"] = email_config.sender
    message["To"] = ", ".join(email_config.recipients)
    message["Subject"] = "Falha no pipeline de preços de criptomoedas"
    message.set_content(
        (
            "O pipeline de coleta de preços falhou.\n\n"
            f"Erro: {error}\n\n"
            "Traceback:\n"
            f"{trace}\n"
        )
    )

    context = ssl.create_default_context()

    try:
        if email_config.use_tls:
            with smtplib.SMTP(email_config.smtp_server, email_config.smtp_port, timeout=30) as server:
                server.starttls(context=context)
                _login_if_needed(server, email_config)
                server.send_message(message)
        else:
            with smtplib.SMTP_SSL(email_config.smtp_server, email_config.smtp_port, context=context, timeout=30) as server:
                _login_if_needed(server, email_config)
                server.send_message(message)
        LOGGER.info("Alerta de falha enviado para %s.", ", ".join(email_config.recipients))
    except smtplib.SMTPException as exc:
        LOGGER.error("Erro ao enviar alerta por e-mail: %s", exc)


def _login_if_needed(server: smtplib.SMTP, config: EmailConfig) -> None:
    if config.username and config.password:
        server.login(config.username, config.password)
