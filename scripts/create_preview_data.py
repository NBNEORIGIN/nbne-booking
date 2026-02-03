"""
Create preview data for local testing
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.core.database import SessionLocal
from api.models.tenant import Tenant
from api.models.service import Service
from api.models.availability import Availability
from datetime import time

def create_preview_data():
    db = SessionLocal()
    
    try:
        # Check if preview tenant already exists
        existing = db.query(Tenant).filter(Tenant.slug == "preview-demo").first()
        if existing:
            print(f"Preview tenant already exists (ID: {existing.id})")
            tenant = existing
        else:
            # Create preview tenant
            tenant = Tenant(
                slug="preview-demo",
                name="Preview Demo Company",
                email="demo@example.com",
                phone="+44 20 1234 5678",
                client_display_name="Preview Demo",
                primary_color="#FF5722",
                secondary_color="#E64A19",
                accent_color="#4CAF50",
                booking_page_title="Book Your Appointment",
                booking_page_intro="Welcome! Select a service and time that works for you.",
                location_text="London, UK",
                contact_email="bookings@previewdemo.com",
                contact_phone="+44 20 1234 5678"
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            print(f"Created preview tenant (ID: {tenant.id})")
        
        # Create sample services
        services_data = [
            {
                "name": "Consultation",
                "description": "30-minute consultation session",
                "duration_minutes": 30,
                "price": 50.00
            },
            {
                "name": "Full Service",
                "description": "Comprehensive 60-minute service",
                "duration_minutes": 60,
                "price": 100.00
            },
            {
                "name": "Quick Check",
                "description": "15-minute quick check-up",
                "duration_minutes": 15,
                "price": 25.00
            }
        ]
        
        for service_data in services_data:
            existing_service = db.query(Service).filter(
                Service.tenant_id == tenant.id,
                Service.name == service_data["name"]
            ).first()
            
            if not existing_service:
                service = Service(
                    tenant_id=tenant.id,
                    **service_data
                )
                db.add(service)
                print(f"Created service: {service_data['name']}")
        
        db.commit()
        
        # Create availability (Monday-Friday, 9 AM - 5 PM)
        for day in range(5):  # 0=Monday, 4=Friday
            existing_avail = db.query(Availability).filter(
                Availability.tenant_id == tenant.id,
                Availability.day_of_week == day
            ).first()
            
            if not existing_avail:
                availability = Availability(
                    tenant_id=tenant.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0)
                )
                db.add(availability)
                print(f"Created availability for day {day}")
        
        db.commit()
        
        print("\n✅ Preview data created successfully!")
        print(f"\nAccess the preview at:")
        print(f"http://localhost:8000/public/preview")
        print(f"http://localhost:8000/public/book")
        print(f"\nUse header: X-Tenant-Slug: preview-demo")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_preview_data()
