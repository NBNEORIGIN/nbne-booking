from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime
import re


class TenantBase(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    name: str = Field(..., min_length=1, max_length=255)
    subdomain: Optional[str] = Field(None, min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    # Branding fields
    client_display_name: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    primary_color: str = Field(default="#2196F3", max_length=7)
    secondary_color: Optional[str] = Field(None, max_length=7)
    accent_color: Optional[str] = Field(None, max_length=7)
    booking_page_title: Optional[str] = Field(None, max_length=255)
    booking_page_intro: Optional[str] = None
    location_text: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    business_address: Optional[str] = None
    social_links: Optional[Dict[str, str]] = Field(default_factory=dict)
    
    @validator('primary_color', 'secondary_color', 'accent_color')
    def validate_hex_color(cls, v):
        if v is None:
            return v
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex color (e.g., #2196F3)')
        return v.upper()
    
    @validator('logo_url')
    def validate_logo_url(cls, v):
        if v is None:
            return v
        # Basic URL validation - allow http, https, or relative paths
        if not (v.startswith('http://') or v.startswith('https://') or v.startswith('/')):
            raise ValueError('Logo URL must be a valid HTTP/HTTPS URL or relative path')
        return v


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    
    # Branding fields (all optional for updates)
    client_display_name: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    primary_color: Optional[str] = Field(None, max_length=7)
    secondary_color: Optional[str] = Field(None, max_length=7)
    accent_color: Optional[str] = Field(None, max_length=7)
    booking_page_title: Optional[str] = Field(None, max_length=255)
    booking_page_intro: Optional[str] = None
    location_text: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    business_address: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    
    @validator('primary_color', 'secondary_color', 'accent_color')
    def validate_hex_color(cls, v):
        if v is None:
            return v
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex color (e.g., #2196F3)')
        return v.upper()
    
    @validator('logo_url')
    def validate_logo_url(cls, v):
        if v is None:
            return v
        if not (v.startswith('http://') or v.startswith('https://') or v.startswith('/')):
            raise ValueError('Logo URL must be a valid HTTP/HTTPS URL or relative path')
        return v


class TenantInDB(TenantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantResponse(TenantInDB):
    pass
