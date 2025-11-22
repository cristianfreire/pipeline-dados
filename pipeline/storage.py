from __future__ import annotations

import logging
import os
import sqlite3
from contextlib import closing

import pandas as pd

LOGGER = logging.getLogger(__name__)


def store_data(dataframe: pd.DataFrame, database_path: str) -> None:
    try:
        with closing(sqlite3.connect(database_path)) as connection:
            dataframe.to_sql("prices", connection, if_exists="append", index=False)
        LOGGER.debug("Dados gravados no banco SQLite %s.", database_path)
    except sqlite3.DatabaseError as exc:
        raise RuntimeError("Falha ao gravar dados no banco SQLite.") from exc


def export_csv(dataframe: pd.DataFrame, csv_path: str) -> None:
    try:
        dataframe.to_csv(csv_path, mode="a", header=not os.path.exists(csv_path), index=False)
        LOGGER.debug("Dados exportados para %s.", csv_path)
    except OSError as exc:
        raise RuntimeError(f"Falha ao exportar dados para o arquivo {csv_path}.") from exc
