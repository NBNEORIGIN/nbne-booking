# Vercel Deployment Guide - Frontend Only

**Date:** 2026-02-04  
**Project:** NBNE Booking App - The Mind Department Frontend

---

## Deployment Strategy

### ✅ What Gets Deployed to Vercel

**Frontend static files only:**
- `frontend/classes.html` - Group classes listing
- `frontend/booking.html` - Booking form
- `frontend/index.html` - Original appointment booking
- `frontend/admin.html` - Admin dashboard

### ❌ What Stays on VPS

**Backend API (booking.nbnesigns.co.uk):**
- FastAPI application
- PostgreSQL database
- Alembic migrations
- Email sending (SMTP)
- All API endpoints

**Why?**
- FastAPI requires persistent connections and lifecycle management
- Database connections not serverless-friendly
- Complex middleware and tenant resolution
- SMTP email sending may timeout in serverless functions

---

## Prerequisites

1. **Vercel Account**
   - Sign up at https://vercel.com
   - Install Vercel CLI: `npm install -g vercel`

2. **Backend CORS Configuration**
   - Must allow Vercel domain in CORS origins
   - Update `api/core/config.py` or environment variables

3. **Git Repository**
   - Project must be in Git repository
   - Push to GitHub/GitLab/Bitbucket

---

## Step 1: Configure CORS on Backend

Update backend to allow Vercel domain:

```python
# api/core/config.py or .env

# Add Vercel domain to CORS origins
CORS_ORIGINS = [
    "https://nbne-booking.vercel.app",  # Your Vercel domain
    "https://booking.nbnesigns.co.uk",  # Existing domain
    "http://localhost:3000",            # Local development
]
```

**Or via environment variable:**
```bash
CORS_ORIGINS='["https://nbne-booking.vercel.app","https://booking.nbnesigns.co.uk"]'
```

Restart backend after updating:
```bash
docker-compose restart api
```

---

## Step 2: Deploy to Vercel

### Option A: Via Vercel CLI

```bash
# Login to Vercel
vercel login

# Deploy from project root
cd "g:/My Drive/003 APPS/024 BOOKING"
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? nbne-booking-frontend
# - Directory? ./
# - Override settings? No
```

### Option B: Via Vercel Dashboard

1. Go to https://vercel.com/new
2. Import Git repository
3. Configure project:
   - **Framework Preset:** Other
   - **Root Directory:** `./`
   - **Build Command:** (leave empty)
   - **Output Directory:** `frontend`
4. Click "Deploy"

---

## Step 3: Configure Custom Domain (Optional)

### Option 1: Subdomain on nbnesigns.co.uk

**DNS Configuration:**
```
Type: CNAME
Name: booking-app
Value: cname.vercel-dns.com
```

**In Vercel Dashboard:**
1. Go to Project Settings → Domains
2. Add domain: `booking-app.nbnesigns.co.uk`
3. Follow verification steps

### Option 2: Custom Domain for The Mind Department

**DNS Configuration:**
```
Type: CNAME
Name: book (or @)
Value: cname.vercel-dns.com
```

**Example:** `book.theminddepartment.com`

---

## Step 4: Environment Variables (If Needed)

If you want to make API URL configurable:

**In Vercel Dashboard:**
1. Go to Project Settings → Environment Variables
2. Add:
   - Key: `VITE_API_URL`
   - Value: `https://booking.nbnesigns.co.uk/api/v1`

**Update frontend files to use:**
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'https://booking.nbnesigns.co.uk/api/v1';
```

**Note:** Current implementation has hardcoded API URL, which is fine for single-tenant deployment.

---

## Step 5: Test Deployment

### Verify Frontend

1. Visit Vercel URL: `https://your-project.vercel.app/classes.html`
2. Check browser console for errors
3. Verify API calls work (check Network tab)

### Test User Journey

1. **Classes Page:**
   - Sessions load correctly
   - Branding applies
   - Modal opens
   - "Book Now" redirects

2. **Booking Page:**
   - Session details display
   - Form submits successfully
   - Success message shows

3. **CORS Check:**
   - No CORS errors in console
   - API responses received

---

## Vercel Configuration File

**File:** `vercel.json`

```json
{
  "version": 2,
  "name": "nbne-booking-frontend",
  "builds": [
    {
      "src": "frontend/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/",
      "destination": "/frontend/classes.html"
    }
  ]
}
```

**What this does:**
- Serves files from `frontend/` directory
- Adds security headers
- Sets root path to `classes.html`

---

## URL Structure

### After Deployment

**Vercel URLs:**
- Root: `https://your-project.vercel.app/` → classes.html
- Classes: `https://your-project.vercel.app/classes.html`
- Booking: `https://your-project.vercel.app/booking.html`
- Admin: `https://your-project.vercel.app/admin.html`
- Original: `https://your-project.vercel.app/index.html`

**API URLs (still on VPS):**
- `https://booking.nbnesigns.co.uk/api/v1/sessions/public`
- `https://booking.nbnesigns.co.uk/api/v1/branding/public`
- `https://booking.nbnesigns.co.uk/api/v1/bookings/public`

---

## Advantages of Vercel Deployment

### ✅ Benefits

1. **Global CDN** - Fast loading worldwide
2. **Automatic HTTPS** - SSL certificates included
3. **Zero downtime deploys** - Instant rollbacks
4. **Git integration** - Auto-deploy on push
5. **Preview deployments** - Test before production
6. **Free tier** - Generous limits for small projects
7. **Custom domains** - Easy DNS configuration

### ⚠️ Considerations

1. **Split architecture** - Frontend and backend on different domains
2. **CORS required** - Must configure backend
3. **API dependency** - Frontend useless without backend
4. **No backend features** - Can't deploy FastAPI to Vercel easily

---

## Alternative: Keep Everything on VPS

If you prefer single-domain deployment:

**Pros:**
- No CORS configuration needed
- Single deployment process
- Backend and frontend together
- Simpler architecture

**Cons:**
- No global CDN
- Manual SSL management
- No automatic Git deploys
- Single point of failure

**Current VPS setup works well** - Vercel is optional enhancement for frontend performance.

---

## Troubleshooting

### CORS Errors

**Symptom:** Console shows "CORS policy" errors

**Fix:**
```python
# In api/main.py or api/core/config.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",
        "https://booking.nbnesigns.co.uk"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 404 Errors

**Symptom:** Pages not found on Vercel

**Fix:** Check `vercel.json` routes configuration

### API Calls Failing

**Symptom:** Network errors in console

**Fix:** Verify API URL is correct and backend is running

---

## Cost Estimate

### Vercel Pricing

**Hobby (Free):**
- ✅ 100GB bandwidth/month
- ✅ Unlimited requests
- ✅ Custom domains
- ✅ Automatic HTTPS
- **Cost:** $0/month

**Pro ($20/month):**
- 1TB bandwidth
- Advanced analytics
- Team collaboration
- **Cost:** $20/month

**For this project:** Free tier is sufficient

### VPS (Current)

**Backend hosting:** ~$10-20/month (existing)

**Total with Vercel:** $0-20/month (same as current)

---

## Recommendation

### For The Mind Department

**Option 1: Vercel Frontend + VPS Backend** ⭐ RECOMMENDED
- Fast global delivery
- Easy updates via Git
- Free hosting for frontend
- Backend stays on VPS

**Option 2: Keep Everything on VPS**
- Simpler architecture
- No CORS complexity
- Single deployment
- Current setup works fine

**My recommendation:** Try Vercel for frontend performance benefits, but VPS-only is perfectly fine too.

---

## Deployment Checklist

- [ ] Create Vercel account
- [ ] Install Vercel CLI (optional)
- [ ] Update backend CORS configuration
- [ ] Deploy to Vercel (CLI or dashboard)
- [ ] Test classes page loads
- [ ] Test booking flow works
- [ ] Configure custom domain (optional)
- [ ] Update DNS records (if custom domain)
- [ ] Test from mobile device
- [ ] Monitor for errors

---

## Support

**Vercel Documentation:** https://vercel.com/docs  
**Vercel CLI Reference:** https://vercel.com/docs/cli  
**CORS Guide:** https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

**Status:** Ready for deployment  
**Complexity:** Low (frontend-only deployment)  
**Time Required:** 15-30 minutes  
**Cost:** Free (Hobby tier)
