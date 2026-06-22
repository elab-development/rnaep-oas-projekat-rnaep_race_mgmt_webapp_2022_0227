from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"],
        extra="ignore",
        env_file_encoding="utf-8"
    )
    ENVIRONMENT: str = Field(default="development", validation_alias="environment")
    database_url: str = Field(validation_alias="user_database_url")
    secret_key: SecretStr = Field(validation_alias="user_secret_key")
    algorithm: str = Field(default="HS256", validation_alias="user_algorithm")
    access_token_expire_days: int = Field(default=30, validation_alias="user_access_token_expire_days")

settings = Settings()