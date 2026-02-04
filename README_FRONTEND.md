# NBNE Booking - Frontend Documentation

## 🚀 Production Deployment

**Live URLs:**
- **Public Booking Form**: https://booking.nbnesigns.co.uk/
- **Admin Dashboard**: https://booking.nbnesigns.co.uk/admin.html

**Status**: ✅ **LIVE AND OPERATIONAL**

## Overview

Standalone HTML frontend for the NBNE Booking Platform. Built with vanilla JavaScript and Tailwind CSS for simplicity and ease of deployment.

## Features

### Public Booking Form (`/index.html`)
- Service selection from 4 available services
- Date and time picker
- Customer information form (name, email, phone)
- Notes field for special requests
- Real-time form validation
- Automatic email notifications
- Responsive design with Tailwind CSS

### Admin Dashboard (`/admin.html`)
- Secure JWT authentication
- View all bookings in sortable table
- Filter bookings by:
  - Date range (from/to)
  - Status (confirmed, cancelled, completed, no_show)
- Export bookings to CSV
- Logout functionality
- Responsive design

### Technical Features
- Vanilla JavaScript (no framework dependencies)
- Tailwind CSS via CDN
- HTTPS API calls
- JWT token storage in localStorage
- Error handling and user feedback
- Mobile-responsive design

## Production Configuration

### Frontend Files
- **Location on Server**: `/srv/booking/frontend/`
- **Public Form**: `/srv/booking/frontend/index.html`
- **Admin Dashboard**: `/srv/booking/frontend/admin.html`

### API Configuration
Both frontend files connect to:
```javascript
const API_URL = 'https://booking.nbnesigns.co.uk/api/v1';
```

### Endpoints Used

**Public Booking Form:**
- `GET /services/public` - Fetch available services
- `POST /bookings/public` - Submit booking (no auth required)

**Admin Dashboard:**
- `POST /auth/login` - Login with email/password
- `GET /bookings/` - Fetch all bookings (auth required)
- `GET /bookings/export` - Download CSV (auth required)

### Admin Credentials
- **Email**: admin@nbnesigns.co.uk
- **Password**: Admin123!
- **Role**: superadmin

## File Structure

```
frontend/
├── index.html           # Public booking form
│   ├── Service selection dropdown
│   ├── Date picker
│   ├── Time picker
│   ├── Customer form (name, email, phone)
│   ├── Notes textarea
│   └── Submit button
│
└── admin.html          # Admin dashboard
    ├── Login form
    ├── Booking list table
    ├── Date range filters
    ├── Status filter dropdown
    └── CSV export button
```

### Key JavaScript Functions

**index.html:**
- `loadServices()` - Fetches services from API
- `displayServices()` - Renders service cards
- `selectService()` - Handles service selection
- `submitBooking()` - Submits booking to API

**admin.html:**
- `login()` - Authenticates user and stores JWT
- `loadBookings()` - Fetches all bookings
- `displayBookings()` - Renders booking table
- `filterBookings()` - Filters by date/status
- `exportCSV()` - Downloads CSV file

## Deployment

### Uploading Frontend Files

**From Windows PowerShell:**
```powershell
# Upload public booking form
scp "g:\My Drive\003 APPS\024 BOOKING\frontend\index.html" toby@87.106.65.142:/srv/booking/frontend/index.html

# Upload admin dashboard
scp "g:\My Drive\003 APPS\024 BOOKING\frontend\admin.html" toby@87.106.65.142:/srv/booking/frontend/admin.html
```

**On Server:**
```bash
# Verify files uploaded
ls -lh /srv/booking/frontend/

# Files are served by Caddy automatically
# No restart needed for static files
```

### Caddy Configuration

Frontend files are served by Caddy from `/srv/booking/frontend/`:

```caddyfile
booking.nbnesigns.co.uk {
    # Serve frontend files
    root * /srv/booking/frontend
    file_server
    
    # Proxy API requests
    reverse_proxy /api/* api:8000
}
```

## API Integration

### Public Booking Flow

1. **Load Services**
   ```javascript
   GET /api/v1/services/public
   // Returns: Array of service objects
   ```

2. **Submit Booking**
   ```javascript
   POST /api/v1/bookings/public
   Content-Type: application/json
   
   {
     "service_id": 1,
     "start_time": "2026-02-04T10:00:00Z",
     "end_time": "2026-02-04T12:00:00Z",
     "customer_name": "John Doe",
     "customer_email": "john@example.com",
     "customer_phone": "1234567890",
     "notes": "Optional notes"
   }
   ```

### Admin Dashboard Flow

1. **Login**
   ```javascript
   POST /api/v1/auth/login
   Content-Type: application/json
   
   {
     "email": "admin@nbnesigns.co.uk",
     "password": "Admin123!"
   }
   // Returns: { "access_token": "...", "token_type": "bearer" }
   ```

2. **Fetch Bookings**
   ```javascript
   GET /api/v1/bookings/
   Authorization: Bearer {token}
   // Returns: Array of booking objects
   ```

3. **Export CSV**
   ```javascript
   GET /api/v1/bookings/export
   Authorization: Bearer {token}
   // Returns: CSV file download
   ```

## Testing

### Test Public Booking Form

1. Visit https://booking.nbnesigns.co.uk/
2. Select a service
3. Choose date and time
4. Fill in customer details
5. Click "Request Booking"
6. Check sales@nbnesigns.co.uk for email notification

### Test Admin Dashboard

1. Visit https://booking.nbnesigns.co.uk/admin.html
2. Login with admin@nbnesigns.co.uk / Admin123!
3. View booking list
4. Test filters (date range, status)
5. Click "Export to CSV" to download bookings

### Local Development

```bash
# Serve locally with Python
cd frontend
python -m http.server 8080

# Update API_URL in both files to:
const API_URL = 'http://localhost:8000/api/v1';
```

## Troubleshooting

### Services Not Loading
- Check browser console for errors
- Verify API_URL is correct in index.html
- Test API endpoint: `curl https://booking.nbnesigns.co.uk/api/v1/services/public`
- Hard refresh browser (Ctrl+Shift+R)

### Login Not Working
- Verify credentials: admin@nbnesigns.co.uk / Admin123!
- Check browser console for 422 or 429 errors
- If rate limited, restart API: `docker compose restart api`
- Hard refresh browser (Ctrl+Shift+R)

### Bookings Not Appearing
- Verify JWT token is stored in localStorage
- Check Authorization header is sent with requests
- Verify user has superadmin role
- Check API logs: `docker compose logs api --tail 50`

### CSV Export Not Working
- Verify user is logged in
- Check browser console for errors
- Verify /bookings/export endpoint exists
- Test with curl: `curl -H "Authorization: Bearer {token}" https://booking.nbnesigns.co.uk/api/v1/bookings/export`

## Customization

### Update Services

Services are managed in the database:
```bash
# Connect to database
docker compose exec db psql -U nbne_admin -d nbne_main

# View services
SELECT id, name, description, duration_minutes, price FROM services;

# Update service
UPDATE services SET name='New Name', price=300.00 WHERE id=1;
```

### Update Branding

Edit the HTML files directly:
- **Title**: Change `<title>` tag in both files
- **Header**: Update "NBNE Signs" text
- **Colors**: Modify Tailwind CSS classes
- **Logo**: Add `<img>` tag in header

### Add New Fields

1. Add input field to index.html form
2. Update `submitBooking()` function to include new field
3. Update backend BookingCreate schema
4. Update database model if needed
5. Run migration

## Browser Support

- Chrome/Edge: Latest 2 versions ✅
- Firefox: Latest 2 versions ✅
- Safari: Latest 2 versions ✅
- Mobile Safari: iOS 12+ ✅
- Chrome Mobile: Latest ✅

## Future Enhancements

- [ ] Calendar view for available slots
- [ ] Real-time availability checking
- [ ] Customer booking history
- [ ] Email confirmation to customers
- [ ] SMS notifications
- [ ] Payment integration
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Booking cancellation/rescheduling
- [ ] Admin booking creation

## Related Documentation

- [README.md](README.md) - Main project documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment guide
- [API Documentation](https://booking.nbnesigns.co.uk/api/v1/docs) - Interactive API docs
