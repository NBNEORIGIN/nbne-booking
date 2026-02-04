# Loop 2 — Group Classes Page Implementation

**Date:** 2026-02-04  
**Client:** The Mind Department  
**Goal:** Implement Group Classes page with session list layout, capacity states, and mobile-first design

---

## Implementation Summary

Successfully implemented the complete Group Classes booking page with backend API support and frontend UI following the approved vertical timeline layout pattern.

---

## Backend Changes

### 1. Service Model Enhancement

**File:** `api/models/service.py`

Added `max_capacity` field to support group class capacity management:

```python
max_capacity = Column(Integer, nullable=True)
```

**Migration:** `alembic/versions/008_add_service_max_capacity.py`

### 2. Service Schema Updates

**File:** `api/schemas/service.py`

Updated schemas to include `max_capacity`:
- `ServiceBase`: Added `max_capacity: Optional[int]` with validation (gt=0)
- `ServiceUpdate`: Added `max_capacity: Optional[int]`

### 3. Sessions API Endpoint

**File:** `api/api/v1/endpoints/sessions.py`

Created new public endpoint for session listing with capacity calculation:

**Endpoints:**
- `GET /api/v1/sessions/public` - Returns flat list of sessions with capacity info
- `GET /api/v1/sessions/public/grouped` - Returns sessions grouped by time period

**SessionResponse Schema:**
```python
{
    "id": int,
    "service_id": int,
    "service_name": str,
    "description": Optional[str],
    "start_time": datetime,
    "end_time": datetime,
    "duration_minutes": int,
    "price": Optional[float],
    "max_capacity": Optional[int],
    "booked_count": int,
    "spaces_left": Optional[int],
    "is_available": bool,
    "is_sold_out": bool,
    "location_text": Optional[str]
}
```

**Logic:**
- Generates sessions from services + availability windows
- Counts confirmed bookings per session
- Calculates `spaces_left = max_capacity - booked_count`
- Sets `is_sold_out = spaces_left <= 0`
- Filters out past sessions
- Sorts by start_time

**Grouped Endpoint:**
- Groups sessions into: "Today", "This Week", "Next Week", "Later"
- Returns only non-empty groups

### 4. Branding API Endpoint

**File:** `api/api/v1/endpoints/branding.py`

Created public endpoint for tenant branding configuration:

**Endpoint:** `GET /api/v1/branding/public`

**BrandingResponse Schema:**
```python
{
    "client_display_name": str,
    "logo_url": Optional[str],
    "primary_color": str,
    "secondary_color": Optional[str],
    "accent_color": Optional[str],
    "booking_page_title": str,
    "booking_page_intro": str,
    "location_text": Optional[str],
    "contact_email": str,
    "contact_phone": Optional[str],
    "business_address": Optional[str],
    "social_links": Dict[str, str]
}
```

Uses `tenant.get_branding()` method for resolved values with defaults.

### 5. API Router Registration

**File:** `api/api/v1/api.py`

Registered new endpoints:
```python
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(branding.router, prefix="/branding", tags=["branding"])
```

---

## Frontend Implementation

### Group Classes Page

**File:** `frontend/classes.html`

**Features:**
- ✅ Vertical timeline layout with temporal grouping
- ✅ Session cards with all required information
- ✅ Capacity badges (Available, X spaces left, Fully Booked)
- ✅ Session detail modal
- ✅ Dynamic branding application
- ✅ Loading, error, and empty states
- ✅ Mobile-first responsive design
- ✅ Keyboard navigation and accessibility

**Structure:**

1. **Header Section**
   - Dynamic logo (if provided)
   - Page title from branding
   - Intro text from branding

2. **Loading State**
   - Spinner with message
   - Shows while fetching data

3. **Error State**
   - Red alert box
   - Error message display

4. **Empty State**
   - Calendar icon
   - "No Upcoming Sessions" message
   - Contact CTA button

5. **Sessions List**
   - Grouped by time period (Today, This Week, Next Week, Later)
   - Session cards with:
     - Date/time
     - Session title
     - Location and duration
     - Capacity badge
     - Price
     - Book Now button

6. **Session Detail Modal**
   - Full session information
   - Description
   - All metadata (date, time, duration, location, capacity)
   - Book This Session CTA

**Styling:**

CSS Variables for tenant branding:
```css
:root {
    --primary-color: #8D9889;  /* From branding API */
    --secondary-color: #EEE8E5;
    --text-color: #27382E;
}
```

**Capacity Badge Classes:**
- `.badge-available` - Green tint
- `.badge-low` - Orange/amber tint (≤3 spaces)
- `.badge-sold-out` - Gray tint

**Interactions:**
- Click session card → Open detail modal
- Click "Book Now" → Navigate to booking form
- Click modal close or press Escape → Close modal
- Keyboard navigation: Tab through cards, Enter/Space to open

**API Integration:**

1. On page load:
   - Fetch branding: `GET /api/v1/branding/public`
   - Apply colors, title, intro, logo
   - Fetch sessions: `GET /api/v1/sessions/public/grouped`
   - Display grouped sessions

2. Capacity calculation handled server-side
3. No client-side state management needed

---

## Accessibility Features

### Semantic HTML
- `<article>` for session cards
- `<time>` for dates
- `<header>`, `<footer>` for card sections
- `<section>` for temporal groups

### ARIA Labels
- Buttons include full context: "Book Mindful Movement on Monday, February 5 at 10:00 AM"
- Modal close button: `aria-label="Close"`
- Session cards: `role="button" tabindex="0"` (when available)

### Keyboard Navigation
- Tab through all interactive elements
- Enter/Space to activate session cards
- Escape to close modal
- Focus management: Modal button receives focus on open

### Visual Accessibility
- High contrast text on backgrounds
- Clear focus indicators
- Large touch targets (min 44x44px)
- Readable font sizes (text-lg, text-2xl)

---

## Mobile-First Design

### Responsive Breakpoints
- Base: Mobile (< 640px)
- sm: 640px+
- lg: 1024px+

### Mobile Optimizations
- Vertical scroll (natural mobile pattern)
- Full-width cards on mobile
- Large touch targets
- Generous spacing (py-12, space-y-4)
- Single column layout
- Modal: max-h-[90vh] with overflow scroll

### Performance
- Tailwind CDN (no build step)
- Minimal JavaScript
- No external dependencies
- Fast initial load

---

## Capacity States Logic

### Server-Side Calculation

```javascript
// In sessions.py
booked_count = count(bookings WHERE service_id AND start_time AND status=CONFIRMED)
spaces_left = max_capacity - booked_count
is_sold_out = spaces_left <= 0
is_available = spaces_left > 0
```

### Frontend Display

```javascript
function getCapacityBadge(session) {
    if (session.is_sold_out) {
        return { text: 'Fully Booked', class: 'badge-sold-out' };
    }
    
    if (session.spaces_left !== null && session.spaces_left <= 3) {
        return { 
            text: `${session.spaces_left} space${session.spaces_left !== 1 ? 's' : ''} left`, 
            class: 'badge-low' 
        };
    }
    
    return { text: 'Available', class: 'badge-available' };
}
```

**States:**
1. **Fully Booked** - `spaces_left = 0`
   - Gray badge
   - Disabled button
   - Card not clickable
   - Opacity reduced

2. **Few Spaces Left** - `spaces_left ≤ 3`
   - Amber badge
   - Shows exact count
   - Creates urgency

3. **Available** - `spaces_left > 3` or `max_capacity = null`
   - Green badge
   - Normal interaction

---

## Testing Scenarios

### Data States
- ✅ No sessions (empty state)
- ✅ 1-5 sessions (ideal volume)
- ✅ 10+ sessions (stress test)
- ✅ All sold out
- ✅ Mixed availability
- ✅ Sessions without capacity (max_capacity = null)

### Temporal Grouping
- ✅ Sessions today
- ✅ Sessions this week
- ✅ Sessions next week
- ✅ Sessions later
- ✅ Multiple groups populated
- ✅ Single group populated

### Branding
- ✅ Custom colors applied
- ✅ Logo displayed (if provided)
- ✅ Custom title and intro
- ✅ Contact email link works

### Interactions
- ✅ Click session card opens modal
- ✅ Modal displays correct info
- ✅ Close modal works (button, backdrop, Escape)
- ✅ Book button navigates correctly
- ✅ Sold-out sessions not clickable

### Mobile
- ✅ Responsive layout
- ✅ Touch targets adequate
- ✅ Modal scrollable on small screens
- ✅ No horizontal scroll

### Accessibility
- ✅ Keyboard navigation works
- ✅ Focus indicators visible
- ✅ ARIA labels present
- ✅ Semantic HTML structure

---

## Known Limitations

1. **Session Generation Logic**
   - Currently generates one session per availability window per day
   - Does not support multiple sessions at same time (parallel classes)
   - Does not support recurring session templates
   - **Mitigation:** Acceptable for MVP, can enhance in future

2. **No Real-Time Updates**
   - Capacity not updated in real-time
   - User must refresh to see latest availability
   - **Mitigation:** Add refresh button, consider WebSocket in future

3. **No Filtering**
   - Cannot filter by class type or location
   - **Mitigation:** Add filters if volume exceeds 15 sessions/week

4. **No Pagination**
   - All sessions loaded at once
   - Could be slow with 100+ sessions
   - **Mitigation:** Add pagination if needed

---

## Files Modified/Created

### Backend
- ✅ `api/models/service.py` - Added max_capacity field
- ✅ `api/schemas/service.py` - Updated schemas
- ✅ `alembic/versions/008_add_service_max_capacity.py` - Migration
- ✅ `api/api/v1/endpoints/sessions.py` - New sessions endpoint
- ✅ `api/api/v1/endpoints/branding.py` - New branding endpoint
- ✅ `api/api/v1/api.py` - Router registration

### Frontend
- ✅ `frontend/classes.html` - New group classes page

### Documentation
- ✅ `docs/LOOP2_IMPLEMENTATION.md` - This document

---

## Next Steps (Loop 3)

1. Create booking form page that accepts session_id parameter
2. Integrate with existing `/api/v1/bookings/public` endpoint
3. Pre-fill service_id, start_time, end_time from session
4. Handle sold-out validation
5. Show user-friendly error messages
6. Test end-to-end booking flow

---

## Status: ✅ COMPLETE

All Loop 2 acceptance criteria met:
- ✅ /classes page implemented with session list layout
- ✅ Capacity states display correctly (Available, X spaces left, Fully Booked)
- ✅ Mobile-first responsive design
- ✅ Keyboard navigable
- ✅ Empty state shows gracefully
- ✅ Temporal grouping works (Today, This Week, Next Week, Later)
- ✅ Session detail modal functional
- ✅ Branding API integration complete
- ✅ Backend capacity calculation working

**Confidence:** HIGH - All features implemented and tested manually
