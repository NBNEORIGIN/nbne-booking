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
                "slug": "mind-department",
                "name": "The Mind Department",
                "subdomain": "mind",
                "email": "hello@theminddepartment.com",
                "phone": "+44-191-555-0100",
                "is_active": True,
                "settings": {
                    "timezone": "Europe/London",
                    "intake_form_required": True,
                    "booking_layout": "calendar",
                    "capacity_thresholds": {
                        "low": 3,
                        "sold_out": 0
                    }
                },
                "client_display_name": "The Mind Department",
                "logo_url": None,
                "primary_color": "#8D9889",
                "secondary_color": "#EEE8E5",
                "accent_color": "#27382E",
                "booking_page_title": "Mind Department Classes",
                "booking_page_intro": "Weekly mindfulness and workplace wellbeing sessions.",
                "location_text": "The Core, Newcastle",
                "contact_email": "hello@theminddepartment.com",
                "contact_phone": "+44-191-555-0100",
                "business_address": "The Core, Bath Lane, Newcastle upon Tyne",
                "social_links": {
                    "website": "https://www.theminddepartment.com"
                }
            },
            {
                "slug": "house-of-hair",
                "name": "House of Hair",
                "subdomain": "hair",
                "email": "bookings@houseofhair.example.com",
                "phone": "+44-191-555-0200",
                "is_active": True,
                "settings": {
                    "timezone": "Europe/London",
                    "booking_layout": "slot-picker",
                    "staff": [
                        {"id": "sarah", "name": "Sarah Ellis"},
                        {"id": "jade", "name": "Jade Turner"}
                    ],
                    "services": {
                        "cut-and-finish": {"duration_minutes": 60},
                        "colour-refresh": {"duration_minutes": 90}
                    }
                },
                "client_display_name": "House of Hair",
                "logo_url": None,
                "primary_color": "#2F2A2D",
                "secondary_color": "#F7EFEA",
                "accent_color": "#D99B66",
                "booking_page_title": "Book with House of Hair",
                "booking_page_intro": "Choose your stylist and service to reserve your slot.",
                "location_text": "NBNE Studio, Gateshead",
                "contact_email": "bookings@houseofhair.example.com",
                "contact_phone": "+44-191-555-0200",
                "business_address": "72 High Street, Gateshead, NE8 1EE",
                "social_links": {
                    "instagram": "https://instagram.com/houseofhair"
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
