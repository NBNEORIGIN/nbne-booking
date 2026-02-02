from pydantic import BaseModel, Field
from datetime import datetime, date


class SlotRequest(BaseModel):
    service_id: int = Field(..., gt=0)
    start_date: date
    end_date: date
    timezone_offset: int = Field(0, ge=-12, le=14, description="Timezone offset in hours")


class Slot(BaseModel):
    start_time: str
    end_time: str


class SlotResponse(BaseModel):
    service_id: int
    service_name: str
    duration_minutes: int
    slots: list[Slot]
