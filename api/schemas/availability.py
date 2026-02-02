from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, time


class AvailabilityBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time

    @field_validator('end_time')
    @classmethod
    def validate_end_after_start(cls, v, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityUpdate(BaseModel):
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class AvailabilityInDB(AvailabilityBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AvailabilityResponse(AvailabilityInDB):
    pass


class BlackoutBase(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = Field(None, max_length=500)

    @field_validator('end_datetime')
    @classmethod
    def validate_end_after_start(cls, v, info):
        if 'start_datetime' in info.data and v <= info.data['start_datetime']:
            raise ValueError('end_datetime must be after start_datetime')
        return v


class BlackoutCreate(BlackoutBase):
    pass


class BlackoutUpdate(BaseModel):
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    reason: Optional[str] = Field(None, max_length=500)


class BlackoutInDB(BlackoutBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlackoutResponse(BlackoutInDB):
    pass
