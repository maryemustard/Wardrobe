from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, read from environment variables (or a local .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "dev"

    database_url: str = "postgresql+psycopg://wardrobe:wardrobe@localhost:5432/wardrobe"

    jwt_secret: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    # Comma-separated list of allowed browser origins.
    cors_origins: str = "http://localhost:5173"

    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # Absolute path to the built frontend (set in the Docker image). Empty in dev.
    spa_dist_dir: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
