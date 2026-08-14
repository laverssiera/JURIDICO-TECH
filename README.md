# JURIDICOTECH

[![Backend CI](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-ci.yml)
[![Backend NATS E2E](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-nats-e2e.yml/badge.svg)](https://github.com/laverssiera/JURIDICO-TECH/actions/workflows/backend-nats-e2e.yml)

**JURIDICOTECH - Infraestrutura Legal da Civilização**

Runtime jurídico escalável que evolui de plataforma corporativa para **guardião legal da inovação científica e governança civilizacional planetária e interplanetária**.

**Missão Expandida**:
- Garantir que descobertas científicas sejam protegidas dentro de compliance
- Manter conhecimento produzido rastreável e auditar contratos científicos
- Preservar patentes, autoria e soberania intelectual multiinstitucional
- Estabelecer governança para programas globais e interplanetários
- Assegurar que toda inovação tenha finalidade civilizacional

### Camada Federativa + Interplanetária

JURIDICOTECH passa a operar como runtime legal soberano do ecossistema, com foco em:

- Interplanetary Legal Runtime para pesquisa, tratados e operações planetárias
- Sovereign Compliance Engine para compliance científico e financeiro
- Patent Intelligence Network para proteção de autoria e descoberta
- Regulatory AI Mesh para validação de AGI e automação extrema
- Treaty & Space Law Runtime para operações orbitais e interplanetárias

Integrações canônicas:

- P&D
- Academia do Saber
- CEA Investimentos
- Econotech
- Game MKT
- Archimedes
- Hub Backoffice
- Fornecedores
- Opera
- BIMARQENG
- John Brasileiro
- Cefeida 3C273

### Camadas LICEU 6.x + Cosmic Law (1-17)

**Camadas 1-13** (Legal Corporativo):
1. Digital Twin Jurídico | 2. Regulatory Radar Global | 3. Autonomous Arbitration
4. Legal War Room | 5. Psycholegal | 6. ESG + Human Rights | 7. Smart Clause
8. Legal Knowledge Graph | 9. Legal OS Runtime | 10. Trust Engine
11. Governance AI | 12. Marketplace Jurídico | 13. Universidade Jurídica

**Camadas 14-17** (Cosmic Law - Scientific Governance):
14. **Interplanetary Governance Layer** - Regulação jurídica de pesquisas orbitais, laboratórios extremos, habitats oceânicos e lunares
15. **Scientific Sovereignty Engine** - Proteção de autoria, descoberta, datasets científicos, modelos IA, algoritmos e processos industriais
16. **Planetary Compliance Engine** - Compliance para ESG global, tratados científicos, ética IA, bioengenharia, segurança quântica
17. **Civilizational IP Runtime** - Sistema operacional de propriedade intelectual que controla patentes, royalties, licenciamento, coautoria e transferência tecnológica

## Visão de Arquitetura

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
│   ├── mobile-field-app/
│   ├── interplanetary-law-runtime/
│   ├── patent-intelligence-engine/
│   ├── scientific-compliance-runtime/
│   ├── orbital-regulatory-radar/
│   ├── sovereign-governance-runtime/
│   ├── legal-war-room/
│   ├── treaty-engine/
│   ├── space-law-runtime/
│   ├── ai-regulation-runtime/
│   └── research-protection-runtime/
├── packages/
│   ├── ui-kit/
│   ├── legal-sdk/
│   ├── nats-sdk/
│   ├── auth-sdk/
│   ├── legal-events/
│   ├── design-system/
│   ├── federation-sdk/
│   ├── observability-sdk/
│   ├── ecosystem-memory-sdk/
│   ├── causal-sdk/
│   └── legal-knowledge-sdk/
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

## Estado Atual da Implementação

**Status**: Fase 2 → Fase 5 (mai/2026) - Transição de Legal Corporativo para *Scientific Governance*

### Core Domains (Fase 1-2)
- **Legal Core**: Contratos, Compliance, Governança, Risco Legal, Arbitragem, Jurisprudência, IA Legal
- **Phase 2 Domains**: Tax, Corporate, Litigation, Forensic, Legal NLP, Evidence Vault
- **Services**: Módulo Preventivo, Aprendizado Contratual, Arbitration Service

### Scientific Governance Domains (Fase 5+)
- **Scientific Authorship Engine** - Registro de autoria, contribuição intelectual, cadeia de descoberta
- **Patent & Discovery Engine** - Controle de patentes, compósitos, materiais, algoritmos, sistemas energéticos
- **Interplanetary Research Compliance** - Compliance para pesquisas espaciais, oceânicas, quânticas, nucleares
- **Orbital & Space Law Engine** - Regulação de laboratórios orbitais, mineração espacial, habitats lunares/marcianos
- **Deep Ocean Law Engine** - Governança para cidades submersas, construção oceânica, laboratórios marítimos
- **AI Ethics & AGI Governance** - Regulação de AGI, IA científica, IA autônoma
- **Quantum & Fusion Regulation** - Compliance de computação quântica, fusão nuclear, sistemas energéticos
- **Civilizational Impact Engine** - Análise de impacto social, benefício coletivo, prioridade de habitação

### WAVE 43 — JURIDICOTECH

A WAVE 43 consolida o estado jurídico continental em cinco tracks operacionais:

- **Legal State**: estado jurídico por países, rota e operação.
- **Contracts**: lei aplicável, cláusulas obrigatórias e avaliação cross-border.
- **Regulation**: bundles normativos por país e conflitos regulatórios.
- **IP**: cobertura de proteção intelectual, lacunas e índice de cobertura.
- **Compliance**: regras exigidas, controles ausentes e score de conformidade.

Endpoints:

- `GET /legal/waves/43` — manifesto da wave e payloads de referência.
- `POST /legal/continental/state` — avaliação consolidada da operação.

### Infraestrutura Backend
- Backend principal em `backend/` com FastAPI, tenant middleware, NATS integration completa
- Novo domínio em `apps/interplanetary-governance/` com sub-engines especializados
- Legal Event Registry com 50+ NATS subjects (+ 8 novos para scientific governance)
- SQL base expandida com tabelas para autoria científica, patentes, pesquisa, impacto civilizacional
- Nova camada federativa em `apps/interplanetary-law-runtime/` com NATS, Neo4j, Redis, Prometheus e causal runtime
- SDKs compartilhados em `packages/federation-sdk/`, `packages/observability-sdk/`, `packages/ecosystem-memory-sdk/`, `packages/causal-sdk/` e `packages/legal-knowledge-sdk/`

### Testes
- Backend: `pytest -q` → 76 passed, 1 skipped (última execução: 2026-05-07)
- E2E NATS: Testes de integração com event bus canônico
- Scientific compliance validation (em construção)

## Stack de Producao Prevista

- Backend: FastAPI, PostgreSQL, Redis, NATS JetStream, SQLAlchemy Async, Alembic.
- IA e dados: LangChain, pgvector, Neo4j, YOLOv8, RAG jurídico.
- Observabilidade: OpenTelemetry, Prometheus, Grafana, Loki, Tempo, Jaeger.
- Seguranca: JWT, OAuth2, RBAC, mTLS, HMAC, audit trail.
- Scientific Governance: Knowledge Graphs, Patent databases, Research registries, Impact analysis engines

## 🚀 Cosmic Law - Scientific Governance APIs

### 1. Scientific Authorship Engine (`/science/authorship/`)
Registro e validação de autoria científica, contribuição intelectual e cadeia de descoberta.

```
POST   /science/authorship/register      # Registrar nova autoria
POST   /science/authorship/validate      # Validar autoria (conflict resolution)
GET    /science/authorship/history/{id}  # Histórico de descoberta
POST   /science/authorship/dispute       # Registrar disputa de autoria
GET    /science/authorship/credits/{exp} # Créditos por experimento
```

### 2. Patent & Discovery Engine (`/patents/`)
Controle de patentes, compósitos, materiais, algoritmos, sistemas energéticos.

```
POST   /patents/register               # Registrar nova patente/descoberta
POST   /patents/analyze-novelty        # Análise de novidade
POST   /patents/validate-prior-art     # Validar prior art
POST   /patents/license                # Criar licença
GET    /patents/{id}                   # Detalhes da patente
POST   /patents/royalty/calculate      # Calcular royalties
GET    /patents/portfolio/{owner}      # Portfolio intelectual
```

### 3. Interplanetary Research Compliance (`/research/`)
Compliance para pesquisas espaciais, oceânicas, quânticas, nucleares, IA avançada.

```
POST   /research/compliance/check       # Verificar compliance
POST   /research/compliance/approve     # Aprovar pesquisa
POST   /research/compliance/block       # Bloquear por risco
GET    /research/compliance/history     # Histórico de aprovações
POST   /research/risk/assess            # Avaliação de risco
GET    /research/categories             # Listar categorias de pesquisa
```

### 4. Orbital & Space Law Engine (`/space/`)
Regulação de laboratórios orbitais, mineração espacial, habitats lunares, satélites científicos.

```
POST   /space/treaty/analyze            # Analisar compliance de tratado
POST   /space/habitat/compliance        # Validar habitat orbital/lunar
POST   /space/mining/risk               # Análise de risco de mineração
POST   /space/mission/legal-review      # Revisão jurídica de missão
GET    /space/jurisdiction/{zone}       # Lei aplicável por zona
```

### 5. Deep Ocean Law Engine (`/oceanic/`)
Governança para cidades submersas, construção oceânica, laboratórios marítimos, infraestrutura extrema.

```
POST   /oceanic/habitat/legal-check     # Validar habitat oceânico
POST   /oceanic/material/compliance     # Compliance de materiais exóticos
POST   /oceanic/environmental-risk      # Análise de risco ambiental
POST   /oceanic/treaty/validate         # Validar tratado oceânico
GET    /oceanic/depth-zones             # Jurisdição por profundidade
```

### 6. AI Ethics & AGI Governance (`/ai/governance/`)
Governança jurídica de AGI, IA científica, IA decisória, IA autônoma.

```
POST   /ai/governance/audit             # Auditoria de IA
POST   /ai/governance/risk              # Avaliação de risco AGI
POST   /ai/governance/ethics-check      # Validação ética
POST   /ai/governance/runtime-monitor   # Monitoramento em runtime
GET    /ai/governance/transparency/{id} # Explainability audit trail
```

### 7. Quantum & Fusion Regulation (`/quantum/`, `/fusion/`)
Compliance de computação quântica, fusão nuclear, sistemas energéticos extremos.

```
POST   /quantum/compliance/check         # Compliance quântico
POST   /quantum/encryption/audit         # Auditoria de criptografia quântica
POST   /fusion/reactor/audit             # Auditoria de reator de fusão
POST   /fusion/risk/analyze              # Análise de risco nuclear
GET    /quantum/entanglement-log/{id}    # Log de entrelaçamento
```

### 8. Civilizational Impact Engine (`/civilization/`)
Garantir inovação com impacto social positivo, habitação, infraestrutura acessível.

```
POST   /civilization/impact/analyze      # Análise de impacto civilizacional
POST   /civilization/ethics/check        # Validação ética de projeto
POST   /civilization/social-benefit/score # Score de benefício social
POST   /civilization/habitat/priority    # Validar priorização de habitação
GET    /civilization/impact-metrics      # Métricas de impacto global
```

## Quick Start

### 1) Backend API

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main  # ou uvicorn app.main:app --reload
```

**Rodando testes**:
```bash
cd backend
pytest -q  # rápido
pytest -v  # verbose
```

**Endpoints principais**:

**Legal Admin** (`/legal/*`):
- `POST /legal/create-spe` - Criar SPE (Sociedade em Participações)
- `POST /legal/audit-contract` - Auditoria de contrato
- `POST /legal/norms-alerts` - Alertas de normas
- `POST /legal/compliance-check` - Verificação de compliance

**LICEU Jurídico** (`/liceu/*`):
- `/liceu/preventivo` - Módulo preventivo e conformidade
- `/liceu/aprendizado` - Sistema de aprendizado contratual
- `/liceu/arbitragem` - Arbitragem autônoma
- `/liceu/governanca` - Governança corporativa
- `/liceu/tributario` - Compliance tributário
- `/liceu/societario` - Direito societário
- `/liceu/contencioso` - Litigância
- `/liceu/forense` - Análise forense
- `/liceu/nlp` - Processamento de linguagem natural
- `/liceu/cofre` - Evidence vault
- `/liceu/simulacao-global` - Simulação global de cenários legais

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

## Event Bus Canônico (NATS)

**Legal Event Registry** com 50+ subjects registrados:

**Core Legal Events** (13):
- `legal.contract.created` - Contrato criado
- `legal.contract.signed` - Contrato assinado
- `legal.contract.breach` - Violação de contrato
- `legal.arbitration.started` - Arbitragem iniciada
- `legal.arbitration.closed` - Arbitragem encerrada
- `legal.compliance.alert` - Alerta de compliance
- `legal.audit.created` - Auditoria criada
- `legal.embargo.detected` - Embargo detectado
- `legal.sst.violation` - Violação de segurança
- `legal.esg.alert` - Alerta ESG
- `legal.tax.risk` - Risco tributário
- `legal.governance.blocked` - Governança bloqueada
- `legal.pericia.generated` - Perícia gerada

**Simulation Events** (2):
- `simulation.global.executed` - Simulação global executada
- `simulation.global.risk.high` - Risco alto identificado

**Scientific Governance Events** (8):
- `science.authorship.registered` - Autoria científica registrada
- `science.discovery.validated` - Descoberta validada
- `science.discovery.disputed` - Disputa de autoria
- `patent.created` - Patente criada
- `patent.approved` - Patente aprovada
- `patent.licensed` - Patente licenciada
- `research.compliance.approved` - Pesquisa aprovada
- `research.compliance.blocked` - Pesquisa bloqueada

**Space & Planetary Events** (4):
- `space.mission.legal.approved` - Missão espacial aprovada
- `space.treaty.violation` - Violação de tratado espacial
- `oceanic.habitat.compliant` - Habitat oceânico em compliance
- `planetary.treaty.registered` - Tratado planetário registrado

**AGI & Advanced Tech Events** (3):
- `ai.governance.alert` - Alerta de AGI/IA
- `agi.ethics.violation` - Violação ética de AGI
- `quantum.runtime.risk.detected` - Risco quântico detectado

**Impact & Civilization Events** (2):
- `fusion.reactor.audit.completed` - Auditoria de fusão concluída
- `civilization.impact.assessed` - Impacto civilizacional avaliado

Ver `packages/legal-events/` para estrutura completa e tipagem NATS envelope.

### ⚠️ Notas de Compatibilidade

- Evento `contract.signed` é consumido por subscriber legado que exige: `monolito_id`, `spe_name`, `partners`, `purpose` - manter payload compatível ao publicar novos fluxos.
- TestClient global sem context manager pode não disparar startup/lifespan - registre subscribers críticos também no bootstrap quando necessário.

## 🛡️ Civilization War Room

Central jurídica e científica para:
- **Crises Regulatórias** - Conflitos de normas planetárias e interplanetárias
- **Conflitos de Patente** - Disputas de autoria e propriedade intelectual
- **Vazamentos Científicos** - Proteção de pesquisa sensível
- **Riscos AGI** - Monitoramento de IA autônoma e AGI
- **Conflitos Internacionais** - Disputas entre nações e instituições
- **Disputas Científicas** - Validação de descobertas e autoria

**Interfaces**:
- Real-time monitoring de events NATS críticos
- Escalação automática para John Civilizational Counsel
- Análise de impacto civilizacional
- Recomendações de resolução baseadas em jurisprudência
- Rastreamento de precedentes científicos

## 🧠 John Jurídico → John Civilizational Counsel

Evolução de General Counsel Cognitivo para **Civilizational Intelligence System**:

**Funções Novas**:
- Prever conflitos regulatórios em pesquisa global
- Antecipar riscos de patentes e descobertas
- Validar tratados científicos e espaciais
- Sugerir compliance para projetos extremos
- Proteger autoria e soberania intelectual
- Priorizar benefício social em inovações
- Monitorar AGI ethics em runtime
- Assessorar habitats extremos e construção planetária

**Dados que Consome**:
- Legal precedents repository
- Scientific authorship database
- Patent registries (global + space-based)
- AGI ethics audit logs
- Impact assessment metrics

## 📊 Novas Tabelas SQL (Cosmic Law)

```sql
CREATE TABLE scientific_authorship (
    id UUID PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    contribution_type TEXT, -- 'discovery', 'methodology', 'validation', 'improvement'
    contribution_score NUMERIC(5,2),
    institution TEXT,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE patents_registry (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT, -- 'material', 'algorithm', 'process', 'energy', 'quantum', 'fusion'
    description TEXT,
    novelty_score NUMERIC(5,2),
    prior_art_checked BOOLEAN,
    status TEXT, -- 'draft', 'filed', 'approved', 'licensed'
    owner_id TEXT,
    owner_institution TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP
);

CREATE TABLE interplanetary_research (
    id UUID PRIMARY KEY,
    research_type TEXT, -- 'space', 'oceanic', 'quantum', 'fusion', 'biotech', 'agi'
    risk_level TEXT, -- 'low', 'medium', 'high', 'critical'
    compliance_status TEXT, -- 'pending', 'approved', 'blocked', 'suspended'
    jurisdiction_scope TEXT, -- 'earth', 'orbit', 'lunar', 'mars', 'ocean', 'multi-planetary'
    researcher_id TEXT,
    institution TEXT,
    reviewed_by TEXT,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP
);

CREATE TABLE civilizational_impact (
    id UUID PRIMARY KEY,
    project_id TEXT NOT NULL,
    project_name TEXT,
    housing_impact NUMERIC(5,2), -- -100 to 100
    infrastructure_impact NUMERIC(5,2), -- -100 to 100
    social_benefit_score NUMERIC(5,2), -- 0 to 100
    environmental_impact NUMERIC(5,2), -- -100 to 100
    global_benefit BOOLEAN,
    accessibility_score NUMERIC(5,2),
    assessed_by TEXT,
    final_score NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    assessed_at TIMESTAMP
);

CREATE TABLE agora_covenant (
    id UUID PRIMARY KEY,
    treaty_type TEXT, -- 'scientific', 'space', 'oceanic', 'quantum', 'fusion'
    parties TEXT[], -- Array de partes/instituições
    terms TEXT,
    binding_level TEXT, -- 'advisory', 'recommended', 'binding'
    compliance_mandatory BOOLEAN,
    status TEXT, -- 'draft', 'active', 'archived'
    created_at TIMESTAMP DEFAULT NOW(),
    activated_at TIMESTAMP
);
```

## Roadmap LICEU 6.0 → Cosmic Law

### Legal Corporativo (Fases 1-4)
- **Fase 1** ✅: Contratos, compliance, RBAC, auditoria, frontend base
- **Fase 2** ✅: AI, RAG, arbitragem, perícia, novos domínios (tax, corporate, litigation, forensic)
- **Fase 3** 🚀: War room jurídico, graph intelligence, legal predictive
- **Fase 4** 📋: Governance engine global, marketplace jurídico escalável

### Scientific Governance (Fases 5-9)
- **Fase 5** 🔬: Scientific authorship engine, cadeia de descoberta, proteção de datasets
- **Fase 6** 🧬: Patent & discovery engine, prior art validation, royalty management
- **Fase 7** 🌍: Planetary compliance engine (IA ethics, bioengenharia, quântica, fusão, oceânico)
- **Fase 8** 🚀: Interplanetary governance (habitats extremos, orbital law, tratados científicos)
- **Fase 9** 🌱: Civilizational governance (impacto social, benefício coletivo, habitação global)

## 🌌 Visão Final: JURIDICOTECH como Infraestrutura Legal da Civilização

**Evolução da Plataforma**:

JURIDICOTECH deixa de ser apenas um sistema jurídico corporativo.

Ele passa a ser:

1. **Infraestrutura Legal da Civilização** do ecossistema global e interplanetário
2. **Guardião de Inovação** - Proteção da descoberta científica e soberania intelectual
3. **Proteção Jurídica da Ciência** - Compliance em pesquisa avançada sem frear inovação
4. **Sistema Operacional de Soberania Intelectual** - IP runtime que controla patentes, royalties e créditos
5. **Camada Regulatória Planetária** - Compliance para IA, bioengenharia, quântica, fusão, oceânico
6. **Governança Jurídica de Engenharia Planetária e Interplanetária** - Habitats extremos, tratados científicos

**Princípios Fundadores**:
- ✅ Descobertas científicas devem ser protegidas dentro de compliance
- ✅ Pesquisas avançam em segurança jurídica
- ✅ Conhecimento produzido permanece rastreável
- ✅ Contratos científicos são auditar levando em conta transparência
- ✅ Patentes e autoria são preservadas multiinstitucionalmente
- ✅ Programas planetários e interplanetários têm governança clara
- ✅ Toda inovação tem finalidade civilizacional

**Alcance**:
- 13 camadas jurídicas corporativas (LICEU 1-13)
- 4 camadas de Cosmic Law (LICEU 14-17)
- 8 domínios científicos especializados
- 50+ NATS event subjects
- 5 tabelas SQL para scientific governance
- 1 Civilization War Room
- 1 John Civilizational Counsel cognitivo

## Desenvolvimento

### Variáveis de Ambiente

Ver `.env.example` ou documentação de cada aplicação em `apps/*/README.md`.

### CI/CD

- GitHub Actions workflows em `infra/github-actions/`
- Backend CI: executado em push/PR para `backend/**`
- NATS E2E: validação de event bus

### Documentação

- **Arquitetura**: [docs/](docs/)
- **Cosmic Law**:
  - [INTERPLANETARY_GOVERNANCE.md](docs/INTERPLANETARY_GOVERNANCE.md)
  - [SCIENTIFIC_IP_RUNTIME.md](docs/SCIENTIFIC_IP_RUNTIME.md)
  - [SPACE_LAW_ENGINE.md](docs/SPACE_LAW_ENGINE.md)
  - [OCEANIC_INFRASTRUCTURE_LAW.md](docs/OCEANIC_INFRASTRUCTURE_LAW.md)
  - [AGI_ETHICS_RUNTIME.md](docs/AGI_ETHICS_RUNTIME.md)
  - [CIVILIZATIONAL_GOVERNANCE.md](docs/CIVILIZATIONAL_GOVERNANCE.md)
  - [PATENT_AND_DISCOVERY_ENGINE.md](docs/PATENT_AND_DISCOVERY_ENGINE.md)
- **API docs** (backend): `http://localhost:8000/docs` (Swagger)
- **Infra**: `infra/README.md`
