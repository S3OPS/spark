from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    secret_key: str = "your-secret-key-here"
    
    # Database
    database_url: str = "sqlite:///./data/stealth_ai.db"
    
    # AI/ML Services
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    use_local_llm: bool = False
    local_llm_model: str = "llama2"
    
    # Social Media APIs
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "StealthAI/1.0"
    
    # Payment Processing
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    
    # Email Services
    sendgrid_api_key: Optional[str] = None
    from_email: str = "noreply@yourdomain.com"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Analytics
    google_analytics_id: Optional[str] = None
    
    # Deployment
    landing_page_domain: str = "https://yourdomain.com"
    gumroad_access_token: Optional[str] = None
    
    # Automation Settings
    signal_scan_interval_hours: int = 6
    content_posting_enabled: bool = True
    min_conversion_threshold: float = 0.05
    auto_reinvest_threshold: float = 310
    target_monthly_revenue: float = 8700
    
    # Platform Settings
    comply_with_tos: bool = True
    max_posts_per_day: int = 10
    engagement_delay_seconds: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
