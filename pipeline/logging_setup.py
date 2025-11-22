from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import LoggingConfig


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGGER_NAME = "pipeline"


def _resolve_log_path(path_value: str) -> Path:
    candidate = Path(path_value) if path_value else Path("pipeline.log")
    if candidate.is_absolute():
        return candidate
    return (PROJECT_ROOT / candidate).resolve()


def configure_logging(config: LoggingConfig) -> None:
    """Inicializa logging com saída em console e arquivo rotativo."""
    logger = logging.getLogger(LOGGER_NAME)

    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        stream_handler = logging.StreamHandler(sys.__stdout__)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    log_path = _resolve_log_path(config.file)
    existing_file_handler = next(
        (
            handler
            for handler in logger.handlers
            if isinstance(handler, RotatingFileHandler)
            and Path(getattr(handler, "baseFilename", "")) == log_path
        ),
        None,
    )

    if existing_file_handler:
        existing_file_handler.setFormatter(formatter)
        return

    try:
        if log_path.parent and not log_path.parent.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(log_path, maxBytes=1_048_576, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError as exc:
        logger.warning("Não foi possível inicializar o arquivo de log %s: %s", log_path, exc)
