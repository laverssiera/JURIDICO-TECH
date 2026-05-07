from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LEGAL_AI_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://juridico:juridico@localhost:5432/juridico"
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"
    vector_collection: str = "legal_documents"
    top_k: int = 5


settings = Settings()
