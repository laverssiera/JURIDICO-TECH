# JuridicoTech Core (isolado)

Core juridico modular com:
- contratos versionados
- anti-bypass
- risk engine
- eventos (NATS)
- integracao core_dna
- RBAC simplificado
- auditoria
- stream WebSocket para mesa juridica

## Estrutura

- main.py
- core/db.py
- core/rbac.py
- core/audit.py
- modules/contracts.py
- modules/risk.py
- modules/bypass.py
- modules/events.py
- integrations/nats.py
- integrations/core_dna.py
- sql/schema.sql

## Rodar local

```bash
cd backend
uvicorn juridicotech.main:app --reload --host 0.0.0.0 --port 8010
```

Healthcheck:

```bash
curl http://localhost:8010/health
```

## Variaveis de ambiente

- DATABASE_URL: PostgreSQL do core (default em core/db.py)
- JURIDICO_INIT_SCHEMA=1: aplica schema.sql no startup
- NATS_URL=nats://localhost:4222: habilita conexao no startup
- CORE_DNA_URL=http://localhost:7000/decide

## Fluxo E2E (API)

1) POST /events/deal-created
2) Core cria contrato automatico
3) Core avalia risco
4) Core consulta core_dna
5) retorna decisao bloqueio/liberacao

Eventos emitidos no barramento/app:

- legal.contract.created
- legal.risk.update
- legal.risk.flagged

WebSocket de stream em tempo real (app principal):

- ws://localhost:8000/events/ws

## Orquestrador NATS

Consumidor dedicado:

```bash
cd backend
python -m juridicotech.modules.events_engine
```

Ele consome `deal.created` e publica:

- legal.contract.created
- legal.risk.update
- legal.risk.flagged (quando risco alto)

## SDK Node

Arquivo: ../sdk/juridico-sdk.js

## Trading Desk React

Microfrontend React dedicado:

```bash
cd frontend/legal-trading-desk
npm install
npm run dev
```

Componente principal: `src/LegalTradingDesk.jsx`
