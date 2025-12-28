# Herfa Marketplace - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Prerequisites
- Python 3.10+
- Redis (for Celery and Channels)
- PostgreSQL (optional, SQLite works for development)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Run Migrations
```bash
python manage.py migrate
```

### Step 3: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 4: Start Redis

**Option 1: Using Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name redis redis
```

**Option 2: Install Redis for Windows**
- Download from: https://github.com/microsoftarchive/redis/releases
- Or use WSL2: `wsl sudo apt-get install redis-server && wsl sudo service redis-server start`

**Option 3: Use Redis Cloud (Free tier)**
- Sign up at: https://redis.com/try-free/
- Update `CELERY_BROKER_URL` in `backend/config/settings.py`

**Option 4: Use Memurai (Redis-compatible for Windows)**
- Download from: https://www.memurai.com/get-memurai

**Check Redis Status:**
```powershell
# Run the check script
.\backend\scripts\check_redis.ps1
```

### Step 5: Start Celery Worker (in a new terminal)
```bash
cd backend
celery -A config worker -l info
```

### Step 6: Start Django Server
```bash
cd backend
python manage.py runserver
```

## 📋 Testing the API

### 1. Register a Client
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "client1",
    "email": "client1@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "role": "CLIENT"
  }'
```

### 2. Register an Artisan
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "artisan1",
    "email": "artisan1@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "role": "ARTISAN"
  }'
```

### 3. Login as Client
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "client1",
    "password": "testpass123"
  }'
```

Save the `access` token from the response.

### 4. Create a Service Request
```bash
curl -X POST http://localhost:8000/api/requests/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Plumbing",
    "description": "Fix leaking pipe in kitchen",
    "budget_min": "100.00",
    "budget_max": "300.00"
  }'
```

### 5. Deposit Funds (as Client)
```bash
curl -X POST http://localhost:8000/api/payments/deposit/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "500.00"
  }'
```

### 6. Upload National ID (as Artisan)
```bash
curl -X POST http://localhost:8000/api/profiles/upload-id/ \
  -H "Authorization: Bearer ARTISAN_ACCESS_TOKEN" \
  -F "national_id_photo=@/path/to/id_photo.jpg"
```

### 7. Verify Artisan (as Admin)
- Go to http://localhost:8000/admin/
- Login with superuser credentials
- Navigate to Artisan Profiles
- Approve the artisan's verification

### 8. Submit Offer (as Verified Artisan)
```bash
curl -X POST http://localhost:8000/api/requests/REQUEST_ID/bid/ \
  -H "Authorization: Bearer ARTISAN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price": "150.00",
    "message": "I can fix this today"
  }'
```

### 9. Accept Offer (as Client)
```bash
curl -X POST http://localhost:8000/api/offers/OFFER_ID/accept/ \
  -H "Authorization: Bearer CLIENT_ACCESS_TOKEN"
```

### 10. Complete Service (as Client)
```bash
curl -X POST http://localhost:8000/api/requests/REQUEST_ID/complete/ \
  -H "Authorization: Bearer CLIENT_ACCESS_TOKEN"
```

## 🎯 Key Features Implemented

✅ **User Authentication** - JWT-based auth with role-based access  
✅ **Identity Verification** - AI-powered ID verification for artisans  
✅ **Smart Pricing** - AI suggests price ranges  
✅ **Escrow Payments** - Secure payment system  
✅ **Real-time Chat** - WebSocket-based messaging  
✅ **Chat Safety** - AI monitors for off-platform payment attempts  
✅ **Admin Panel** - Full admin interface for managing the platform  

## 📚 Documentation

- [System Design](docs/system_design.txt)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Backend README](backend/README.md)

## 🔧 Troubleshooting

### Redis Connection Error
- Make sure Redis is running: `redis-cli ping` should return `PONG`
- Check Redis URL in settings

### Celery Not Working
- Ensure Redis is running
- Check Celery worker logs for errors
- Verify `CELERY_BROKER_URL` in settings

### Database Errors
- Run migrations: `python manage.py migrate`
- Check database connection settings

### Import Errors
- Activate virtual environment
- Install all requirements: `pip install -r requirements.txt`

## 🎉 Next Steps

1. Set up frontend client (React/Flutter/etc.)
2. Configure production database (PostgreSQL)
3. Set up file storage (AWS S3, etc.)
4. Configure production Redis
5. Set up monitoring and logging
6. Deploy to production server

## 📞 Support

For issues or questions, refer to the system design document or API documentation.

