"""DAG do Apache Airflow para orquestrar o pipeline de preços de criptomoedas."""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

try:
    from pipeline import configure_logging, load_config, run_pipeline
except ImportError as exc:  # pragma: no cover - execução em ambiente Airflow
    logging.exception("Falha ao importar o pacote pipeline. Ajuste PYTHONPATH no Airflow.")
    raise


def execute_pipeline() -> None:
    """Wrapper para executar o pipeline e propagar falhas ao Airflow."""
    config = load_config()
    configure_logging(config.logging)
    success = run_pipeline(config)
    if not success:
        raise RuntimeError("Execução do pipeline falhou. Consulte os logs para detalhes.")


def _build_dag() -> DAG:
    default_args = {
        "owner": "data_team",
        "depends_on_past": False,
        "email_on_failure": False,  # alertas tratados dentro do pipeline
        "email_on_retry": False,
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    }

    dag = DAG(
        dag_id="crypto_prices_pipeline",
        description="Coleta incremental de preços de criptomoedas (Coinbase)",
        default_args=default_args,
        schedule_interval="*/15 * * * *",  # a cada 15 minutos
        start_date=datetime(2025, 1, 1),
        catchup=False,
        max_active_runs=1,
        tags=["crypto", "etl"],
    )

    with dag:
        PythonOperator(
            task_id="run_crypto_pipeline",
            python_callable=execute_pipeline,
        )

    return dag


dag = _build_dag()
