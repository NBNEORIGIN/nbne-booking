from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator, Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "NBNE Booking API"
    VERSION: str = "0.1.0-alpha"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_PORT: str = "5432"
    
    DATABASE_URL: Optional[str] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        # Build from individual components if DATABASE_URL not provided
        if all([values.get('POSTGRES_USER'), values.get('POSTGRES_PASSWORD'), 
                values.get('POSTGRES_SERVER'), values.get('POSTGRES_DB')]):
            return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
        raise ValueError("Either DATABASE_URL or all POSTGRES_* variables must be provided")
    
    BACKEND_CORS_ORIGINS: Union[str, List[AnyHttpUrl]] = Field(default="")
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if v is None or v == "":
            return []
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        if isinstance(v, list):
            return v
        return []
    
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = ""
    FROM_NAME: str = "NBNE Booking"
    
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_SMS_NOTIFICATIONS: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name == 'BACKEND_CORS_ORIGINS':
                return raw_val
            return cls.json_loads(raw_val)


settings = Settings()
