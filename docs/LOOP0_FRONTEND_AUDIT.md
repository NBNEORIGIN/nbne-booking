# Loop 0 — Frontend Audit for The Mind Department

**Date:** 2026-02-04  
**Client:** The Mind Department  
**Objective:** Audit existing frontend components and identify reusable patterns for mindfulness/wellbeing class booking experience

---

## Executive Summary

The NBNE Booking App has a functional single-page booking form (`index.html`) and admin dashboard (`admin.html`). Both are standalone HTML files using Tailwind CSS and vanilla JavaScript. The current implementation is suitable for appointment-style bookings but needs adaptation for group class sessions with capacity management.

---

## Current Frontend Structure

### Existing Pages

1. **`/frontend/index.html`** - Public booking form
   - **Purpose:** Single-service appointment booking
   - **Current flow:** Service selection → Customer details → Date/Time → Submit
   - **Tech:** Vanilla JS, Tailwind CSS CDN, no build process
   - **API calls:** 
     - `GET /api/v1/services/public` - Load services
     - `POST /api/v1/bookings/public` - Submit booking

2. **`/frontend/admin.html`** - Admin dashboard
   - **Purpose:** View bookings, export CSV
   - **Features:** JWT login, booking list with filters, CSV export
   - **Not relevant for public booking experience**

### Current UX Flow (index.html)

```
1. Page loads → Fetch services
2. Display service cards (grid layout)
3. User selects service (card highlights)
4. User fills form:
   - Name, Email, Phone
   - Date picker (min: today)
   - Time dropdown (9 AM - 4 PM)
   - Notes textarea
5. Submit → POST to /bookings/public
6. Success message → Auto-reload after 3s
```

### Existing Components/Patterns

#### ✅ Reusable (Can Use As-Is)
- **Loading state:** Spinner with message
- **Error state:** Red alert box with message
- **Success state:** Green confirmation box
- **Form inputs:** Text, email, tel, date, select, textarea with consistent styling
- **Responsive layout:** Mobile-first with Tailwind breakpoints
- **API integration pattern:** Async/await with error handling

#### ⚠️ Needs Modification
- **Service display:** Currently grid of cards - needs to become session list
- **Date/Time selection:** Currently separate date + time dropdowns - needs session-based selection
- **No capacity handling:** No "sold out" or "few spaces left" states
- **No grouping:** Services shown flat, no temporal grouping (this week/next week)

#### ❌ Missing (Need to Build)
- **Session list view:** Upcoming sessions grouped by time period
- **Capacity indicators:** "3 spaces left", "Fully booked", "Available"
- **Session detail view:** Modal/page showing full session info
- **Intake form:** One-time registration before first booking
- **Empty state:** "No upcoming sessions" message
- **Past session handling:** Hide or show as "Past"
- **Tenant branding system:** Config-driven colors, fonts, logo

---

## Backend Capabilities Assessment

### Available Models

1. **Tenant** (`/api/models/tenant.py`)
   - ✅ Multi-tenant isolation ready
   - ✅ Branding fields: `primary_color`, `secondary_color`, `accent_color`, `logo_url`, `client_display_name`
   - ✅ Custom text: `booking_page_title`, `booking_page_intro`, `location_text`
   - ✅ Contact info: `contact_email`, `contact_phone`, `business_address`
   - ✅ `get_branding()` method returns resolved branding with defaults

2. **Service** (`/api/models/service.py`)
   - ✅ Basic fields: `name`, `description`, `duration_minutes`, `price`, `is_active`
   - ✅ Tenant-scoped
   - ❌ **Missing:** `max_capacity` field for group classes
   - ❌ **Missing:** `session_type` (one-off vs recurring)

3. **Booking** (`/api/models/booking.py`)
   - ✅ Customer info: `customer_name`, `customer_email`, `customer_phone`
   - ✅ Time slots: `start_time`, `end_time`
   - ✅ Status enum: `CONFIRMED`, `CANCELLED`, `COMPLETED`, `NO_SHOW`
   - ✅ Tenant-scoped
   - ❌ **Missing:** Link to intake/registration form completion

4. **Availability** (exists in `/api/models/availability.py`)
   - ✅ Day of week + time windows
   - ✅ Used by slot generator

5. **Blackout** (exists in `/api/models/`)
   - ✅ Block specific date/time ranges

### Available API Endpoints

#### Public Endpoints (No Auth)
- ✅ `GET /api/v1/services/public` - List active services for tenant
- ✅ `POST /api/v1/bookings/public` - Create booking
- ❌ **Missing:** `GET /api/v1/sessions/public` - List upcoming sessions with capacity
- ❌ **Missing:** `GET /api/v1/sessions/{id}` - Get session details
- ❌ **Missing:** `GET /api/v1/tenant/branding` - Get tenant branding config

#### Slot Generation
- ✅ `SlotGenerator` service exists (`/api/services/slot_generator.py`)
- ✅ Generates slots based on availability + blackouts
- ✅ `is_slot_available()` method for validation
- ❌ **Missing:** Capacity tracking per slot
- ❌ **Missing:** "Spaces left" calculation

---

## Gaps Analysis

### Critical Gaps (Must Build)

1. **Capacity Management**
   - Need to add `max_capacity` to Service model
   - Need to count bookings per session to calculate spaces left
   - Need API endpoint to return sessions with capacity info

2. **Session Concept**
   - Current system is slot-based (any time within availability)
   - Group classes need fixed sessions (specific date/time with capacity)
   - Options:
     - A) Extend Service model with `is_group_class` flag + `max_capacity`
     - B) Create new `Session` model (more complex, better for recurring)
   - **Decision needed in Loop 1**

3. **Intake Form System**
   - Need to track if user has completed intake for tenant
   - Options:
     - A) Add `intake_completed` JSON field to Booking (per-booking flag)
     - B) Create `CustomerProfile` model (better for returning customers)
   - **Decision needed in Loop 4**

4. **Tenant Branding API**
   - Need public endpoint to fetch branding config
   - Frontend needs to apply colors, fonts, logo dynamically

### Nice-to-Have (Can Defer)
- Calendar view (complex on mobile)
- Real-time capacity updates (WebSocket)
- Waitlist functionality
- Recurring session templates

---

## Layout Options Assessment (Preview for Loop 1)

### Option A: Upcoming Sessions List ⭐ **RECOMMENDED**
**Best for:** Low-medium volume (1-10 sessions/week)

**Structure:**
```
[This Week]
  Mon, Feb 5 • 10:00 AM - 11:00 AM
  Mindful Movement
  3 spaces left • £15
  [Book Now]

  Wed, Feb 7 • 6:00 PM - 7:00 PM
  Evening Meditation
  Fully Booked
  [Fully Booked]

[Next Week]
  ...
```

**Pros:**
- ✅ Simple, mobile-friendly
- ✅ Clear availability at a glance
- ✅ Low cognitive load (calm UX)
- ✅ Easy to implement
- ✅ Works well for sold-out states

**Cons:**
- ❌ Can get long with many sessions
- ❌ No visual calendar overview

### Option B: Month/Week Calendar View
**Best for:** High volume (10+ sessions/week)

**Pros:**
- ✅ Visual overview of availability
- ✅ Good for planning ahead

**Cons:**
- ❌ Complex on mobile (small touch targets)
- ❌ Higher implementation complexity
- ❌ More cognitive load (less calm)
- ❌ Harder to show capacity indicators

### Option C: Slot Picker (Day → Time)
**Best for:** Appointment-style bookings

**Cons:**
- ❌ Not appropriate for fixed group sessions
- ❌ Doesn't show session titles/descriptions
- ❌ Poor for sold-out visibility

**Recommendation:** Option A (List) as default, with Option B (Calendar) as future enhancement if volume increases.

---

## Reusable Code Inventory

### Can Reuse Unchanged

```javascript
// API call pattern
async function loadData() {
    try {
        const response = await fetch(`${API_URL}/endpoint`);
        if (!response.ok) throw new Error('Failed to load');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
}

// Form submission pattern
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    // ... API call ...
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit';
});

// State management pattern
document.getElementById('loading').classList.add('hidden');
document.getElementById('content').classList.remove('hidden');
```

### Tailwind Classes to Reuse

```css
/* Layout */
.max-w-4xl .mx-auto .px-4 .py-12

/* Cards */
.bg-white .rounded-lg .shadow-md .p-8

/* Buttons */
.bg-blue-600 .text-white .py-3 .px-6 .rounded-lg .font-semibold .hover:bg-blue-700

/* Inputs */
.w-full .px-4 .py-2 .border .border-gray-300 .rounded-lg .focus:ring-2 .focus:ring-blue-500

/* States */
.bg-red-50 .border-red-200 .text-red-700  /* Error */
.bg-green-50 .border-green-200 .text-green-700  /* Success */
```

### Need New Components

1. **Session Card Component**
   ```html
   <div class="session-card">
     <div class="session-header">
       <h3>Session Title</h3>
       <span class="session-time">Mon, Feb 5 • 10:00 AM</span>
     </div>
     <div class="session-details">
       <span class="capacity-badge">3 spaces left</span>
       <span class="price">£15</span>
     </div>
     <button class="book-btn">Book Now</button>
   </div>
   ```

2. **Capacity Badge Component**
   ```html
   <!-- Available -->
   <span class="badge-available">Available</span>
   
   <!-- Low capacity -->
   <span class="badge-low">3 spaces left</span>
   
   <!-- Sold out -->
   <span class="badge-sold-out">Fully Booked</span>
   ```

3. **Session Detail Modal**
   ```html
   <div class="modal">
     <div class="modal-content">
       <h2>Session Title</h2>
       <p>Full description...</p>
       <div class="session-info">
         <span>Date/Time</span>
         <span>Duration</span>
         <span>Location</span>
         <span>Capacity</span>
       </div>
       <button>Book This Session</button>
     </div>
   </div>
   ```

4. **Intake Form Component**
   ```html
   <form class="intake-form">
     <h2>Welcome! Tell us about yourself</h2>
     <p>We need a few details before your first booking.</p>
     <!-- Minimal fields -->
     <input type="text" placeholder="Full Name" required>
     <input type="email" placeholder="Email" required>
     <input type="tel" placeholder="Phone" required>
     <label>
       <input type="checkbox" required>
       I agree to the privacy policy
     </label>
     <button>Continue to Booking</button>
   </form>
   ```

---

## Technical Constraints

### Must Preserve
- ✅ Multi-tenant isolation (all queries scoped to tenant_id)
- ✅ No build process (vanilla JS + Tailwind CDN)
- ✅ Mobile-first responsive design
- ✅ Accessibility basics (keyboard nav, ARIA labels)
- ✅ CSRF protection (public endpoints exempt)

### Can Modify
- ✅ HTML structure and layout
- ✅ JavaScript logic and flow
- ✅ Tailwind classes and styling
- ✅ API endpoint structure (add new endpoints)
- ✅ Database models (add fields/tables with migrations)

### Cannot Do
- ❌ Fork codebase per client
- ❌ Hardcode client branding in frontend
- ❌ Break tenant isolation
- ❌ Introduce complex build tools (keep it simple)

---

## Next Steps (Loop 1)

1. **Make Layout Decision**
   - Confirm Option A (List) as default
   - Document rationale in `/docs/decisions.md`

2. **Define Session Data Model**
   - Decide: Extend Service vs Create Session model
   - Plan database migration

3. **Design Capacity System**
   - How to track bookings per session
   - How to calculate "spaces left"
   - How to handle sold-out state

4. **Plan API Endpoints**
   - `GET /api/v1/sessions/public?tenant_id=X&from_date=Y`
   - `GET /api/v1/tenant/branding`

---

## Audit Conclusion

**PASS** ✅

### Summary
- Current codebase provides solid foundation
- Existing patterns (API calls, form handling, states) are reusable
- Main gaps: capacity management, session concept, intake form, branding API
- Recommended approach: List layout (Option A) for calm, mobile-friendly UX
- Implementation is feasible within existing architecture

### Confidence Level
**High** - No blockers identified. All gaps can be filled with incremental additions that preserve multi-tenant isolation and existing patterns.

---

**Next Loop:** Loop 1 - Frontend Layout Assessment & Decision
