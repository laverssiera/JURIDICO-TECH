from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class FederationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MONOLITH_NAME: str = "juridicotech"

    NATS_URL: str = "nats://localhost:4222"

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "liceu"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    # Backends: auto|memory|redis, auto|memory|neo4j, auto|memory|otel
    FEDERATION_MEMORY_BACKEND: str = "auto"
    FEDERATION_GRAPH_BACKEND: str = "auto"
    FEDERATION_OBSERVABILITY_BACKEND: str = "auto"

    SPACE_LAW_RUNTIME: bool = True
    PLANETARY_COMPLIANCE: bool = True
    INTERPLANETARY_ARBITRATION: bool = True


settings = FederationSettings()
