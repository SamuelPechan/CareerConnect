from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CareerConnect API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://careerconnect:careerconnect@localhost:5432/careerconnect"
    jwt_secret_key: str = "development-only-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    frontend_origins: str = "http://localhost:5173,http://localhost:5174"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.app_env == "production" and self.jwt_secret_key == "development-only-secret":
            raise ValueError("JWT_SECRET_KEY must be changed before running in production")
        return self

    @property
    def allowed_frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
