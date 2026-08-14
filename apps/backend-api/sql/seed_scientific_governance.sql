-- Seed minimo para simulacao de Scientific Governance / Cosmic Law

INSERT INTO scientific_authorship (
    id, experiment_id, author_id, contribution_type, contribution_score, institution, verified_at, created_at
) VALUES (
    '00000000-0000-0000-0000-000000000101',
    'EXP-ORBIT-001',
    'AUTH-LICEU-01',
    'discovery',
    92.50,
    'LICEU Space Lab',
    NOW(),
    NOW()
);

INSERT INTO patents_registry (
    id, title, category, description, novelty_score, prior_art_checked, status, owner_id, owner_institution, created_at
) VALUES (
    '00000000-0000-0000-0000-000000000201',
    'Composite-X Habitat Shell',
    'material',
    'Composite para habitats extremos de baixa manutencao',
    88.30,
    TRUE,
    'approved',
    'ORG-001',
    'LICEU Advanced Materials',
    NOW()
);

INSERT INTO interplanetary_research (
    id, research_type, risk_level, compliance_status, jurisdiction_scope, researcher_id, institution, reviewed_by, review_notes, created_at, reviewed_at
) VALUES (
    '00000000-0000-0000-0000-000000000301',
    'space',
    'high',
    'approved',
    'orbit',
    'RES-007',
    'LICEU Orbital Program',
    'counsel-01',
    'Aprovado com monitoramento continuo de seguranca',
    NOW(),
    NOW()
);

INSERT INTO civilizational_impact (
    id, project_id, project_name, housing_impact, infrastructure_impact, social_benefit_score, environmental_impact, global_benefit, accessibility_score, assessed_by, final_score, created_at, assessed_at
) VALUES (
    '00000000-0000-0000-0000-000000000401',
    'CIV-HAB-01',
    'Habitat Modular de Alta Resiliencia',
    22.40,
    18.75,
    91.20,
    8.10,
    TRUE,
    89.00,
    'john-civilizational-counsel',
    90.15,
    NOW(),
    NOW()
);

INSERT INTO agora_covenant (
    id, treaty_type, parties, terms, binding_level, compliance_mandatory, status, created_at, activated_at
) VALUES (
    '00000000-0000-0000-0000-000000000501',
    'scientific',
    ARRAY['LICEU Orbital Program', 'LICEU Oceanic Lab', 'LICEU Quantum Core'],
    'Compartilhamento de dados sensiveis com trilha de autoria e auditoria obrigatoria',
    'binding',
    TRUE,
    'active',
    NOW(),
    NOW()
);
