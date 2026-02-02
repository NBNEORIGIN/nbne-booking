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

## Template for New Decisions

### [Loop X] Decision Title
**Date:** YYYY-MM-DD  
**Context:** What problem are we solving?  
**Decision:** What did we decide?  
**Rationale:** Why did we choose this?  
**Consequences:** What are the trade-offs?  
**Status:** Accepted
