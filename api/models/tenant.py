from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, Text
from sqlalchemy.sql import func
from api.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=True, index=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSON, default=dict, nullable=False)
    
    # Branding fields
    client_display_name = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#2196F3", nullable=False)
    secondary_color = Column(String(7), nullable=True)
    accent_color = Column(String(7), nullable=True)
    booking_page_title = Column(String(255), nullable=True)
    booking_page_intro = Column(Text, nullable=True)
    location_text = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    business_address = Column(Text, nullable=True)
    social_links = Column(JSON, default=dict, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Tenant(id={self.id}, slug='{self.slug}', name='{self.name}')>"
    
    def get_branding(self) -> dict:
        """Get resolved branding with defaults."""
        return {
            "client_display_name": self.client_display_name or self.name,
            "logo_url": self.logo_url,
            "primary_color": self.primary_color or "#2196F3",
            "secondary_color": self.secondary_color or "#1976D2",
            "accent_color": self.accent_color or "#4CAF50",
            "booking_page_title": self.booking_page_title or f"Book with {self.name}",
            "booking_page_intro": self.booking_page_intro or "Select a service and time to book your appointment.",
            "location_text": self.location_text,
            "contact_email": self.contact_email or self.email,
            "contact_phone": self.contact_phone or self.phone,
            "business_address": self.business_address,
            "social_links": self.social_links or {}
        }
