from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./cashorbit.db"
    jwt_secret: str = "local-only-change-me"
    jwt_expire_minutes: int = 720
    cors_origins: str = "http://localhost:3000"
    payment_public_base_url: str = "http://localhost:8000"
    frontend_public_url: str = "http://localhost:3000"
    payment_provider_mode: str = "sandbox"
    bkash_base_url: str = "https://tokenized.sandbox.bka.sh/v1.2.0-beta"
    bkash_app_key: str = ""
    bkash_app_secret: str = ""
    bkash_username: str = ""
    bkash_password: str = ""
    sslcommerz_base_url: str = "https://sandbox.sslcommerz.com"
    sslcommerz_store_id: str = ""
    sslcommerz_store_password: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
