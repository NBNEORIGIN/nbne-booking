from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    duration_minutes: int = Field(..., gt=0, le=1440)
    price: Optional[float] = Field(None, ge=0)
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    duration_minutes: Optional[int] = Field(None, gt=0, le=1440)
    price: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ServiceInDB(ServiceBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceResponse(ServiceInDB):
    pass
