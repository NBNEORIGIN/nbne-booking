# Architecture Decision Records

## Format
Each decision should include:
- **Date**: When the decision was made
- **Context**: What prompted the decision
- **Decision**: What was decided
- **Rationale**: Why this choice was made
- **Consequences**: Trade-offs and implications
- **Status**: Accepted, Superseded, Deprecated

---

## Decision Log

### [Loop 0] Stack Selection
**Date:** 2026-02-02  
**Context:** Need to choose backend framework, database, and deployment platform for MVP.  
**Decision:** 
- Backend: FastAPI (Python 3.11)
- Database: PostgreSQL 15
- ORM: SQLAlchemy 2.0
- Migrations: Alembic
- Frontend: Server-rendered templates (FastAPI Jinja2) for admin UI
- Deployment: Render
- Local Dev: Docker + docker-compose

**Rationale:**
- **FastAPI**: Modern, fast, automatic API docs, excellent for rapid MVP development, type hints for safety
- **PostgreSQL**: Robust ACID compliance needed for booking conflicts, excellent for multi-tenancy, JSON support for flexible tenant settings
- **SQLAlchemy 2.0**: Mature ORM with strong transaction support for double-booking prevention
- **Alembic**: Industry standard for database migrations, integrates seamlessly with SQLAlchemy
- **Server-rendered templates**: Simpler than separate React app for MVP admin UI, reduces complexity, faster to build
- **Render**: Free tier with PostgreSQL support, easy deployment, suitable for pilot phase
- **Docker**: Consistent dev environment, one-command startup, matches production deployment

**Consequences:**
- Python ecosystem means excellent libraries for email/SMS
- FastAPI async support allows future scalability
- Server-rendered UI means less client-side complexity but may need refactor if complex interactions needed
- Docker requirement adds slight local setup overhead but ensures consistency
- Render free tier has limitations (sleeps after inactivity) but acceptable for pilot

**Status:** Accepted

---

### [Frontend Loop 0] Frontend Tech Stack for Public Booking UI
**Date:** 2026-02-02  
**Context:** Need to build a customizable, branded public booking frontend that supports multiple tenants without per-client code forks. Must integrate with existing FastAPI backend and tenant resolution system.

**Decision:**
- **Frontend Approach**: Server-rendered templates (Jinja2)
- **CSS Framework**: Tailwind CSS (via CDN for MVP)
- **JavaScript**: Vanilla JS for minimal interactivity
- **Template Location**: `api/templates/public/` (separate from admin templates)
- **Branding Storage**: New columns in `tenants` table (not JSON settings)
- **Routing**: `/{tenant}/book/*` or subdomain-based (leveraging existing middleware)

**Rationale:**
1. **Consistency**: Backend already uses Jinja2 for admin UI - proven pattern
2. **Simplicity**: No separate frontend build/deploy pipeline needed
3. **Tenant Resolution**: Existing `TenantMiddleware` handles tenant context automatically
4. **No CORS**: Same origin as API eliminates CORS complexity
5. **SEO-Friendly**: Server-rendered HTML is search engine friendly
6. **Fastest Development**: Leverage existing infrastructure and patterns
7. **Type Safety**: Branding as DB columns provides validation and type safety
8. **Deployment**: Single deployment artifact (no separate frontend server)

**Rejected Alternatives:**
- **Separate Next.js/React Frontend**: Adds complexity (separate deployment, CORS, build pipeline, state management), slower development
- **Vue/Nuxt**: Same issues as React, less familiar to team
- **Static Site Generator**: Cannot handle dynamic per-tenant branding without rebuild
- **JSON Settings for Branding**: Less type-safe, harder to query/validate, not discoverable in schema

**Consequences:**
- **Pros**:
  - Faster development (no frontend framework learning curve)
  - Simpler deployment (one app, one container)
  - Tenant branding immediately available via middleware
  - No API versioning concerns for frontend
  - Server-side rendering for better initial load
- **Cons**:
  - Less interactive UI (acceptable for booking flow)
  - Tailwind via CDN means larger initial CSS load (can optimize later with build step)
  - May need refactor if complex client-side interactions needed later
  - Requires database migration for branding fields

**Migration Path if Needed:**
- If future requirements demand rich client-side interactions, can build separate SPA while keeping server-rendered templates as fallback
- Branding data model will work for both approaches
- API endpoints already support headless consumption

**Status:** Accepted

---

### [The Mind Department - Loop 1] Group Classes Layout Pattern
**Date:** 2026-02-04  
**Context:** The Mind Department needs a public booking page for mindfulness/wellbeing group classes. Must show upcoming sessions with capacity (sold out, few spaces, available) in a calm, mobile-first UX that matches their grounded, non-pushy brand.

**Decision:** Implement **Upcoming Sessions List** (vertical timeline) as default layout pattern.

**Layout Structure:**
- Temporal grouping: "Today", "This Week", "Next Week", "Later"
- Session cards showing: date/time, title, location, duration, capacity badge, price, CTA
- Capacity states: "Available", "X spaces left", "Fully Booked"
- Vertical scroll, one session per row
- Mobile-first responsive design

**Rationale:**
1. **Mobile Excellence**: Vertical scroll is natural on phones (70%+ of wellness bookings). Large touch targets, no pinch-zoom needed.
2. **Calm UX**: Simple linear flow with generous spacing. Low cognitive load matches mindfulness audience.
3. **Capacity Transparency**: "3 spaces left" badge immediately visible. No hidden information.
4. **Implementation Safety**: Low technical risk, reuses existing patterns, accessible by default.
5. **Brand Alignment**: Calm, grounded aesthetic with generous whitespace feels premium, not cluttered.

**Alternatives Considered:**
- **Calendar Grid View**: Rejected - too complex on mobile, higher cognitive load, harder to show capacity in small cells. Score: 5.05/10
- **Slot Picker (Day → Time)**: Rejected - wrong model for fixed group sessions, poor capacity visibility, higher friction. Score: 5.85/10
- **List View**: Selected - best mobile UX, clearest capacity visibility, lowest cognitive load. Score: 9.15/10

**Consequences:**
- **Pros**:
  - Excellent mobile experience (primary device for wellness clients)
  - Clear capacity visibility reduces booking friction
  - Simple implementation with low technical risk
  - Accessible by default (linear navigation)
  - Scales well for 1-10 sessions/week
- **Cons**:
  - Can get long with 10+ sessions (requires scrolling)
  - No visual calendar overview
  - Limited multi-dimensional filtering

**Fallback Strategy:**
If session volume exceeds 15/week for 3 consecutive months:
1. Add filter by class type (Meditation, Movement, etc.)
2. Add pagination (10 sessions per page)
3. Consider calendar view as optional toggle (feature flag)

**Success Metrics:**
- Mobile booking completion rate > 70%
- Average time to book < 2 minutes
- User feedback score > 4/5 for "ease of use"

**Review Date:** May 2026 (after 3 months of usage)

**Status:** Accepted

---

## Template for New Decisions

### [Loop X] Decision Title
**Date:** YYYY-MM-DD  
**Context:** What problem are we solving?  
**Decision:** What did we decide?  
**Rationale:** Why did we choose this?  
**Consequences:** What are the trade-offs?  
**Status:** Accepted
