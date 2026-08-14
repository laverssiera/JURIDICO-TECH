from __future__ import annotations

# In-memory cache for fast prototype mode. Database-backed persistence is handled in endpoints.
contracts_db: dict[str, dict] = {}
contract_versions_db: dict[str, list[dict]] = {}
contract_signatures_db: dict[str, list[dict]] = {}
non_circ_db: dict[str, dict] = {}
