"""Configuration for Seller Intelligence Copilot."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Mock Services Configuration
    MOCK_SERVICES_HOST: str = "http://localhost"
    MOCK_SERVICES_PORT: int = 8001
    
    # LLM Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"  # Default model, can be overridden
    
    # Timeouts (seconds)
    SERVICE_TIMEOUT: int = 10
    LLM_TIMEOUT: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
