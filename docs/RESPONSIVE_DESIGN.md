# Responsive Design - NBNE Booking Frontend

## Breakpoints (Tailwind CSS)

- **Mobile**: < 640px (default)
- **Tablet**: ≥ 640px (`sm:`)
- **Desktop**: ≥ 768px (`md:`)
- **Large Desktop**: ≥ 1024px (`lg:`)
- **Extra Large**: ≥ 1280px (`xl:`)

## Mobile-First Approach

All styles are written mobile-first, with larger breakpoints adding enhancements.

### Example:
```html
<!-- Full width on mobile, half width on tablet, third on desktop -->
<div class="w-full sm:w-1/2 md:w-1/3">
```

## Component Responsiveness

### Header
- **Mobile**: Stacked layout, contact info hidden
- **Tablet**: Contact info visible
- **Desktop**: Full horizontal layout

### Service Cards
- **Mobile**: 1 column
- **Tablet**: 2 columns
- **Desktop**: 2 columns (max-width container)

### Time Slots
- **Mobile**: 2 columns
- **Tablet**: 4 columns
- **Desktop**: 4 columns

### Progress Indicator
- **Mobile**: Compact with smaller text
- **Tablet**: Full size with labels
- **Desktop**: Full size with labels

### Forms
- **Mobile**: Full width inputs, stacked buttons
- **Tablet**: Full width inputs, inline buttons
- **Desktop**: Optimized width with inline buttons

### Admin Branding Page
- **Mobile**: Stacked (form then preview)
- **Tablet**: Stacked (form then preview)
- **Desktop**: Side-by-side (form left, preview right sticky)

## Touch Targets

All interactive elements meet minimum 44x44px touch target size:
- Buttons: `px-6 py-3` (minimum)
- Time slots: `px-4 py-3`
- Form inputs: `px-4 py-2`
- Links: Adequate padding

## Typography Scaling

- **Headings**: Scale down on mobile
  - h1: `text-2xl md:text-3xl`
  - h2: `text-xl md:text-2xl`
  - h3: `text-lg md:text-xl`
- **Body**: `text-base` (16px) on all devices
- **Small text**: `text-sm` (14px)
- **Extra small**: `text-xs` (12px)

## Spacing

- **Container**: `px-4` (mobile) → `px-6` (tablet) → `px-8` (desktop)
- **Section gaps**: `space-y-4` (mobile) → `space-y-6` (tablet)
- **Grid gaps**: `gap-4` (mobile) → `gap-6` (desktop)

## Images

- Logo: Max height constrained, responsive width
- Service images: Full width on mobile, constrained on desktop
- All images use `object-fit` for proper scaling

## Navigation

- **Mobile**: Hamburger menu (if needed in future)
- **Desktop**: Full horizontal menu

## Tables (Admin)

- **Mobile**: Card view or horizontal scroll
- **Tablet**: Horizontal scroll with sticky headers
- **Desktop**: Full table layout

## Testing Devices

### Priority Devices:
1. iPhone 12/13/14 (390x844)
2. Samsung Galaxy S21 (360x800)
3. iPad (768x1024)
4. Desktop 1920x1080

### Browser Testing:
- Chrome (mobile & desktop)
- Safari (iOS & macOS)
- Firefox (desktop)
- Edge (desktop)

## Performance

- Tailwind CSS loaded via CDN (no build step)
- Minimal JavaScript
- No large images (logo only)
- Fast page loads on 3G

## Print Styles

Currently using browser defaults. Future enhancement: custom print stylesheet.
