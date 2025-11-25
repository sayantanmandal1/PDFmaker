"""
Configuration settings for the AI Document Generator API.
"""
import os
from typing import List
try:
    from pydantic_settings import BaseSettings
    from pydantic import field_validator
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings
    from pydantic import validator as field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "AI Document Generator API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Database
    database_url: str
    
    # Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # OpenAI / Ollama
    openai_api_key: str
    openai_base_url: str = "http://localhost:11434/v1"
    openai_model: str = "qwen2.5:14b"
    
    # CORS
    allowed_origins: str = "http://localhost:3000"
    
    # Logging
    log_level: str = "INFO"
    log_to_file: bool = False
    
    # Image Scraping
    image_scraping_timeout: int = 10
    image_scraping_max_retries: int = 3
    image_scraping_retry_delay: int = 2
    image_download_timeout: int = 15
    image_max_file_size_mb: int = 5
    image_scraping_delay: float = 1.0
    
    def get_allowed_origins(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(",")]
        return self.allowed_origins
    
    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v):
        """Parse debug flag from string."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    @field_validator("reload", mode="before")
    @classmethod
    def parse_reload(cls, v):
        """Parse reload flag from string."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    @field_validator("log_to_file", mode="before")
    @classmethod
    def parse_log_to_file(cls, v):
        """Parse log_to_file flag from string."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()