"""Configuration management for backend"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Database configuration
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://travelbuddy:travelbuddy@localhost:5432/travelbuddy"
    )
    
    # Wake-on-LAN configuration
    pc_mac_address: str = os.getenv("PC_MAC_ADDRESS", "")
    pc_ip_address: str = os.getenv("PC_IP_ADDRESS", "")
    pc_port: int = int(os.getenv("PC_PORT", "9"))
    
    # PC Processing API configuration
    pc_processing_api_url: Optional[str] = os.getenv("PC_PROCESSING_API_URL", None)
    pc_processing_api_port: int = int(os.getenv("PC_PROCESSING_API_PORT", "8001"))
    
    # Processing configuration
    processing_schedule: str = os.getenv("PROCESSING_SCHEDULE", "0 2 * * *")  # 2 AM daily
    
    # Model paths
    nllb_model_name: str = os.getenv("NLLB_MODEL_NAME", "facebook/nllb-200-3.3B")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    model_cache_dir: str = os.getenv("MODEL_CACHE_DIR", "./models")
    
    # API configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_debug: bool = os.getenv("API_DEBUG", "False").lower() == "true"
    
    # Translation configuration
    target_language: str = os.getenv("TARGET_LANGUAGE", "eng_Latn")  # English
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

