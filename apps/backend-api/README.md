# Backend API (JURIDICOTECH)

## Federation Backends

O runtime federado suporta seleção de backend por ambiente com fallback automático.

### Variáveis

Use as variáveis abaixo no arquivo .env (base em .env.example):

- FEDERATION_MEMORY_BACKEND=auto|memory|redis
- FEDERATION_GRAPH_BACKEND=auto|memory|neo4j
- FEDERATION_OBSERVABILITY_BACKEND=auto|memory|otel

Infra associada:

- NATS_URL
- REDIS_HOST
- REDIS_PORT
- REDIS_DB
- REDIS_PASSWORD
- NEO4J_URI
- NEO4J_USER
- NEO4J_PASSWORD
- OTEL_EXPORTER_OTLP_ENDPOINT

### Modos Recomendados

Desenvolvimento local sem serviços externos:

```bash
FEDERATION_MEMORY_BACKEND=memory
FEDERATION_GRAPH_BACKEND=memory
FEDERATION_OBSERVABILITY_BACKEND=memory
```

Modo automático (tenta serviço real e faz fallback):

```bash
FEDERATION_MEMORY_BACKEND=auto
FEDERATION_GRAPH_BACKEND=auto
FEDERATION_OBSERVABILITY_BACKEND=auto
```

Modo com serviços reais obrigatórios:

```bash
FEDERATION_MEMORY_BACKEND=redis
FEDERATION_GRAPH_BACKEND=neo4j
FEDERATION_OBSERVABILITY_BACKEND=otel
```

### Diagnóstico de Backends Ativos

Endpoint de diagnóstico:

- GET /federation/legal/diagnostics/backends

Esse endpoint retorna:

- configured: backend configurado por variável de ambiente
- effective: backend efetivamente ativo em runtime
- connection: dados de conexão de NATS, Redis, Neo4j e OTel

Resumo agregado com diagnóstico também disponível em:

- GET /federation/legal/summary

### Exemplos de .env por Cenário

#### 1) Somente memória local

```env
FEDERATION_MEMORY_BACKEND=memory
FEDERATION_GRAPH_BACKEND=memory
FEDERATION_OBSERVABILITY_BACKEND=memory
NATS_URL=nats://localhost:4222
```

#### 2) Auto com fallback

```env
FEDERATION_MEMORY_BACKEND=auto
FEDERATION_GRAPH_BACKEND=auto
FEDERATION_OBSERVABILITY_BACKEND=auto
REDIS_HOST=localhost
REDIS_PORT=6379
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=liceu
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

#### 3) Serviços reais obrigatórios

```env
FEDERATION_MEMORY_BACKEND=redis
FEDERATION_GRAPH_BACKEND=neo4j
FEDERATION_OBSERVABILITY_BACKEND=otel
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=liceu
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

## Bootstrap Rápido

### 1. Preparar ambiente

```bash
cp .env.example .env
pip install -r requirements.txt
```

### 2. Subir infraestrutura opcional

Se quiser testar os modos redis, neo4j e otel com serviços reais:

```bash
docker compose -f /workspaces/JURIDICO-TECH/docker-compose.federation.yml up -d
```

### 3. Subir a API

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Validar diagnóstico de backend

```bash
curl -s http://127.0.0.1:8000/federation/legal/diagnostics/backends | cat
curl -s http://127.0.0.1:8000/federation/legal/summary | cat
```

### 5. Rodar testes de sanidade

```bash
pytest tests/test_federation_runtime.py tests/test_health.py -q
```

## Utilitario de Troca de Perfil

Script:

- ./scripts/switch_federation_profile.sh
- make profile-local | make profile-auto | make profile-real

Exemplos:

```bash
./scripts/switch_federation_profile.sh local
./scripts/switch_federation_profile.sh auto
./scripts/switch_federation_profile.sh real
./scripts/switch_federation_profile.sh real --dry-run

make profile-local
make profile-auto
make profile-real
make profile-real-dry-run
```

Comportamento:

- Atualiza somente:
	- FEDERATION_MEMORY_BACKEND
	- FEDERATION_GRAPH_BACKEND
	- FEDERATION_OBSERVABILITY_BACKEND
- Cria backup de .env antes de aplicar (pode desativar com --no-backup)
