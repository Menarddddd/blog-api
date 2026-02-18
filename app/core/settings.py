from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="UTF-8")

    DATABASE_URL: SecretStr
    ACCESS_SECRET_KEY: SecretStr
    REFRESH_SECRET_KEY: SecretStr
    ALGORITHM: str
    ACCESS_EXPIRE_MINUTES: int
    REFRESH_EXPIRE_DAYS: int


settings = Settings()  # type: ignore
