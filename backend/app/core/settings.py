from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILES = (BASE_DIR / ".env", BASE_DIR / "backend" / ".env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore"
    )
    APP_NAME: str = "AI Onboarding Assistant"
    ENV: str = "development"

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    REDIS_HOST: str
    REDIS_PORT: int

    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_HOST: str
    MINIO_PORT: int

    CHROMA_HOST: str
    CHROMA_PORT: int

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def minio_endpoint(self) -> str:
        return f"https://{self.MINIO_HOST}:{self.MINIO_PORT}/"

    @property
    def chroma_endpoint(self) -> str:
        return f"https://{self.CHROMA_HOST}:{self.CHROMA_PORT}/"


settings = Settings()
