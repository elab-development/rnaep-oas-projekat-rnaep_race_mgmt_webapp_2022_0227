from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=["../.env", ".env.local", ".env"],
        extra="ignore",
        env_file_encoding="utf-8"
    )
    database_url: str = Field(validation_alias="payment_database_url")
    secret_key: SecretStr = Field(validation_alias="user_secret_key")
    algorithm: str = Field(default="HS256")
    payment_secret_key: SecretStr = Field(validation_alias="payment_secret_key")
    stripe_webhook_secret: str = Field(validation_alias="payment_webhook_secret")
    stripe_success_url: str = Field(validation_alias="payment_success_url")
    stripe_cancel_url: str = Field(validation_alias="payment_cancel_url")
    kafka_bootstrap_servers: str = Field(validation_alias="kafka_bootstrap_servers")

settings = Settings()