"""
Assignment Platform - Backend Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Assignment Platform API"
    DEBUG: bool = True
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # File upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = ["pdf", "docx", "pptx", "ppt"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"

# Explicitly load dotenv to handle cases where pydantic doesn't find it
import os
from dotenv import load_dotenv

# Try to find .env in current or parent directory
if os.path.exists(".env"):
    load_dotenv(".env")
elif os.path.exists("backend/.env"):
    load_dotenv("backend/.env")
elif os.path.exists("../.env"):
    load_dotenv("../.env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
