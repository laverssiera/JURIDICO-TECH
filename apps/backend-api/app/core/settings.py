from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "JURIDICOTECH"
    app_version: str = "6.0.0"
    database_url: str = "postgresql+asyncpg://juridico:juridico@localhost:5432/juridico"
    redis_url: str = "redis://localhost:6379/0"
    nats_url: str = "nats://localhost:4222"


settings = Settings()
