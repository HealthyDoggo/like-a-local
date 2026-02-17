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

    # Promotion/clustering configuration
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))  # Cosine similarity threshold for clustering
    min_mentions: int = int(os.getenv("MIN_MENTIONS", "3"))  # Minimum mentions to promote a tip

    # JWT configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-in-production-use-openssl-rand-base64-32")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Google OAuth configuration
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_ios_client_id: str = os.getenv("GOOGLE_IOS_CLIENT_ID", "")
    google_android_client_id: str = os.getenv("GOOGLE_ANDROID_CLIENT_ID", "")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

