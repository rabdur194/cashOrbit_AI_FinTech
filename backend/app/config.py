from pydantic_settings import BaseSettings, SettingsConfigDict
import warnings

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
    openai_base_url: str = "https://api.groq.com/openai/v1"
    openai_model: str = "openai/gpt-oss-20b"
    # gemini_api_key: str = ""
    # gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    # gemini_model: str = "gemini-2.5-flash-lite"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def validate_for_deploy(self) -> None:
        """Warn loudly if insecure defaults are still in use."""
        if self.jwt_secret in ("local-only-change-me", "change-me", ""):
            warnings.warn(
                "JWT_SECRET is using an insecure default. "
                "Set a long random value before any public deployment.",
                UserWarning,
                stacklevel=2,
            )

settings = Settings()
settings.validate_for_deploy()
