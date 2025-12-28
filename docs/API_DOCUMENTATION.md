# Herfa Marketplace API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication

All endpoints (except registration and login) require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "password2": "securepassword123",
  "phone_number": "+201234567890",
  "role": "CLIENT"  // or "ARTISAN"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "CLIENT"
  },
  "tokens": {
    "refresh": "refresh_token",
    "access": "access_token"
  }
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "john_doe",  // or email
  "password": "securepassword123"
}
```

**Response:** Same as registration

---

### Profiles

#### Get My Profile
```http
GET /api/profiles/me/
Authorization: Bearer <token>
```

**Response (Client):**
```json
{
  "id": "uuid",
  "user": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "CLIENT"
  },
  "display_name": "John Doe",
  "address": "123 Main St, Cairo"
}
```

**Response (Artisan):**
```json
{
  "id": "uuid",
  "user": {...},
  "display_name": "Ahmed Ali",
  "bio": "Experienced plumber",
  "verification_status": "VERIFIED",
  "rating_avg": 4.5,
  "is_verified": true
}
```

#### Update Profile
```http
PUT /api/profiles/me/
Authorization: Bearer <token>
Content-Type: application/json

{
  "display_name": "John Doe",
  "address": "New Address"  // for clients
  // or
  "display_name": "Ahmed Ali",
  "bio": "Updated bio"  // for artisans
}
```

#### Upload National ID (Artisans Only)
```http
POST /api/profiles/upload-id/
Authorization: Bearer <token>
Content-Type: multipart/form-data

national_id_photo: <file>
```

**Response:**
```json
{
  "message": "National ID uploaded successfully. Verification in progress.",
  "profile": {...}
}
```

---

### Marketplace

#### List Service Requests
```http
GET /api/requests/?status=OPEN&category=Plumbing
Authorization: Bearer <token>
```

**Query Parameters:**
- `status`: Filter by status (OPEN, IN_PROGRESS, COMPLETED, CANCELLED)
- `category`: Filter by category

**Response:**
```json
[
  {
    "id": "uuid",
    "client": {...},
    "category": "Plumbing",
    "description": "Fix leaking pipe",
    "budget_min": "100.00",
    "budget_max": "300.00",
    "ai_suggested_price": "150-200 EGP",
    "status": "OPEN",
    "offers_count": 3,
    "created_at": "2025-01-01T10:00:00Z"
  }
]
```

#### Create Service Request (Clients Only)
```http
POST /api/requests/
Authorization: Bearer <token>
Content-Type: application/json

{
  "category": "Plumbing",
  "description": "Fix leaking pipe in kitchen",
  "media_url": "https://example.com/image.jpg",
  "budget_min": "100.00",
  "budget_max": "300.00"
}
```

#### Get Service Request Details
```http
GET /api/requests/{id}/
Authorization: Bearer <token>
```

#### Submit Offer (Verified Artisans Only)
```http
POST /api/requests/{request_id}/bid/
Authorization: Bearer <token>
Content-Type: application/json

{
  "price": "150.00",
  "message": "I can fix this today"
}
```

#### Accept Offer (Clients Only)
```http
POST /api/offers/{offer_id}/accept/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Offer accepted. Funds moved to escrow.",
  "offer": {...},
  "service_request": {...}
}
```

#### Complete Service (Clients Only)
```http
POST /api/requests/{request_id}/complete/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Service completed. Payment released to artisan.",
  "service_request": {...}
}
```

---

### Payments

#### Get Wallet
```http
GET /api/payments/wallet/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "user": {...},
  "balance": "500.00",
  "created_at": "2025-01-01T10:00:00Z"
}
```

#### Deposit Funds
```http
POST /api/payments/deposit/
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": "100.00"
}
```

#### List Transactions
```http
GET /api/payments/transactions/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "amount": "100.00",
    "transaction_type": "DEPOSIT",
    "description": "Wallet deposit",
    "created_at": "2025-01-01T10:00:00Z"
  }
]
```

---

### Chat

#### Get Chat Messages
```http
GET /api/chat/requests/{request_id}/messages/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "sender": {...},
    "content": "Hello, when can you start?",
    "is_flagged": false,
    "sent_at": "2025-01-01T10:00:00Z"
  }
]
```

#### Send Message
```http
POST /api/chat/requests/{request_id}/send/
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "I can start tomorrow morning"
}
```

**Response:**
```json
{
  "id": "uuid",
  "content": "I can start tomorrow morning",
  "is_flagged": false,
  "sent_at": "2025-01-01T10:00:00Z"
}
```

If message is flagged:
```json
{
  "id": "uuid",
  "content": "...",
  "is_flagged": true,
  "flag_reason": "Message contains patterns suggesting off-platform payment...",
  "warning": "Warning message"
}
```

#### WebSocket Connection (Real-time Chat)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/{request_id}/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message:', data);
};

ws.send(JSON.stringify({
  message: 'Hello!'
}));
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Error message",
  "field_name": ["Field-specific error"]
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
  "error": "You don't have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

---

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Notes

1. All monetary values are in EGP (Egyptian Pounds)
2. All timestamps are in UTC
3. JWT tokens expire after 24 hours (access) and 7 days (refresh)
4. Chat is only available for service requests with status `IN_PROGRESS`
5. Artisans must be verified before submitting offers
6. Clients must have sufficient wallet balance before accepting offers

