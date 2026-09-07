from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI 考证教练 API"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    secret_key: str
    database_url: str
    frontend_origins: str = "http://localhost:5173"
    ai_api_key: str = ""
    ai_base_url: str = ""
    ai_model: str = ""
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen3.7-max"
    access_token_expire_minutes: int = 60 * 24 * 7
    payment_provider: str = "mock"
    payment_callback_url: str = ""
    payment_return_url: str = ""
    redis_url: str = "redis://127.0.0.1:6379/0"
    email_code_secret: str
    email_code_expire_seconds: int = 300
    email_code_cooldown_seconds: int = 60
    email_code_max_attempts: int = 5
    email_code_daily_limit: int = 20
    email_delivery_mode: str = "console"
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "AI 考证教练"
    smtp_from_email: str = ""
    smtp_use_ssl: bool = True
    cos_region: str = "ap-chengdu"
    cos_bucket: str = ""
    cos_secret_id: str = ""
    cos_secret_key: str = ""
    cos_public_base_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def frontend_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
