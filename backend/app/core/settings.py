import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./lavajato.db"
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "LavaJato System"
    
    # WhatsApp
    WHATSAPP_API_URL: Optional[str] = None
    WHATSAPP_API_TOKEN: Optional[str] = None
    WHATSAPP_TEST_NUMBER: Optional[str] = None
    
    # PIX
    PIX_PROVIDER: Optional[str] = None  # 'pagseguro', 'mercadopago', 'gerencianet'
    PIX_API_KEY: Optional[str] = None
    PIX_CLIENT_ID: Optional[str] = None
    PIX_CLIENT_SECRET: Optional[str] = None
    
    # Security
    REQUIRE_PAYMENT_FOR_DELIVERY: bool = True
    SEND_WHATSAPP_NOTIFICATIONS: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
