-- JURIDICOTECH CORE - BASE REAL (PostgreSQL)
-- Requires extension pgcrypto for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ENTIDADES JURIDICAS
CREATE TABLE IF NOT EXISTS legal_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('pf', 'pj', 'monolith')),
    name TEXT NOT NULL,
    document_hash TEXT NOT NULL,
    jurisdiction TEXT NOT NULL DEFAULT 'BR',
    risk_profile VARCHAR(20) NOT NULL DEFAULT 'medium',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- USUARIOS JURIDICOS
CREATE TABLE IF NOT EXISTS legal_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    entity_id UUID REFERENCES legal_entities(id) ON DELETE SET NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- CONTRATOS
CREATE TABLE IF NOT EXISTS contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_by UUID,
    deal_id UUID,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- VERSIONAMENTO
CREATE TABLE IF NOT EXISTS contract_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    version INT NOT NULL,
    content JSONB NOT NULL,
    hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(contract_id, version)
);

-- ASSINATURAS
CREATE TABLE IF NOT EXISTS contract_signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    user_id UUID,
    ip_address TEXT,
    signed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ANTI-BYPASS
CREATE TABLE IF NOT EXISTS non_circumvention (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    relationship_hash TEXT NOT NULL UNIQUE,
    lead_id UUID,
    broker_id UUID,
    property_id UUID,
    protected_until TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- AUDITORIA
CREATE TABLE IF NOT EXISTS legal_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action TEXT NOT NULL,
    actor_id UUID,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- RISCO
CREATE TABLE IF NOT EXISTS legal_risk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID,
    risk_level VARCHAR(10) NOT NULL,
    score FLOAT NOT NULL,
    flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- SLA
CREATE TABLE IF NOT EXISTS legal_sla (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL UNIQUE,
    sla_hours INT NOT NULL CHECK (sla_hours > 0)
);

CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_contracts_deal_id ON contracts(deal_id);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON legal_audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_risk_deal_id ON legal_risk(deal_id);
