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

## Template for New Decisions

### [Loop X] Decision Title
**Date:** YYYY-MM-DD  
**Context:** What problem are we solving?  
**Decision:** What did we decide?  
**Rationale:** Why did we choose this?  
**Consequences:** What are the trade-offs?  
**Status:** Accepted
