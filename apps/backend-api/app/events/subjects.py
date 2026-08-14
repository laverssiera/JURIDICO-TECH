LEGAL_SUBJECTS = [
    "legal.contract.created",
    "legal.contract.signed",
    "legal.contract.breach",
    "legal.arbitration.started",
    "legal.arbitration.closed",
    "legal.compliance.alert",
    "legal.audit.created",
    "legal.pericia.generated",
    "legal.embargo.detected",
    "legal.asset.risk",
    "legal.sst.violation",
    "legal.esg.alert",
    "legal.tax.risk",
    "legal.governance.blocked",
    "legal.compliance.runtime.started",
    "legal.compliance.runtime.pulsed",
    "legal.compliance.runtime.scope_updated",
    "legal.compliance.runtime.stopped",
    "legal.space.treaty.updated",
    "legal.patent.registered",
    "legal.ip.protected",
    "legal.orbital.dispute",
    "legal.mars.compliance",
    "legal.global.risk.alert",
    "legal.war_room.action",
]

FEDERATION_EVENTS = [
    "federation.runtime.register",
    "federation.runtime.snapshot",
    "federation.runtime.telemetry",
]

ALL_LEGAL_SUBJECTS = [*LEGAL_SUBJECTS, *FEDERATION_EVENTS]
