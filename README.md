# JURIDICOTECH

[![Backend CI](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-ci.yml)
[![Backend NATS E2E](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-nats-e2e.yml/badge.svg)](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-nats-e2e.yml)

LICEU 6.0: runtime juridico, compliance engine, arbitration engine, forensic center, governance engine e legal intelligence para engenharia e construcao.

## Visao de Arquitetura

```text
juridicotech/
├── apps/
│   ├── backend-api/
│   ├── legal-ai/
│   ├── arbitration-engine/
│   ├── forensic-engine/
│   ├── compliance-engine/
│   ├── contract-engine/
│   ├── legal-event-gateway/
│   ├── legal-worker/
│   ├── legal-marketplace/
│   ├── legal-public-site/
│   ├── legal-control-center/
│   └── mobile-field-app/
├── packages/
│   ├── ui-kit/
│   ├── legal-sdk/
│   ├── nats-sdk/
│   ├── auth-sdk/
│   ├── legal-events/
│   └── design-system/
├── infra/
│   ├── kubernetes/
│   ├── terraform/
│   ├── docker/
│   ├── github-actions/
│   ├── observability/
│   └── helm/
├── datasets/
├── docs/
├── scripts/
└── README.md
```

## Estado Atual do Scaffold

- Monorepo workspaces na raiz com scripts para backend-api e legal-control-center.
- Backend principal em apps/backend-api com FastAPI, tenant middleware, routers de contratos/arbitragem/compliance e health check.
- SQL base com tabelas legais em apps/backend-api/sql/schema.sql.
- NATS subjects e envelope tipado em packages/legal-events.
- Infra inicial com docker compose, manifests Kubernetes, Terraform baseline e Helm chart API.

## Stack de Producao Prevista

- Backend: FastAPI, PostgreSQL, Redis, NATS JetStream, SQLAlchemy Async, Alembic.
- IA e dados: LangChain, pgvector, Neo4j, YOLOv8, RAG juridico.
- Observabilidade: OpenTelemetry, Prometheus, Grafana, Loki, Tempo, Jaeger.
- Seguranca: JWT, OAuth2, RBAC, mTLS, HMAC, audit trail.

## Quick Start

### 1) Backend API (novo scaffold)

```bash
cd apps/backend-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints iniciais:

- GET /health
- POST /contracts/
- POST /arbitration/start
- POST /compliance/check

### 2) Legal Control Center (Next.js)

```bash
cd apps/legal-control-center
npm install
npm run dev
```

### 3) Stack local com Docker

```bash
cd infra/docker
docker compose up -d
```

## Event Bus Canonico (NATS)

- legal.contract.created
- legal.contract.signed
- legal.contract.breach
- legal.arbitration.started
- legal.arbitration.closed
- legal.compliance.alert
- legal.audit.created
- legal.pericia.generated
- legal.embargo.detected
- legal.asset.risk
- legal.sst.violation
- legal.esg.alert
- legal.tax.risk
- legal.governance.blocked

## Roadmap LICEU 6.0

- Fase 1: contratos, compliance, RBAC, auditoria, frontend base.
- Fase 2: AI, RAG, arbitragem, pericia.
- Fase 3: war room, graph intelligence, predictive legal.
- Fase 4: global governance engine.
