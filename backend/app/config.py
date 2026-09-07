"""Application settings, loaded from environment / .env."""

from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="VAMOS_", extra="ignore")

    database_url: str = f"sqlite:///{PROJECT_ROOT / 'vamos.db'}"
    environment: str = "development"
    jwt_secret: str = "dev-only-secret-change-me-before-sharing"
    jwt_secret_file: Path | None = None
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # one week

    content_dir: Path = PROJECT_ROOT / "content"
    log_file: Path = PROJECT_ROOT / "logs" / "vamos.log"
    watch_dir: Path = Path("/srv/files/ytwatcher/Espanol")
    vitamina_dir: Path = PROJECT_ROOT / "Vitamina"

    ai_enabled: bool = False
    ai_cloud_enabled: bool = False
    ai_conversation_adapter: str = "openai_compatible"
    ai_conversation_url: str = "http://127.0.0.1:8349/v1"
    ai_conversation_model: str = "SmolLM3-Q4_K_M.gguf"
    ai_conversation_key_env: str = ""
    ai_conversation_local: bool = True
    ai_correction_adapter: str = "barto"
    ai_correction_url: str = "http://127.0.0.1:8351"
    ai_correction_model: str = "SkitCon/gec-spanish-BARTO-SYNTHETIC"
    ai_correction_key_env: str = ""
    ai_correction_local: bool = True

    @model_validator(mode="after")
    def validate_ai(self) -> "Settings":
        from urllib.parse import urlparse
        import os
        for task in ("conversation", "correction"):
            adapter = getattr(self, f"ai_{task}_adapter")
            allowed = {"openai_compatible", "openai_responses", "anthropic"}
            if task == "correction":
                allowed.add("barto")
            if adapter not in allowed:
                raise ValueError(f"Unsupported {task} provider")
            url = urlparse(getattr(self, f"ai_{task}_url"))
            if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
                raise ValueError(f"Invalid {task} URL")
            if self.ai_enabled:
                local = getattr(self, f"ai_{task}_local")
                if local and url.hostname not in {"localhost", "127.0.0.1", "::1"}:
                    raise ValueError("Local AI must use a loopback gateway")
                if not local and not self.ai_cloud_enabled:
                    raise ValueError("Cloud AI is disabled")
                if not local and url.scheme != "https":
                    raise ValueError("Cloud AI requires HTTPS")
                key_env = getattr(self, f"ai_{task}_key_env")
                if not local and (not key_env or not os.environ.get(key_env)):
                    raise ValueError("Cloud AI needs a configured API key environment variable")
        return self

    whisper_model: str = "small"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    backup_dir: Path = PROJECT_ROOT / "backups"
    speech_cache_max_files: int = 256
    speech_cache_max_bytes: int = 128 * 1024 * 1024

    cors_origins: list[str] = [
        "http://localhost:5173",
        "https://localhost",
        "capacitor://localhost",
    ]

    @model_validator(mode="after")
    def load_and_validate_jwt_secret(self) -> "Settings":
        if self.jwt_secret_file is not None:
            try:
                self.jwt_secret = self.jwt_secret_file.read_text(encoding="utf-8").strip()
            except OSError as exc:
                raise ValueError(f"Cannot read JWT secret file: {self.jwt_secret_file}") from exc
        if self.environment.lower() == "production":
            if self.jwt_secret == "dev-only-secret-change-me-before-sharing" or len(self.jwt_secret) < 64:
                raise ValueError("Production requires a unique JWT secret of at least 64 characters")
        return self


settings = Settings()
