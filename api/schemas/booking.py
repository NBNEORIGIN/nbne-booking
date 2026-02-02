from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from api.models.booking import BookingStatus


class BookingBase(BaseModel):
    service_id: int = Field(..., gt=0)
    start_time: datetime
    end_time: datetime
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: EmailStr
    customer_phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=1000)


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)


class BookingInDB(BookingBase):
    id: int
    tenant_id: int
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingResponse(BookingInDB):
    service_name: Optional[str] = None


class BookingListItem(BaseModel):
    id: int
    service_id: int
    service_name: str
    start_time: datetime
    end_time: datetime
    customer_name: str
    customer_email: str
    customer_phone: Optional[str]
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True
