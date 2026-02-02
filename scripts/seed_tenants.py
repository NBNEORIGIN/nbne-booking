#!/usr/bin/env python3
"""
Seed script to create test tenants for development.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.core.database import SessionLocal
from api.models.tenant import Tenant


def seed_tenants():
    """Create test tenants for development."""
    db = SessionLocal()
    
    try:
        # Check if tenants already exist
        existing_count = db.query(Tenant).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} tenant(s). Skipping seed.")
            return
        
        tenants_data = [
            {
                "slug": "acme-corp",
                "name": "Acme Corporation",
                "subdomain": "acme",
                "email": "bookings@acme-corp.example.com",
                "phone": "+1-555-0100",
                "is_active": True,
                "settings": {
                    "timezone": "America/New_York",
                    "business_hours": {
                        "monday": {"start": "09:00", "end": "17:00"},
                        "tuesday": {"start": "09:00", "end": "17:00"},
                        "wednesday": {"start": "09:00", "end": "17:00"},
                        "thursday": {"start": "09:00", "end": "17:00"},
                        "friday": {"start": "09:00", "end": "17:00"}
                    }
                }
            },
            {
                "slug": "beauty-salon",
                "name": "Beauty & Wellness Salon",
                "subdomain": "beauty",
                "email": "appointments@beautysalon.example.com",
                "phone": "+1-555-0200",
                "is_active": True,
                "settings": {
                    "timezone": "America/Los_Angeles",
                    "business_hours": {
                        "tuesday": {"start": "10:00", "end": "19:00"},
                        "wednesday": {"start": "10:00", "end": "19:00"},
                        "thursday": {"start": "10:00", "end": "19:00"},
                        "friday": {"start": "10:00", "end": "19:00"},
                        "saturday": {"start": "09:00", "end": "17:00"}
                    }
                }
            },
            {
                "slug": "tech-consulting",
                "name": "Tech Consulting Group",
                "subdomain": "techconsult",
                "email": "meetings@techconsulting.example.com",
                "phone": "+1-555-0300",
                "is_active": True,
                "settings": {
                    "timezone": "America/Chicago",
                    "business_hours": {
                        "monday": {"start": "08:00", "end": "18:00"},
                        "tuesday": {"start": "08:00", "end": "18:00"},
                        "wednesday": {"start": "08:00", "end": "18:00"},
                        "thursday": {"start": "08:00", "end": "18:00"},
                        "friday": {"start": "08:00", "end": "16:00"}
                    }
                }
            }
        ]
        
        for tenant_data in tenants_data:
            tenant = Tenant(**tenant_data)
            db.add(tenant)
            print(f"✓ Created tenant: {tenant_data['name']} (slug: {tenant_data['slug']})")
        
        db.commit()
        print(f"\n✓ Successfully seeded {len(tenants_data)} tenants")
        
    except Exception as e:
        print(f"✗ Error seeding tenants: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_tenants()
