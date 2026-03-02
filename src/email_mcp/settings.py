from __future__ import annotations

from pathlib import Path

from platformdirs import user_cache_dir, user_data_dir
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_data_dir() -> Path:
    return Path(user_data_dir("email-mcp", "ClawInbox"))


def _default_cache_dir() -> Path:
    return Path(user_cache_dir("email-mcp", "ClawInbox"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMAIL_MCP_", env_file=".env")

    data_dir: Path = Field(default_factory=_default_data_dir)
    cache_dir: Path = Field(default_factory=_default_cache_dir)
    store_dir: Path | None = None

    imap_host: str | None = None
    imap_port: int = 993
    imap_user: str | None = None
    imap_password: str | None = None
    imap_ssl: bool = True
    account_name: str = "default"
    imap_retry_count: int = 3
    imap_retry_delay_seconds: float = 1.0
    register_accounts: bool = True
    accounts_json: str | None = None

    log_level: str = "INFO"

    vector_enabled: bool = False
    vector_backend: str = "chroma"
    vector_dir: Path | None = None
    embedding_model: str = "all-MiniLM-L6-v2"

    transport: str = "stdio"
    http_host: str = "127.0.0.1"
    http_port: int = 8000

    auth_mode: str = "none"
    bearer_token: str | None = None
    auth_issuer_url: str | None = None
    auth_resource_server_url: str | None = None
    auth_required_scopes: str | None = None

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        store = self.store_dir or (self.data_dir / "eml")
        store.mkdir(parents=True, exist_ok=True)
        vector_dir = self.vector_dir or (self.data_dir / "vector")
        vector_dir.mkdir(parents=True, exist_ok=True)

    @property
    def resolved_store_dir(self) -> Path:
        return self.store_dir or (self.data_dir / "eml")

    @property
    def resolved_vector_dir(self) -> Path:
        return self.vector_dir or (self.data_dir / "vector")
