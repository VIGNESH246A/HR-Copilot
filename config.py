"""
Configuration management for HR Copilot (Gemini Version)
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "HR Copilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    
    # API Keys - Using Gemini instead of Claude
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    
    # Gemini Configuration
    GEMINI_MODEL: str = "gemini-2.0-flash"  # Latest model
    GEMINI_MAX_TOKENS: int = 8000
    GEMINI_TEMPERATURE: float = 0.7
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./data/hr_copilot.db",
        env="DATABASE_URL"
    )
    
    # Vector Store (optional for basic version)
    VECTOR_STORE_PATH: str = "./data/vector_store"
    
    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    RESUME_DIR: str = "./data/resumes"
    TEMPLATE_DIR: str = "./data/templates"
    
    # Email Configuration
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    FROM_EMAIL: Optional[str] = Field(default=None, env="FROM_EMAIL")
    
    # Calendar Configuration
    GOOGLE_CALENDAR_CREDENTIALS: Optional[str] = Field(
        default=None, 
        env="GOOGLE_CALENDAR_CREDENTIALS"
    )
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/hr_copilot.log"
    
    # Agent Configuration
    MAX_ITERATIONS: int = 5
    CONVERSATION_HISTORY_LIMIT: int = 20
    
    # ATS Integration (Optional)
    ATS_API_KEY: Optional[str] = Field(default=None, env="ATS_API_KEY")
    ATS_API_URL: Optional[str] = Field(default=None, env="ATS_API_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Initialize settings
settings = Settings()


def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "./data",
        "./data/uploads",
        "./data/resumes",
        "./data/templates",
        "./data/vector_store",
        "./logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Validate critical settings
def validate_settings():
    """Validate critical configuration"""
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found. Please set it in .env file"
        )
    
    create_directories()
    return True


if __name__ == "__main__":
    validate_settings()
    print("✓ Configuration validated successfully")
    print(f"App: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Model: {settings.GEMINI_MODEL}")
    print(f"Database: {settings.DATABASE_URL}")