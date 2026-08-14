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

CREATE TABLE IF NOT EXISTS scientific_authorship (
    id UUID PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    contribution_type TEXT,
    contribution_score NUMERIC(5,2),
    institution TEXT,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patents_registry (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT,
    description TEXT,
    novelty_score NUMERIC(5,2),
    prior_art_checked BOOLEAN,
    status TEXT,
    owner_id TEXT,
    owner_institution TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interplanetary_research (
    id UUID PRIMARY KEY,
    research_type TEXT,
    risk_level TEXT,
    compliance_status TEXT,
    jurisdiction_scope TEXT,
    researcher_id TEXT,
    institution TEXT,
    reviewed_by TEXT,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS civilizational_impact (
    id UUID PRIMARY KEY,
    project_id TEXT NOT NULL,
    project_name TEXT,
    housing_impact NUMERIC(5,2),
    infrastructure_impact NUMERIC(5,2),
    social_benefit_score NUMERIC(5,2),
    environmental_impact NUMERIC(5,2),
    global_benefit BOOLEAN,
    accessibility_score NUMERIC(5,2),
    assessed_by TEXT,
    final_score NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    assessed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agora_covenant (
    id UUID PRIMARY KEY,
    treaty_type TEXT,
    parties TEXT[],
    terms TEXT,
    binding_level TEXT,
    compliance_mandatory BOOLEAN,
    status TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    activated_at TIMESTAMP
);
