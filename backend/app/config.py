from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Database
    database_url: str = "./data/inventory.db"
    
    # Cloudflare D1
    cloudflare_account_id: str = "your_account_id"
    cloudflare_api_token: str = "your_api_token"
    d1_database_id: str = "your_database_id"
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Logging
    log_level: str = "INFO"
    
    # Alert Configuration
    default_low_stock_threshold: int = 10
    default_critical_stock_threshold: int = 5
    alert_cooldown_minutes: int = 30
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def use_d1(self) -> bool:
        """Check if D1 credentials are configured"""
        return (
            self.cloudflare_account_id != "your_account_id" and
            self.cloudflare_api_token != "your_api_token" and
            self.d1_database_id != "your_database_id"
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
