# Loop 1 — Frontend Layout Decision for The Mind Department

**Date:** 2026-02-04  
**Client:** The Mind Department  
**Decision Type:** UI/UX Pattern Selection  
**Status:** APPROVED ✅

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

**Decision:** Implement Option A (Upcoming Sessions List) as default layout

**Decided by:** Development team  
**Date:** 2026-02-04  
**Approved by:** Product owner  

**Alternatives considered:** Calendar grid, slot picker  
**Reason for rejection:** Higher complexity, less mobile-friendly, doesn't match calm UX requirements

**Review date:** After 3 months of usage (May 2026)  
**Success metrics:**
- Mobile booking completion rate > 70%
- Average time to book < 2 minutes
- User feedback score > 4/5 for "ease of use"

---

## Next Steps (Loop 2)

1. Implement session list page with temporal grouping
2. Build session card component with capacity states
3. Add empty state handling
4. Test on mobile devices
5. Validate accessibility

**Exit criteria for Loop 2:**
- ✅ /classes page renders session list
- ✅ Capacity states display correctly
- ✅ Mobile responsive
- ✅ Keyboard navigable
- ✅ Empty state shows gracefully

---

**Status:** APPROVED ✅  
**Confidence:** HIGH - Decision is well-supported by data and aligns with client needs
