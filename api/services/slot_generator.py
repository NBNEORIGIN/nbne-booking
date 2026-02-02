from datetime import datetime, date, time, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session

from api.models.availability import Availability, Blackout
from api.models.service import Service


class SlotGenerator:
    """Generate available booking slots based on availability, blackouts, and existing bookings."""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    def generate_slots(
        self,
        service_id: int,
        start_date: date,
        end_date: date,
        timezone_offset: int = 0
    ) -> List[dict]:
        """
        Generate available slots for a service within a date range.
        
        Args:
            service_id: ID of the service
            start_date: Start date for slot generation
            end_date: End date for slot generation
            timezone_offset: Timezone offset in hours (default 0 for UTC)
        
        Returns:
            List of slot dictionaries with start_time and end_time
        """
        # Get service
        service = self.db.query(Service).filter(
            Service.id == service_id,
            Service.tenant_id == self.tenant_id,
            Service.is_active == True
        ).first()
        
        if not service:
            return []
        
        # Get availability windows for tenant
        availability_windows = self.db.query(Availability).filter(
            Availability.tenant_id == self.tenant_id
        ).all()
        
        if not availability_windows:
            return []
        
        # Get blackouts that overlap with date range
        blackouts = self.db.query(Blackout).filter(
            Blackout.tenant_id == self.tenant_id,
            Blackout.end_datetime >= datetime.combine(start_date, time.min),
            Blackout.start_datetime <= datetime.combine(end_date, time.max)
        ).all()
        
        # Generate slots
        slots = []
        current_date = start_date
        
        while current_date <= end_date:
            day_slots = self._generate_slots_for_day(
                current_date,
                service.duration_minutes,
                availability_windows,
                blackouts
            )
            slots.extend(day_slots)
            current_date += timedelta(days=1)
        
        return slots
    
    def _generate_slots_for_day(
        self,
        target_date: date,
        duration_minutes: int,
        availability_windows: List[Availability],
        blackouts: List[Blackout]
    ) -> List[dict]:
        """Generate slots for a specific day."""
        slots = []
        
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = target_date.weekday()
        
        # Find availability windows for this day
        day_availability = [
            av for av in availability_windows
            if av.day_of_week == day_of_week
        ]
        
        if not day_availability:
            return []
        
        # Generate slots for each availability window
        for availability in day_availability:
            window_slots = self._generate_slots_in_window(
                target_date,
                availability.start_time,
                availability.end_time,
                duration_minutes,
                blackouts
            )
            slots.extend(window_slots)
        
        return slots
    
    def _generate_slots_in_window(
        self,
        target_date: date,
        start_time: time,
        end_time: time,
        duration_minutes: int,
        blackouts: List[Blackout]
    ) -> List[dict]:
        """Generate slots within a specific availability window."""
        slots = []
        
        # Start from the beginning of the window
        current_time = datetime.combine(target_date, start_time)
        window_end = datetime.combine(target_date, end_time)
        
        while current_time + timedelta(minutes=duration_minutes) <= window_end:
            slot_start = current_time
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if slot overlaps with any blackout
            if not self._overlaps_blackout(slot_start, slot_end, blackouts):
                slots.append({
                    "start_time": slot_start.isoformat(),
                    "end_time": slot_end.isoformat()
                })
            
            # Move to next slot (no gap between slots for now)
            current_time += timedelta(minutes=duration_minutes)
        
        return slots
    
    def _overlaps_blackout(
        self,
        slot_start: datetime,
        slot_end: datetime,
        blackouts: List[Blackout]
    ) -> bool:
        """Check if a slot overlaps with any blackout period."""
        for blackout in blackouts:
            # Check for overlap: slot_start < blackout_end AND slot_end > blackout_start
            if slot_start < blackout.end_datetime and slot_end > blackout.start_datetime:
                return True
        return False
    
    def is_slot_available(
        self,
        service_id: int,
        slot_start: datetime,
        slot_end: datetime
    ) -> bool:
        """
        Check if a specific slot is available for booking.
        Used during booking creation to verify slot is still available.
        """
        # Get service
        service = self.db.query(Service).filter(
            Service.id == service_id,
            Service.tenant_id == self.tenant_id,
            Service.is_active == True
        ).first()
        
        if not service:
            return False
        
        # Check if slot falls within availability windows
        day_of_week = slot_start.weekday()
        slot_time_start = slot_start.time()
        slot_time_end = slot_end.time()
        
        availability = self.db.query(Availability).filter(
            Availability.tenant_id == self.tenant_id,
            Availability.day_of_week == day_of_week,
            Availability.start_time <= slot_time_start,
            Availability.end_time >= slot_time_end
        ).first()
        
        if not availability:
            return False
        
        # Check if slot overlaps with blackouts
        blackouts = self.db.query(Blackout).filter(
            Blackout.tenant_id == self.tenant_id,
            Blackout.start_datetime < slot_end,
            Blackout.end_datetime > slot_start
        ).all()
        
        if blackouts:
            return False
        
        return True
