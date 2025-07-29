from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "SOMerAndomSecretKey12345"
    algorithm: str = "HS256"
    kafka_bootstrap_servers: str = "localhost:9092"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = AppSettings()
