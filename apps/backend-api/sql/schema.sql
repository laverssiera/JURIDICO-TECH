CREATE TABLE IF NOT EXISTS legal_contracts (
    id UUID PRIMARY KEY,
    contract_number VARCHAR(120),
    title TEXT,
    contract_type VARCHAR(100),
    status VARCHAR(50),
    tenant_id UUID,
    risk_score NUMERIC,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS legal_clauses (
    id UUID PRIMARY KEY,
    contract_id UUID,
    clause_type VARCHAR(120),
    clause_text TEXT,
    litigation_score NUMERIC,
    recommended BOOLEAN
);

CREATE TABLE IF NOT EXISTS legal_audit_log (
    id UUID PRIMARY KEY,
    event_type VARCHAR(255),
    actor VARCHAR(255),
    payload JSONB,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS legal_cases (
    id UUID PRIMARY KEY,
    category VARCHAR(100),
    status VARCHAR(50),
    plaintiff TEXT,
    defendant TEXT,
    estimated_risk NUMERIC,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS legal_event_outbox (
    id UUID PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    payload_json TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    attempts INTEGER NOT NULL,
    last_error TEXT,
    created_at TIMESTAMP,
    published_at TIMESTAMP
);
