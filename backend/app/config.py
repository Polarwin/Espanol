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
