from __future__ import annotations

import logging

import pandas as pd

LOGGER = logging.getLogger(__name__)


def transform_data(data: dict[str, object]) -> pd.DataFrame:
    dataframe = pd.DataFrame([data])
    LOGGER.debug("DataFrame transformado: %s", dataframe.head(1).to_dict(orient="records"))
    return dataframe
