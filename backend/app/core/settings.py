from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./lavajato.db"
    
    # Project
    PROJECT_NAME: Optional[str] = "LavaJato System"
    
    # WhatsApp Configuration
    WHATSAPP_API_URL: Optional[str] = None
    WHATSAPP_API_TOKEN: Optional[str] = None
    WHATSAPP_INSTANCE_ID: Optional[str] = None
    WHATSAPP_TEST_NUMBER: Optional[str] = "41988548538"
    
    # PIX
    PIX_PROVIDER: Optional[str] = None
    PIX_API_KEY: Optional[str] = None
    
    # Features
    REQUIRE_PAYMENT_FOR_DELIVERY: Optional[bool] = False
    SEND_WHATSAPP_NOTIFICATIONS: Optional[bool] = False
    
    class Config:
        env_file = ".env"

settings = Settings()
