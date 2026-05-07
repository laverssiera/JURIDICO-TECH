# JURIDICO-TECH (Backend)

[![Backend CI](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-ci.yml)
[![Backend NATS E2E](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-nats-e2e.yml/badge.svg)](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-nats-e2e.yml)

API jurídica construída com FastAPI para suportar fluxos de serviços societários, análise contratual, radar normativo e compliance.

## Stack

- Python 3.11+
- FastAPI
- Uvicorn
- Pytest

## Estrutura

```text
backend/
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── routers/
│   ├── services/
│   ├── integration/
│   └── john/
├── tests/
├── requirements.txt
└── pytest.ini
```

## Como rodar o backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Documentacao interativa:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints ativos

### Health/Info

- `GET /`

### Servicos juridicos

- `POST /legal/create-spe`
- `POST /legal/contract/analyze`

### Radar legal

- `GET /legal/radar/alerts`

### Compliance

- `POST /legal/compliance/check/{monolito_id}`
- `POST /legal/compliance/check`

### Hub legal layer

- `POST /legal/gate/validate`
- `POST /legal/lock`
- `GET /legal/lock/{entity_id}`
- `GET /legal/snapshot/{entity_id}`
- `POST /legal/decision`
- `POST /legal/payment/authorize`
- `GET /legal/audit`
- `POST /legal/events/consume`
- `POST /legal/bypass/detect`

### Ecossistema juridico (issues base)

- `POST /legal/identity/entities`
- `POST /legal/identity/users`
- `POST /legal/rbac/grant`
- `GET /legal/rbac/{user_id}`
- `POST /legal/templates`
- `GET /legal/templates`
- `POST /legal/contracts/v2`
- `POST /legal/contracts/v2/{contract_id}/version`
- `POST /legal/contracts/v2/{contract_id}/status`
- `POST /legal/contracts/v2/{contract_id}/sign`
- `POST /legal/contracts/v2/{contract_id}/digital-sign`
- `POST /legal/contracts/v2/{contract_id}/verify-signature`
- `GET /legal/contracts/v2/{contract_id}/custody`
- `POST /legal/contracts/v2/{contract_id}/verify-custody`
- `GET /legal/contracts`
- `POST /legal/bypass/protect`
- `POST /legal/bypass/check`
- `POST /legal/risk/analyze`
- `POST /legal/risk/ingest`
- `GET /legal/risk`
- `GET /legal/risk/center`
- `POST /legal/audit/immutable`
- `GET /legal/audit/immutable`
- `POST /legal/sla`
- `POST /legal/tasks`
- `GET /legal/tasks`
- `POST /legal/override`
- `POST /legal/core-dna/analyze`
- `POST /legal/john/decision`
- `POST /legal/learning`
- `GET /legal/learning`
- `POST /legal/tasks/{task_id}/stage`
- `GET /legal/notifications`

### Integracao de eventos

- `POST /integration/events/contract.signed`

## Exemplos rapidos

Criar SPE:

```bash
curl -X POST http://localhost:8000/legal/create-spe \
	-H "Content-Type: application/json" \
	-d '{
		"name": "Residencial Aurora",
		"partners": ["ARCHIMEDES", "CEA INVESTIMENTOS"],
		"purpose": "Incorporacao imobiliaria"
	}'
```

Analisar contrato:

```bash
curl -X POST http://localhost:8000/legal/contract/analyze \
	-H "Content-Type: application/json" \
	-d '{
		"title": "Contrato de Compra e Venda",
		"content": "A multa e integral para o comprador e nao ha clausula de protecao de dados."
	}'
```

Disparar fechamento automatico ao assinar contrato:

```bash
curl -X POST http://localhost:8000/integration/events/contract.signed \
	-H "Content-Type: application/json" \
	-d '{
		"contract_id": "CTR-2026-001",
		"monolito_id": "backoffice",
		"spe_name": "Residencial Horizonte",
		"partners": ["ARQUITETA HOLDING", "CEA INVESTIMENTOS"],
		"purpose": "Incorporacao imobiliaria"
	}'
```

## Testes

```bash
cd backend
pytest
```

Teste E2E opcional com NATS JetStream real:

```bash
cd backend
RUN_NATS_E2E=1 pytest -q tests/test_nats_e2e.py
```

CI no GitHub Actions:

- Workflow padrão: `.github/workflows/backend-ci.yml`
- Workflow E2E opcional/manual: `.github/workflows/backend-nats-e2e.yml`

## Persistencia do Core Juridico

- Padrao local: SQLite em `/tmp/juridico_legal_core.db`
- PostgreSQL: defina `LEGAL_CORE_DB_URL` ou `DATABASE_URL`

Exemplo:

```bash
export LEGAL_CORE_DB_URL=postgresql://usuario:senha@localhost:5432/juridicotech
```

- Se usar PostgreSQL, instale as dependencias do arquivo `requirements.txt` antes de subir a API.

## Event Bus NATS

- O backend continua funcionando sem broker, usando fallback local em memoria.
- Para habilitar NATS real, defina `NATS_URL`.
- Retries de conexao: `NATS_CONNECT_RETRIES` e `NATS_RETRY_DELAY_MS`.

Exemplo:

```bash
export NATS_URL=nats://localhost:4222
export NATS_CONNECT_RETRIES=3
export NATS_RETRY_DELAY_MS=250
```

Subjects consumidos/publicados pelo core:

Subjects canonicos:

- `liceu.events.leads.created`
- `liceu.events.deals.match_generated`
- `liceu.events.deals.created`
- `liceu.events.deals.simulation_done`
- `liceu.events.deals.won`
- `liceu.events.legal.contract.required`
- `liceu.events.legal.contract.generated`
- `liceu.events.legal.contract.signed`
- `liceu.events.legal.blocked`
- `liceu.events.legal.approved`
- `liceu.events.legal.bypass.detected`
- `liceu.events.legal.commission.protected`

Padrões reservados:

- `liceu.events.leads.*`
- `liceu.events.deals.*`
- `liceu.events.legal.*`
- `liceu.commands.legal.*`

Aliases legados ainda aceitos na assinatura remota:

- `juridicotech.contract.signed`
- `juridicotech.lead_created`
- `juridicotech.deal_created`
- `juridicotech.match_generated`
- `juridicotech.deal_won`

## CORE_DNA protobuf

- Contrato protobuf: `core_dna/legal.proto`
- Compile os artefatos Python com:

```bash
cd backend
python -m grpc_tools.protoc -I./core_dna --python_out=./core_dna/compiled ./core_dna/legal.proto
```

- Consumer JetStream: `app/consumers/legal_consumer.py`
- Publisher jurídico: `app/publishers/legal_publisher.py`
- Adapter SDK para monólitos: `sdk/legal_adapter.py`

## Frontend (resumo)

O frontend Vue esta na pasta `../frontend`.

Para executar:

```bash
cd frontend
npm install
npm run dev
```

## Observacoes

- Existem comentarios no codigo com endpoints planejados que ainda nao foram implementados.
- Este README descreve apenas os endpoints atualmente expostos em `app/main.py`.
- O adapter interno para uso do Hub esta em `app/services/legal_adapter.py`.
