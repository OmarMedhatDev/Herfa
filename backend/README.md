# Herfa Marketplace - Backend API

A two-sided marketplace connecting Clients with Artisans in Egypt, built with Django REST Framework.

## Features

- **User Authentication**: JWT-based authentication with role-based access (Client, Artisan, Admin)
- **Identity Verification**: AI-powered National ID verification for Artisans
- **Smart Pricing**: AI suggests price ranges based on service category and description
- **Escrow Payments**: Secure payment system with funds held in escrow until service completion
- **Real-time Chat**: WebSocket-based chat between Clients and Artisans
- **Chat Safety**: AI monitors chat messages for off-platform payment attempts

## Tech Stack

- Django 6.0
- Django REST Framework
- PostgreSQL (SQLite for development)
- Celery + Redis (async tasks)
- Django Channels (WebSockets)
- OpenCV (image processing)
- JWT Authentication

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Database Setup

For development (SQLite - default):
```bash
python manage.py migrate
```

For production (PostgreSQL):
- Update `DATABASES` in `config/settings.py`
- Run migrations: `python manage.py migrate`

### 3. Create Superuser

```bash
python manage.py createsuperuser
```

### 4. Run Redis (for Celery and Channels)

```bash
# Windows (using WSL or Docker)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis
```

### 5. Run Celery Worker

```bash
celery -A config worker -l info
```

### 6. Run Development Server

```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/profiles/me/` - Get current user profile
- `PUT /api/profiles/me/` - Update profile
- `POST /api/profiles/upload-id/` - Upload National ID (Artisans only)

### Marketplace
- `GET /api/requests/` - List service requests
- `POST /api/requests/` - Create service request (Clients only)
- `GET /api/requests/{id}/` - Get service request details
- `POST /api/requests/{id}/bid/` - Submit offer (Verified Artisans only)
- `POST /api/offers/{id}/accept/` - Accept offer (Clients only)
- `POST /api/requests/{id}/complete/` - Complete service (Clients only)

### Payments
- `GET /api/payments/wallet/` - Get wallet balance
- `GET /api/payments/transactions/` - List transactions
- `POST /api/payments/deposit/` - Deposit funds

### Chat
- `GET /api/chat/requests/{id}/messages/` - Get chat messages
- `POST /api/chat/requests/{id}/send/` - Send message
- `WS /ws/chat/{id}/` - WebSocket connection for real-time chat

## User Roles & Permissions

### Client
- Can create service requests immediately after signup
- Can accept offers and deposit funds
- Can chat with Artisans after accepting an offer
- Can confirm service completion

### Artisan (Unverified)
- Can view service requests
- Cannot submit offers
- Must upload National ID for verification

### Artisan (Verified)
- Can submit offers on service requests
- Can chat with Clients after offer is accepted
- Receives payment after service completion

### Admin
- Approves/rejects National ID verification
- Manages disputes
- Full access to admin panel

## Workflow

1. **Registration**: User signs up as Client or Artisan
2. **Verification** (Artisans): Upload National ID → AI quality check → Admin approval
3. **Service Request**: Client posts request → AI suggests price
4. **Bidding**: Verified Artisans submit offers
5. **Acceptance**: Client accepts offer → Funds moved to escrow
6. **Service**: Artisan completes work → Chat available
7. **Completion**: Client confirms → Payment released to Artisan

## Environment Variables

Create a `.env` file (optional for development):

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=herfa
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Testing

```bash
python manage.py test
```

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure PostgreSQL database
3. Set up proper SECRET_KEY
4. Configure ALLOWED_HOSTS
5. Set up static file serving
6. Configure Redis and Celery workers
7. Set up WebSocket server (Daphne or similar)

## License

See LICENSE file in project root.

