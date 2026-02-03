# Branding Guide - NBNE Booking

## Overview

The NBNE Booking system supports full white-label branding for each tenant. This guide explains how branding works and how to customize it.

## Branding Fields

### Basic Information

**Client Display Name**
- What customers see in the header
- Falls back to tenant name if not set
- Example: "Acme Corporation"

**Logo URL**
- Optional URL to your logo image
- Recommended size: 200x60px (max height 60px)
- Formats: PNG, SVG, JPG
- Example: `https://example.com/logo.png`

### Brand Colors

**Primary Color** (Required)
- Main brand color
- Used for: Header background, primary buttons
- Default: `#2196F3` (blue)
- Must be hex format: `#RRGGBB`

**Secondary Color** (Optional)
- Complementary color
- Auto-generated if not set (darker shade of primary)
- Used for: Hover states, secondary elements

**Accent Color** (Optional)
- Call-to-action color
- Auto-generated if not set (green)
- Used for: CTA buttons, highlights, focus indicators
- Default: `#4CAF50` (green)

### Booking Page Content

**Page Title**
- Browser tab title and page heading
- Default: "Book Your Appointment"
- Example: "Schedule Your Consultation"

**Welcome Message**
- Introductory text on booking page
- Displayed below page title
- Example: "Welcome! Select a service and time that works for you."

### Contact Information

**Location Text**
- Short location description
- Displayed in header
- Example: "London, UK" or "123 Main St"

**Contact Email**
- Public-facing email address
- Displayed in header and footer
- Falls back to tenant email if not set

**Contact Phone**
- Public-facing phone number
- Displayed in header and footer
- Falls back to tenant phone if not set

**Business Address**
- Full business address
- Optional, displayed in footer
- Example: "123 Main Street\nLondon, UK\nSW1A 1AA"

**Social Links** (Future)
- JSON object with social media links
- Example: `{"facebook": "https://fb.com/...", "twitter": "..."}`

## Color Accessibility

### Automatic Contrast Calculation

The system automatically calculates appropriate text colors for backgrounds to ensure WCAG AA compliance (4.5:1 contrast ratio).

**How it works:**
1. System calculates relative luminance of background color
2. Chooses white (#FFFFFF) or black (#000000) text
3. Ensures minimum 4.5:1 contrast ratio

**Example:**
- Light background (#FF5722) → Black text (#000000)
- Dark background (#1976D2) → White text (#FFFFFF)

### Color Variants

The system automatically generates color variants:
- **Light**: 20% lighter than base color
- **Dark**: 20% darker than base color

Used for hover states and visual hierarchy.

## Best Practices

### Colors

✅ **Do:**
- Use your brand's primary color
- Test colors on different devices
- Ensure sufficient contrast
- Use accent color for CTAs

❌ **Don't:**
- Use very light colors for primary (poor contrast)
- Use similar colors for primary and accent
- Use more than 3 brand colors
- Ignore accessibility warnings

### Logo

✅ **Do:**
- Use transparent PNG or SVG
- Keep logo simple and readable
- Test logo on colored background
- Use appropriate dimensions (200x60px recommended)

❌ **Don't:**
- Use very large images (slow loading)
- Use logos with text that's too small
- Use logos that don't work on colored backgrounds

### Content

✅ **Do:**
- Keep welcome message concise (1-2 sentences)
- Use friendly, professional tone
- Include location if you have physical premises
- Provide accurate contact information

❌ **Don't:**
- Write long paragraphs
- Use jargon or technical terms
- Include pricing in welcome message
- Forget to update contact info

## Editing Branding

### Via Admin Interface

1. Log in to admin panel
2. Navigate to "Branding" page
3. Edit fields in the form
4. See live preview update in real-time
5. Click "Save Changes"
6. View full preview in new tab

### Via API

```bash
# Update branding via API
curl -X PATCH https://your-domain.com/api/v1/tenants/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "primary_color": "#FF5722",
    "client_display_name": "My Business",
    "booking_page_intro": "Welcome! Book your appointment today."
  }'
```

### Via Database

```sql
-- Update branding directly in database
UPDATE tenants 
SET primary_color = '#FF5722',
    client_display_name = 'My Business',
    booking_page_intro = 'Welcome! Book your appointment today.'
WHERE id = 1;
```

## Preview Your Branding

### Full Preview Page
Visit: `/public/preview` with `X-Tenant-Slug` header

Shows:
- Complete color palette
- All UI components
- Contact information
- CSS variables reference

### Live Booking Page
Visit: `/public/book` with `X-Tenant-Slug` header

Shows actual booking flow with your branding.

## Examples

### Professional Services (Blue)
```json
{
  "primary_color": "#2196F3",
  "accent_color": "#4CAF50",
  "client_display_name": "Professional Consulting",
  "booking_page_intro": "Schedule your consultation with our expert team."
}
```

### Creative Agency (Purple)
```json
{
  "primary_color": "#9C27B0",
  "accent_color": "#FF9800",
  "client_display_name": "Creative Studio",
  "booking_page_intro": "Let's bring your vision to life. Book a discovery session."
}
```

### Healthcare (Teal)
```json
{
  "primary_color": "#009688",
  "accent_color": "#FF5722",
  "client_display_name": "Health & Wellness Clinic",
  "booking_page_intro": "Book your appointment online. We're here to help."
}
```

## Troubleshooting

**Colors not updating?**
- Clear browser cache
- Check hex format (#RRGGBB)
- Verify save was successful

**Logo not showing?**
- Check URL is accessible
- Verify image format (PNG/SVG/JPG)
- Check image dimensions

**Text hard to read?**
- System auto-calculates contrast
- Try different primary color
- Check on multiple devices

## Support

For branding assistance, contact: support@nbnesigns.co.uk
