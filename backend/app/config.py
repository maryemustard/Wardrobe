from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, read from environment variables (or a local .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "dev"

    database_url: str = "postgresql+psycopg://wardrobe:wardrobe@localhost:5432/wardrobe"

    # Single-credential HTTP Basic Auth gate for the whole app.
    basic_auth_user: str = "me"
    basic_auth_pass: str = "change-me"

    # Comma-separated list of allowed browser origins.
    cors_origins: str = "http://localhost:5173"

    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # Absolute path to the built frontend (set in the Docker image). Empty in dev.
    spa_dist_dir: str = ""

    @field_validator("database_url")
    @classmethod
    def _use_psycopg_driver(cls, v: str) -> str:
        """Accept the plain URL that Railway/Heroku provide and pin psycopg3."""
        if v.startswith("postgres://"):
            v = "postgresql://" + v.removeprefix("postgres://")
        if v.startswith("postgresql://"):
            v = "postgresql+psycopg://" + v.removeprefix("postgresql://")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
