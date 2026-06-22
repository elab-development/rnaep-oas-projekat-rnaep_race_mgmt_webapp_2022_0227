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
    kafka_bootstrap_servers: str = Field(validation_alias="kafka_bootstrap_servers")
    algorithm: str = Field(default="HS256")

    mailtrap_api_token: SecretStr = Field(validation_alias="mailtrap_api_token")
    mailtrap_sandbox: bool = Field(default=True, validation_alias="mailtrap_sandbox")
    mailtrap_inbox_id: int | None = Field(default=None, validation_alias="mailtrap_inbox_id")

    email_from: str = Field(validation_alias="email_from")
    email_from_name: str = Field(default="Obsta Race", validation_alias="email_from_name")
    email_support: str = Field(validation_alias="email_support")

settings = Settings()