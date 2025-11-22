from __future__ import annotations

import logging
from datetime import datetime

import requests

from .config import AppConfig

LOGGER = logging.getLogger(__name__)


def fetch_data(config: AppConfig) -> dict[str, float | str]:
    LOGGER.debug("Iniciando coleta de dados da API %s", config.api_url)
    try:
        response = requests.get(config.api_url, timeout=10)
        response.raise_for_status()
        payload = response.json()
        price = payload["data"]["amount"]
    except requests.RequestException as exc:
        raise RuntimeError("Erro ao se comunicar com a API Coinbase.") from exc
    except (ValueError, KeyError, TypeError) as exc:
        raise RuntimeError("Resposta inesperada da API Coinbase.") from exc

    try:
        price_value = float(price)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Preço inválido recebido da API Coinbase.") from exc

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOGGER.debug("Dados coletados com sucesso: %s -> %s", timestamp, price_value)
    return {"timestamp": timestamp, "price": price_value}
