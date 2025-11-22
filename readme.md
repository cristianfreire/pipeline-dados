# Pipeline de Dados de Preços de Criptomoedas

Pipeline em Python para coletar, transformar e persistir cotações de criptomoedas a partir da API pública da Coinbase. O projeto foi estruturado para facilitar automação, rastreabilidade e expansão futura para novas fontes ou destinos de dados.

## Sumário
- [Visão Geral](#visão-geral)
- [Arquitetura da Solução](#arquitetura-da-solução)
- [Pré-requisitos](#pré-requisitos)
- [Configuração](#configuração)
- [Execução do Pipeline](#execução-do-pipeline)
- [Automação e Agendamento](#automação-e-agendamento)
- [Integração com Apache Airflow](#integração-com-apache-airflow)
- [Execução com Docker](#execução-com-docker)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Fontes e Saídas de Dados](#fontes-e-saídas-de-dados)
- [Monitoramento e Troubleshooting](#monitoramento-e-troubleshooting)
- [Próximos Passos](#próximos-passos)

## Visão Geral
- **Objetivo:** capturar o preço spot do par `BTC-USD`, transformar em um `DataFrame` e armazenar de forma incremental.
- **Stack:** Python, `requests`, `pandas`, `sqlite3`, `python-dotenv`.
- **Entregáveis:** arquivo SQLite (`crypto_prices.db`) e CSV incremental (`crypto_prices.csv`).
- **Executável:** `index.py` (ou `python -m pipeline`), que delega a orquestração ao pacote `pipeline`.

## Arquitetura da Solução

```
[Coinbase API] --fetch--> [Python (requests)] --transform--> [Pandas DataFrame]
														|                     |
														|                     +--> Exporta CSV incremental
														+--> Persiste em SQLite (tabela prices)
```

Etapas principais:
1. **Extração (`fetch_data`)** – realiza `GET` na URL definida em `API` e normaliza o timestamp.
2. **Transformação (`transform_data`)** – converte o dicionário em `DataFrame` com tipagem numérica.
3. **Armazenamento (`store_data`)** – grava no banco `crypto_prices.db`, criando a tabela `prices` se necessário.
4. **Exportação (`export_csv`)** – adiciona o registro no CSV, mantendo cabeçalho apenas quando o arquivo é criado.

### Componentes do pacote `pipeline`
- `config.py`: carrega variáveis de ambiente e centraliza configurações (API, logging, alertas por e-mail).
- `logging_setup.py`: inicializa logging em console e arquivo rotativo (`pipeline.log`).
- `extract.py`: encapsula a coleta dos dados na API.
- `transform.py`: converte os dados da API em `DataFrame`.
- `storage.py`: persiste em SQLite e exporta CSV.
- `alerts.py`: envia alertas de falha via e-mail quando configurado.
- `pipeline.py`: orquestra as etapas, incluindo o fluxo de erros e alertas.

## Pré-requisitos
- Python 3.10 ou superior instalado e disponível no `PATH`.
- `pip` atualizado (`python -m pip install --upgrade pip`).
- Opcional: `virtualenv` ou `venv` para isolar dependências.

## Configuração
1. Clone ou baixe o repositório.
2. Crie o ambiente virtual (exemplo no Windows PowerShell):

	```powershell
	python -m venv venv
	.\venv\Scripts\Activate.ps1
	```

3. Instale as dependências:

	```powershell
	pip install -r requirements.txt
	```

4. Configure as variáveis de ambiente copiando o arquivo modelo:

	```powershell
	Copy-Item .env.example .env
	```

	Ajuste o valor de `API` caso precise apontar para outra moeda ou provedor.

5. **(Opcional)** Configure os alertas por e-mail no arquivo `.env` preenchendo remetente, destinatários e credenciais SMTP. Defina `EMAIL_ALERTS_ENABLED=true` para ativar o envio.
6. **(Opcional)** Ajuste os caminhos de saída (`DATABASE_PATH`, `CSV_PATH`) caso queira gravar os arquivos fora do diretório raiz do projeto.

## Execução do Pipeline

```powershell
python index.py
```

Ao finalizar, os dados coletados serão anexados à tabela `prices` em `crypto_prices.db` e ao arquivo `crypto_prices.csv`. O log do PowerShell exibirá eventuais erros de rede ou gravação.

## Automação e Agendamento
- **Windows Task Scheduler:** crie uma `Basic Task`, defina a periodicidade desejada (por minuto, hora ou dia) e configure a ação "Start a Program" apontando para `python`. Em "Add arguments", coloque `index.py`, e em "Start in", informe o diretório do projeto (`C:\projetos_de_programacao\pipeline dados`).
- **Linux/macOS:** utilize `cron` executando `python /caminho/para/index.py` na frequência desejada.
- Garanta que o ambiente virtual esteja ativado no momento da execução automatizada ou forneça o caminho completo para o interpretador (`/caminho/para/venv/bin/python`).

## Integração com Apache Airflow
- Copie o diretório do projeto (ou publique como pacote interno) para uma instalação do Airflow com acesso ao mesmo `.env` ou a variáveis equivalentes.
- Adicione as dependências do pipeline (`pandas`, `requests`, `python-dotenv`) ao ambiente do Airflow; utilize `pip install -r requirements.txt` ou configure-as no `requirements.txt` do próprio Airflow.
- Posicione o arquivo `airflow/dags/crypto_pipeline_dag.py` dentro da pasta de DAGs do Airflow.
- Ajuste o `PYTHONPATH` do Airflow (variável `AIRFLOW__CORE__DAGS_FOLDER` ou `PYTHONPATH` do serviço) para incluir o diretório raiz do projeto, permitindo os imports do pacote `pipeline`.
- Opcional: defina `EMAIL_ALERTS_ENABLED=true` no `.env` utilizado pelo Airflow para consolidar alertas dentro do próprio pipeline; caso prefira alertas do Airflow, ajuste `email_on_failure` e configure destinatários na DAG.
- Agende o DAG na UI do Airflow e acompanhe as execuções pela aba *Logs*. Em caso de falhas de importação, verifique as mensagens registradas no log da DAG e em `pipeline.log`.

## Execução com Docker
- Pré-requisitos instalados no host: Docker Desktop (ou daemon compatível) e Docker Compose v2.
- Ajuste, se necessário, o UID utilizado pelos contêineres editando `docker/.env` (`AIRFLOW_UID`).
- Inicialize os serviços executando a partir da raiz do projeto:

	```powershell
	cd docker
	docker compose up airflow-init
	docker compose up -d
	```

	O comando `airflow-init` prepara o banco de metadados e cria um usuário administrador padrão (`admin`/`admin`).
- Acesse a interface web em `http://localhost:8080`, ative o DAG `crypto_prices_pipeline` e monitore as execuções.
- Os contêineres montam o diretório do projeto em `/opt/airflow/project`, permitindo que alterações locais sejam refletidas imediatamente na instância em execução.
- Personalize `AIRFLOW__WEBSERVER__SECRET_KEY` no `docker-compose.yaml` (ou em variáveis de ambiente) antes de ir para produção.
- Para encerrar os serviços, use `docker compose down --volumes` (remove também o banco Postgres) ou `docker compose down` para manter o estado.

## Estrutura do Projeto

```
.
├── index.py
├── requirements.txt
├── crypto_prices.db
├── crypto_prices.csv
├── .env            # configurações locais (não versionado)
├── .env.example    # modelo com a variável API padrão
├── docker/
│   ├── .env
│   └── docker-compose.yaml
├── airflow/
│   └── dags/
│       └── crypto_pipeline_dag.py
├── pipeline/
│   ├── __init__.py
│   ├── alerts.py
│   ├── config.py
│   ├── extract.py
│   ├── logging_setup.py
│   ├── pipeline.py
│   ├── storage.py
│   └── transform.py
├── readme.md
└── venv/           # ambiente virtual (opcional)
```

## Fontes e Saídas de Dados
- **Fonte:** `https://api.coinbase.com/v2/prices/BTC-USD/spot` (valor configurável via `.env`).
- **Banco SQLite (`crypto_prices.db`):** tabela `prices` com colunas `timestamp` (`TEXT`) e `price` (`REAL`).
- **CSV (`crypto_prices.csv`):** mesmas colunas do banco, útil para consumo por ferramentas de BI como Power BI.
- Os caminhos padrão podem ser personalizados via variáveis de ambiente `DATABASE_PATH` e `CSV_PATH`.

## Monitoramento e Troubleshooting
- Verifique conectividade com a API executando `Invoke-WebRequest` ou `requests.get` diretamente no console.
- Caso o arquivo CSV esteja aberto em outra aplicação, a função `export_csv` retornará exceção de permissão; feche o arquivo antes de novas execuções.
- Consulte `pipeline.log` para detalhes de execução e mensagens de erro.
- Utilize ferramentas como DB Browser for SQLite para inspecionar a evolução dos dados.
- Configure alertas por e-mail para receber notificações de falhas críticas e evitar indisponibilidade prolongada.

## Próximos Passos
- Adicionar testes automatizados para validar cada etapa do pipeline.
- Versionar múltiplos pares de moedas e habilitar ingestão paralela.
- Integrar com um orquestrador (Airflow, Prefect ou Dagster) para dependências complexas e monitoramento centralizado.

