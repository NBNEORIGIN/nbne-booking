from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TenantBase(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    name: str = Field(..., min_length=1, max_length=255)
    subdomain: Optional[str] = Field(None, min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict)


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class TenantInDB(TenantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantResponse(TenantInDB):
    pass
