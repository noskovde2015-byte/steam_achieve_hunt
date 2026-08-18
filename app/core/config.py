from pathlib import Path
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = "127.0.0.3"
    port: int = 8003


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    auth_prefix: str = "/auth"
    leaderboard_prefix: str = "/leaderboard"
    profile_prefix: str = "/profile"
    sync_prefix: str = "/sync"


class DataBaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class SteamConfig(BaseModel):
    api_key: str


class JWTConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="APP_CONFIG__",
        env_nested_delimiter="__",
    )
    run: RunConfig = RunConfig()
    api_prefix: ApiPrefix = ApiPrefix()
    db: DataBaseConfig
    steam: SteamConfig
    auth: JWTConfig


settings = Settings()
