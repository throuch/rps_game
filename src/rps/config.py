from enum import StrEnum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEV = "dev"
    QA = "qa"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Pas de valeur par défaut : une variable absente ou invalide fait
    # échouer le démarrage (fail-fast), comme requis par la spec.
    app_env: Environment
    database_url: str
    log_level: str = "INFO"
    app_port: int = 8080

    @property
    def docs_enabled(self) -> bool:
        return self.app_env is not Environment.PROD


@lru_cache
def get_settings() -> Settings:
    return Settings()
