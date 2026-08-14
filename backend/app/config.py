"""Application settings, loaded from environment / .env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="VAMOS_", extra="ignore")

    database_url: str = f"sqlite:///{PROJECT_ROOT / 'vamos.db'}"
    jwt_secret: str = "dev-only-secret-change-me-before-sharing"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # one week

    content_dir: Path = PROJECT_ROOT / "content"
    log_file: Path = PROJECT_ROOT / "logs" / "vamos.log"
    watch_dir: Path = Path("/srv/files/ytwatcher/Espanol")
    vitamina_dir: Path = PROJECT_ROOT / "Vitamina"

    whisper_model: str = "small"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "https://localhost",
        "capacitor://localhost",
    ]


settings = Settings()
