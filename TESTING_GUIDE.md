# Herfa Marketplace - Testing Guide

## 🎯 Quick Test Guide

### Access Points
- **Django Admin**: http://localhost:8000/admin/
- **API Base**: http://localhost:8000/api/

### Test Credentials
- **Client**: `test_client` / `test123`
- **Artisan**: `test_artisan` / `test123`
- **Admin**: `admin` / `admin123`

---

## 📋 Testing Workflow

### Step 1: Login as Client

**Using PowerShell:**
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"test_client","password":"test123"}'

$token = $response.tokens.access
Write-Host "Access Token: $token"
```

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"test_client\",\"password\":\"test123\"}"
```

**Save the `access` token from the response!**

---

### Step 2: Deposit Funds to Client Wallet

**PowerShell:**
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/payments/deposit/" `
  -Method POST `
  -Headers $headers `
  -Body '{"amount":"500.00"}'
```

**curl:**
```bash
curl -X POST http://localhost:8000/api/payments/deposit/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"amount\":\"500.00\"}"
```

---

### Step 3: View Service Requests

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/requests/" `
  -Method GET `
  -Headers @{"Authorization" = "Bearer $token"}
```

**curl:**
```bash
curl -X GET http://localhost:8000/api/requests/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Step 4: Login as Artisan

**PowerShell:**
```powershell
$artisanResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"test_artisan","password":"test123"}'

$artisanToken = $artisanResponse.tokens.access
```

---

### Step 5: View Offers (as Artisan)

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/requests/" `
  -Method GET `
  -Headers @{"Authorization" = "Bearer $artisanToken"}
```

---

### Step 6: Accept Offer (as Client)

**PowerShell:**
```powershell
# Use the Offer ID from the test data: e4f66996-81a9-49de-8a40-392886895fda
Invoke-RestMethod -Uri "http://localhost:8000/api/offers/e4f66996-81a9-49de-8a40-392886895fda/accept/" `
  -Method POST `
  -Headers @{"Authorization" = "Bearer $token"}
```

**curl:**
```bash
curl -X POST http://localhost:8000/api/offers/e4f66996-81a9-49de-8a40-392886895fda/accept/ \
  -H "Authorization: Bearer YOUR_CLIENT_TOKEN"
```

---

### Step 7: Complete Service (as Client)

**PowerShell:**
```powershell
# Use the Service Request ID: a85df45c-a7e9-481a-bc9e-36f1c0b1b32a
Invoke-RestMethod -Uri "http://localhost:8000/api/requests/a85df45c-a7e9-481a-bc9e-36f1c0b1b32a/complete/" `
  -Method POST `
  -Headers @{"Authorization" = "Bearer $token"}
```

---

## 🌐 Using Browser/Postman

### 1. Admin Panel
- Go to: http://localhost:8000/admin/
- Login: `admin` / `admin123`
- Explore: Users, Service Requests, Offers, Wallets, Transactions

### 2. API Testing with Postman/Thunder Client

**Collection Setup:**
1. Base URL: `http://localhost:8000/api/`
2. Add Authorization header: `Bearer {token}`

**Endpoints to Test:**
- `POST /api/auth/login/` - Get token
- `GET /api/profiles/me/` - Get profile
- `GET /api/requests/` - List requests
- `POST /api/payments/deposit/` - Deposit funds
- `POST /api/offers/{id}/accept/` - Accept offer
- `POST /api/requests/{id}/complete/` - Complete service

---

## 🧪 Complete Test Script

Run this PowerShell script for a complete test:

```powershell
# 1. Login as Client
$clientLogin = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" `
  -Method POST -ContentType "application/json" `
  -Body '{"username":"test_client","password":"test123"}'
$clientToken = $clientLogin.tokens.access
Write-Host "Client logged in. Token: $($clientToken.Substring(0,20))..."

# 2. Deposit Funds
$deposit = Invoke-RestMethod -Uri "http://localhost:8000/api/payments/deposit/" `
  -Method POST -Headers @{"Authorization"="Bearer $clientToken"} `
  -ContentType "application/json" -Body '{"amount":"500.00"}'
Write-Host "Deposited 500 EGP. Balance: $($deposit.wallet.balance) EGP"

# 3. View Requests
$requests = Invoke-RestMethod -Uri "http://localhost:8000/api/requests/" `
  -Method GET -Headers @{"Authorization"="Bearer $clientToken"}
Write-Host "Found $($requests.count) service requests"

# 4. Accept Offer
$accept = Invoke-RestMethod -Uri "http://localhost:8000/api/offers/e4f66996-81a9-49de-8a40-392886895fda/accept/" `
  -Method POST -Headers @{"Authorization"="Bearer $clientToken"}
Write-Host "Offer accepted! Service status: $($accept.service_request.status)"

# 5. Complete Service
$complete = Invoke-RestMethod -Uri "http://localhost:8000/api/requests/a85df45c-a7e9-481a-bc9e-36f1c0b1b32a/complete/" `
  -Method POST -Headers @{"Authorization"="Bearer $clientToken"}
Write-Host "Service completed! Payment released to artisan"
```

---

## ✅ Expected Results

1. **Login**: Returns JWT tokens (access + refresh)
2. **Deposit**: Wallet balance increases
3. **View Requests**: Returns list of service requests
4. **Accept Offer**: 
   - Funds moved to escrow
   - Service status → `IN_PROGRESS`
   - Chat becomes available
5. **Complete Service**:
   - Payment released to artisan
   - Service status → `COMPLETED`
   - Artisan wallet balance increases

---

## 🐛 Troubleshooting

**401 Unauthorized**: Token expired or invalid - Login again
**403 Forbidden**: Wrong role (e.g., artisan trying to create request)
**400 Bad Request**: Check request body format
**404 Not Found**: Check endpoint URL and IDs

---

## 📊 Check Database

View data in Django admin:
- http://localhost:8000/admin/
- Login with: `admin` / `admin123`

