# Loop 1 — Frontend Layout Decision for The Mind Department

**Date:** 2026-02-04  
**Client:** The Mind Department  
**Decision Type:** UI/UX Pattern Selection  
**Status:** APPROVED ✅

> **2026-02-04 Reassessment:** Client direction and MASTER_WIGGUM_PROMPT require a calendar/grid experience for group classes. This document now records the refreshed Loop 1 decision to implement a **calendar grid (compact week view)** as the default layout, superseding the earlier sessions-list recommendation. The original analysis remains below for traceability.

---

## Reassessment Summary (Calendar Grid Layout)

### Why the Decision Changed
- **Client expectation:** The Mind Department explicitly asked for a grid/calendar to view classes “week at a glance”.
- **WIGGUM mandate:** MASTER_WIGGUM_PROMPT prioritises calendar/grid visibility for group sessions to reduce ambiguity.
- **Multi-tenant parity:** A week-grid primitive supports House of Hair slot picker work later while keeping shared components.
- **Commercial fit:** Calendar overview differentiates NBNE platform from simple list-based competitors.

### Selected Pattern — Compact 7-Day Grid
- **Layout:** Horizontal row of the next 7 calendar days (rolling window), each column listing sessions with availability badges.
- **Interaction:** Tap/click column expands modal (detail + CTA) — no page reloads.
- **Availability states:** Colour-coded badges (available, few left, sold out, closed, past) surfaced inside each cell.
- **Responsive treatment:** On mobile the grid becomes horizontal scroll cards with sticky weekday headers.
- **Accessibility:** Grid uses `<table>` semantics with ARIA roles; keyboard navigation jumps day-to-day, session-to-session.

### Key Advantages vs Original List
1. **At-a-glance planning:** Users can see distribution across the week without scanning a long list.
2. **Capacity signalling:** Badge legend in header plus per-session chips reduce ambiguity.
3. **Pathless ready:** URLs remain `/classes` with query params (`?view=week&start=<date>`), no subpaths.
4. **Scalable:** Multi-column layout handles increased volume (12+ sessions) without infinite scroll fatigue.
5. **Tenant branding:** Column headers inherit CSS variables, enabling distinctive palettes per tenant configuration.

### Implementation Signals for Loop 2
- Build grid component fed by `/sessions/public/grouped` with new grouping transforms.
- Introduce availability legend + toggle to switch between week grid and list (feature flag for future).
- Ensure empty/holiday days show “No sessions” state without collapsing column height.
- Add responsive breakpoints: desktop (7 columns), tablet (4 columns), mobile (horizontal scroll timeline).

### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Grid overwhelms mobile users | Medium | Medium | Implement horizontal scroll with snap points, provide “View as list” fallback in feature flag |
| Capacity badge clutter | Low | Medium | Use concise badges + legend, hide zero states |
| Keyboard navigation complexity | Medium | High | Define roving tabindex, add skip links, test with NVDA/VoiceOver |
| Implementation effort | Medium | Medium | Break work into reusable components (calendar grid, session card partials) |

### Documentation Actions
- Update `/docs/decisions.md` with calendar-grid ADR.
- Note layout toggle strategy in `/docs/LOOP2_IMPLEMENTATION.md` after development.
- Reflect change in WIGGUM loop log (done in Loop 1 review step).

---

> Original 2026-02-02 analysis retained below (archived for reference).

---

## Decision Context

The Mind Department needs a public-facing "Group Classes" booking page for mindfulness, meditation, and wellbeing sessions. The page must feel calm, minimal, and low-friction while clearly showing availability and capacity.

### Client Requirements
- **Audience:** Mindfulness/meditation/wellbeing clients
- **Brand tone:** Grounded, simple, non-pushy
- **Key needs:** 
  - Show upcoming sessions
  - Display capacity (sold out, few spaces, available)
  - Low cognitive load (calm UX)
  - Mobile-first
  - Handle empty states gracefully

### Technical Constraints
- Must work on mobile (primary device for wellness clients)
- No build process (vanilla JS + Tailwind)
- Multi-tenant (config-driven, no forks)
- Accessibility basics required

---

## Layout Options Evaluated

### Option A: Upcoming Sessions List (Vertical Timeline)

**Visual Structure:**
```
┌─────────────────────────────────────┐
│  This Week                          │
├─────────────────────────────────────┤
│  Mon, Feb 5 • 10:00 AM - 11:00 AM  │
│  Mindful Movement                   │
│  In-person • 60 min                 │
│  [3 spaces left] £15                │
│  [Book Now]                         │
├─────────────────────────────────────┤
│  Wed, Feb 7 • 6:00 PM - 7:00 PM    │
│  Evening Meditation                 │
│  Online • 45 min                    │
│  [Fully Booked]                     │
│  [Fully Booked]                     │
├─────────────────────────────────────┤
│  Next Week                          │
├─────────────────────────────────────┤
│  Mon, Feb 12 • 10:00 AM             │
│  ...                                │
└─────────────────────────────────────┘
```

**Pros:**
- ✅ **Mobile-first:** Vertical scroll is natural on phones
- ✅ **Calm UX:** Simple, linear flow with generous spacing
- ✅ **Clear availability:** Capacity badge visible at a glance
- ✅ **Low cognitive load:** One session at a time, no complex grid
- ✅ **Easy to scan:** Temporal grouping (This Week, Next Week) aids navigation
- ✅ **Sold-out clarity:** Disabled button + badge makes status obvious
- ✅ **Implementation simplicity:** Straightforward HTML/CSS
- ✅ **Accessibility:** Screen readers can navigate linearly
- ✅ **Empty state friendly:** "No sessions this week" message is natural

**Cons:**
- ❌ **Can get long:** With 10+ sessions, requires scrolling
- ❌ **No visual calendar:** Can't see "big picture" of month
- ❌ **Limited filtering:** Harder to show multiple dimensions (location, type)

**Best for:** Low-medium volume (1-10 sessions/week)

**Score:** 9/10 for mindfulness audience

---

### Option B: Month/Week Calendar Grid

**Visual Structure:**
```
┌─────────────────────────────────────┐
│  February 2026                      │
│  S  M  T  W  T  F  S                │
│           1  2  3  4                │
│  5  6  7  8  9 10 11                │
│     •  •     •                      │
│ 12 13 14 15 16 17 18                │
│  •  •  •  •                         │
└─────────────────────────────────────┘
│  Mon, Feb 5                         │
│  10:00 AM - Mindful Movement        │
│  6:00 PM - Evening Meditation       │
└─────────────────────────────────────┘
```

**Pros:**
- ✅ **Visual overview:** See entire month at a glance
- ✅ **Planning ahead:** Good for users booking multiple sessions
- ✅ **Familiar pattern:** Everyone knows how calendars work

**Cons:**
- ❌ **Mobile complexity:** Small touch targets, hard to show capacity
- ❌ **Higher cognitive load:** Grid requires more mental processing
- ❌ **Less calm:** Busy visual, more "corporate" feel
- ❌ **Implementation complexity:** Responsive calendar is challenging
- ❌ **Capacity indicators:** Hard to show "3 spaces left" in small cells
- ❌ **Sold-out visibility:** Requires clicking into day to see status
- ❌ **Empty days:** Lots of empty cells if sessions are sparse

**Best for:** High volume (10+ sessions/week), corporate audiences

**Score:** 5/10 for mindfulness audience

---

### Option C: Slot Picker (Day → Time)

**Visual Structure:**
```
┌─────────────────────────────────────┐
│  Select a Date                      │
│  [Date Picker]                      │
├─────────────────────────────────────┤
│  Available Times                    │
│  [9:00 AM]  [10:00 AM]  [11:00 AM] │
│  [2:00 PM]  [3:00 PM]   [4:00 PM]  │
└─────────────────────────────────────┘
```

**Pros:**
- ✅ **Familiar:** Matches appointment booking pattern
- ✅ **Compact:** Two-step selection is space-efficient

**Cons:**
- ❌ **Wrong model:** Group classes are fixed sessions, not open slots
- ❌ **No session context:** Can't show class title/description until time selected
- ❌ **Poor capacity visibility:** Hard to show "sold out" before selection
- ❌ **Not browseable:** Can't see "what's coming up" without clicking dates
- ❌ **Higher friction:** Two steps instead of one

**Best for:** Appointment-style bookings (1-on-1 services)

**Score:** 3/10 for group classes

---

## Decision Criteria Matrix

| Criterion | Weight | Option A (List) | Option B (Calendar) | Option C (Slot) |
|-----------|--------|-----------------|---------------------|-----------------|
| **Mobile usability** | 20% | 10/10 | 4/10 | 7/10 |
| **Calm UX (low cognitive load)** | 20% | 10/10 | 5/10 | 6/10 |
| **Capacity visibility** | 15% | 10/10 | 4/10 | 3/10 |
| **Sold-out clarity** | 15% | 10/10 | 6/10 | 4/10 |
| **Implementation simplicity** | 10% | 9/10 | 4/10 | 7/10 |
| **Accessibility** | 10% | 9/10 | 6/10 | 8/10 |
| **Empty state handling** | 5% | 10/10 | 3/10 | 5/10 |
| **Scalability (volume)** | 5% | 6/10 | 9/10 | 7/10 |
| **TOTAL** | 100% | **9.15/10** | **5.05/10** | **5.85/10** |

---

## Recommendation: Option A (Upcoming Sessions List)

### Primary Rationale

**1. Audience Alignment**
- Mindfulness clients value simplicity and calm
- Vertical scroll is meditative, not overwhelming
- Clear information hierarchy reduces decision fatigue

**2. Mobile-First Excellence**
- 70%+ of wellness bookings happen on mobile
- Vertical list is native mobile pattern
- Large touch targets (entire session card)
- No pinch-zoom needed

**3. Capacity Transparency**
- "3 spaces left" badge is immediately visible
- "Fully booked" state is unambiguous
- No hidden information requiring clicks

**4. Implementation Safety**
- Low technical risk
- Reuses existing component patterns
- Easy to test and iterate
- Accessible by default

**5. Brand Consistency**
- Calm, grounded aesthetic matches The Mind Department
- Generous whitespace feels premium, not cluttered
- Non-pushy: information is clear but not aggressive

### Fallback Strategy

If session volume grows beyond 10/week:
- **Phase 1:** Add filter by class type (Meditation, Movement, etc.)
- **Phase 2:** Add "Show more" pagination (10 sessions per page)
- **Phase 3:** Consider calendar view as optional toggle (feature flag)

**Trigger:** If average sessions/week > 15 for 3 consecutive months

---

## Implementation Specifications

### Temporal Grouping
```javascript
const groups = [
  { label: "Today", sessions: [...] },
  { label: "This Week", sessions: [...] },
  { label: "Next Week", sessions: [...] },
  { label: "Later", sessions: [...] }
];
```

### Capacity States
```javascript
const getCapacityBadge = (spacesLeft, maxCapacity) => {
  if (spacesLeft === 0) return { text: "Fully Booked", class: "badge-sold-out" };
  if (spacesLeft <= 3) return { text: `${spacesLeft} spaces left`, class: "badge-low" };
  if (spacesLeft < maxCapacity * 0.5) return { text: "Available", class: "badge-available" };
  return { text: "Available", class: "badge-available" };
};
```

### Session Card Structure
```html
<article class="session-card">
  <header class="session-header">
    <time class="session-datetime">Mon, Feb 5 • 10:00 AM - 11:00 AM</time>
    <h3 class="session-title">Mindful Movement</h3>
  </header>
  
  <div class="session-meta">
    <span class="session-location">In-person</span>
    <span class="session-duration">60 min</span>
  </div>
  
  <footer class="session-footer">
    <div class="session-capacity">
      <span class="capacity-badge badge-low">3 spaces left</span>
      <span class="session-price">£15</span>
    </div>
    <button class="btn-book" aria-label="Book Mindful Movement on Monday, February 5 at 10:00 AM">
      Book Now
    </button>
  </footer>
</article>
```

### Empty State
```html
<div class="empty-state">
  <svg class="empty-icon"><!-- Calendar icon --></svg>
  <h3>No sessions scheduled</h3>
  <p>Check back soon for upcoming classes, or contact us to learn more.</p>
  <a href="mailto:hello@theminddepartment.com" class="btn-secondary">Get in Touch</a>
</div>
```

---

## Accessibility Considerations

### Keyboard Navigation
- Tab through session cards sequentially
- Enter/Space to activate "Book Now" button
- Skip links: "Skip to next week"

### Screen Reader
- Semantic HTML: `<article>`, `<time>`, `<h3>`
- ARIA labels on buttons include full context
- Capacity state announced: "3 spaces remaining"
- Sold-out state: "Fully booked, booking unavailable"

### Visual
- Minimum contrast ratio: 4.5:1 (WCAG AA)
- Focus indicators: 2px solid outline
- Touch targets: Minimum 44x44px

---

## Testing Plan

### Manual Testing
1. **Mobile devices:**
   - iPhone SE (small screen)
   - iPhone 14 Pro (standard)
   - Samsung Galaxy S23 (Android)
2. **Browsers:**
   - Safari (iOS)
   - Chrome (Android)
   - Firefox (desktop)
3. **Scenarios:**
   - 0 sessions (empty state)
   - 1-5 sessions (ideal)
   - 10+ sessions (stress test)
   - All sold out
   - Mixed availability

### Accessibility Testing
- VoiceOver (iOS)
- TalkBack (Android)
- Keyboard-only navigation
- Color contrast checker

### Performance
- Page load < 2s on 3G
- No layout shift (CLS < 0.1)
- Smooth scroll on low-end devices

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Too many sessions (>20/week) | Low | Medium | Add pagination + filters |
| Users want calendar view | Low | Low | Feature flag for optional calendar |
| Capacity calculation errors | Medium | High | Thorough testing + API validation |
| Mobile performance issues | Low | Medium | Lazy load images, minimize JS |

---

## Decision Log

**Decision:** Implement compact 7-day calendar grid (week-at-a-glance) as default layout, retaining list view as optional fallback for future A/B testing.

**Decided by:** Development team  
**Date:** 2026-02-04  
**Approved by:** Product owner  

**Alternatives considered:** Session list (archived), slot picker  
**Reason for selection:** Aligns with client/WIGGUM requirements for calendar visibility; supports multi-tenant parity and commercial differentiation.  
**Risks:** Increased implementation effort, responsive complexity (addressed in mitigation plan above).

**Review date:** After 3 months of usage (May 2026)  
**Success metrics:**
- Calendar comprehension score in client testing ≥ 4/5
- Mobile booking completion rate > 65%
- Average time to identify suitable slot < 90 seconds
- Support requests about “finding sessions” reduced vs baseline

---

## Next Steps (Loop 2)

1. Implement `/classes` week-grid layout consuming grouped sessions endpoint.
2. Build responsive column/grid system with horizontal scroll on mobile.
3. Surface availability legend + badge styles per state.
4. Provide polished empty day states and loading skeletons.
5. Validate keyboard navigation, focus management, and screen-reader labels.

**Exit criteria for Loop 2:**
- ✅ Week-grid renders sessions with availability states
- ✅ Responsive behaviour across desktop/tablet/mobile
- ✅ Keyboard + screen reader support verified
- ✅ Empty/past days handled gracefully
- ✅ Feature documented in `/docs/LOOP2_IMPLEMENTATION.md`

---

**Status:** APPROVED ✅  
**Confidence:** HIGH – Calendar grid meets stakeholder requirements and provides clear UX win while maintaining WIGGUM standards
