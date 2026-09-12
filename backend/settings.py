from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "secrets/neo4j.env"), extra="ignore"
    )

    daytona_api_key: str | None = None
    daytona_api_url: str | None = None
    daytona_target: str | None = None
    neo4j_uri: str | None = None
    neo4j_username: str | None = None
    neo4j_password: str | None = None
    neo4j_database: str = "neo4j"
    frontend_origin: str = "http://localhost:3000"

    @property
    def daytona_configured(self) -> bool:
        return bool(self.daytona_api_key)

    @property
    def neo4j_configured(self) -> bool:
        return all((self.neo4j_uri, self.neo4j_username, self.neo4j_password))


@lru_cache
def get_settings() -> Settings:
    return Settings()
