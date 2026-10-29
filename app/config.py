from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "JPetStore 6 AI-Native"
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./jpetstore.db"
    secret_key: str = "jpetstore-stateless-cookie-secret-key-change-in-production-12345"
    session_cookie_name: str = "jpetstore_session"
    cache_ttl_seconds: int = 3600
    enable_ai_advisor: bool = True
    enable_ai_search: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
