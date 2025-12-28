# Redis Setup Guide

## Current Status

Redis is **NOT running**. Celery worker cannot connect to Redis, which is required for:
- Async task processing (ID verification)
- Django Channels (WebSocket chat)

## Quick Solutions

### Option 1: Docker (Easiest - if Docker is installed)
```powershell
docker run -d -p 6379:6379 --name redis redis
```

### Option 2: Install Redis for Windows
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`
3. Or use the installer

### Option 3: Use WSL2 (Windows Subsystem for Linux)
```bash
wsl sudo apt-get update
wsl sudo apt-get install redis-server
wsl sudo service redis-server start
```

### Option 4: Redis Cloud (Free Tier)
1. Sign up at: https://redis.com/try-free/
2. Get your connection URL
3. Update `CELERY_BROKER_URL` in `config/settings.py`:
   ```python
   CELERY_BROKER_URL = 'redis://your-redis-cloud-url:6379/0'
   ```

### Option 5: Memurai (Redis-compatible for Windows)
- Download from: https://www.memurai.com/get-memurai
- Free for development

## Verify Redis is Running

Run the check script:
```powershell
.\backend\scripts\check_redis.ps1
```

Or manually test:
```powershell
Test-NetConnection -ComputerName localhost -Port 6379
```

## What Happens Without Redis?

- ✅ Django server will run fine
- ✅ REST API endpoints will work
- ❌ Celery tasks won't run (ID verification will fail)
- ❌ WebSocket chat won't work
- ❌ Async notifications won't work

## For Development (Temporary Workaround)

If you just want to test the REST API without Redis:

1. Comment out Celery task calls in `apps/users/views.py`:
   ```python
   # process_id_verification.delay(str(profile.id))
   # Run synchronously instead:
   from apps.marketplace.tasks import process_id_verification
   process_id_verification(str(profile.id))
   ```

2. Disable Channels in `config/asgi.py` (use WSGI only)

**Note:** This is only for basic API testing. Full functionality requires Redis.

