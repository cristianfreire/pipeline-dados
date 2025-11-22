from __future__ import annotations

import logging
import traceback

from .alerts import send_failure_alert
from .config import AppConfig
from .extract import fetch_data
from .storage import export_csv, store_data
from .transform import transform_data

LOGGER = logging.getLogger(__name__)


def run_pipeline(config: AppConfig) -> bool:
    try:
        raw_data = fetch_data(config)
        dataframe = transform_data(raw_data)
        store_data(dataframe, config.database_path)
        export_csv(dataframe, config.csv_path)
        LOGGER.info("Pipeline executado com sucesso.")
        return True
    except Exception as exc:  # noqa: BLE001
        error_trace = traceback.format_exc()
        LOGGER.exception("Falha na execução do pipeline.")
        send_failure_alert(config.email, exc, error_trace)
        return False
