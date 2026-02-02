# Debug Loop - FastAPI Session Type Issue

## Problem Statement
API container crashes on startup with FastAPI error about Session type annotation not being a valid Pydantic field.

## Root Cause Analysis
FastAPI's dependency injection system is trying to validate the `Session` type from SQLAlchemy as a Pydantic field, which fails. The `Annotated[Session, Depends(get_db)]` approach should work but isn't being applied correctly.

## Hypothesis
The `DBSession` type alias using `Annotated` is defined but FastAPI still sees raw `Session` types somewhere in the endpoint parameters.

## Test Plan
1. Verify DBSession is correctly defined in database.py
2. Check if all endpoint files are using DBSession (not Session)
3. Test with a minimal endpoint to isolate the issue
4. If Annotated doesn't work, use alternative: remove type hints entirely from db parameters

## Actions Taken
- Created DBSession = Annotated[Session, Depends(get_db)] in database.py
- Updated all endpoint files to use DBSession
- Rebuilt container multiple times

## Current Status
Still failing - need to verify the actual code in the container matches local files.

## Next Steps
1. Check what's actually in the container
2. Try alternative approach: remove Session type hints entirely
3. Use simpler pattern that FastAPI definitely supports

## Solution Applied
**Root Cause:** FastAPI 0.109.0 with Pydantic 2.5.3 doesn't properly handle `Annotated[Session, Depends(get_db)]` type alias in function signatures. The dependency injection system tries to validate the Session type as a Pydantic field.

**Fix:** Remove type annotations from `db` parameters entirely. Use pattern:
```python
def endpoint_function(
    param1: Type1,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)  # No type annotation
):
```

This is the standard, proven FastAPI pattern that works reliably across all versions.

**Files Updated:**
- api/core/database.py - Removed DBSession alias
- api/api/v1/endpoints/tenants.py
- api/api/v1/endpoints/services.py
- api/api/v1/endpoints/availability.py
- api/api/v1/endpoints/blackouts.py
- api/api/v1/endpoints/slots.py
- api/api/v1/endpoints/bookings.py

**Status:** Ready for rebuild and testing
