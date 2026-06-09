from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=["../.env", ".env.local", ".env"],
        extra="ignore",
        env_file_encoding="utf-8"
    )
    database_url: str = Field(validation_alias="race_database_url")
    secret_key: SecretStr = Field(validation_alias="user_secret_key")
    algorithm: str = Field(default="HS256")

settings = Settings()