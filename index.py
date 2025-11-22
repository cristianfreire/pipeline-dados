"""Ponto de entrada para execução do pipeline de preços de criptomoedas."""

from pipeline import configure_logging, load_config, run_pipeline


def main() -> int:
    config = load_config()
    configure_logging(config.logging)
    success = run_pipeline(config)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())