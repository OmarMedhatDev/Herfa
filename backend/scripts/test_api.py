#!/usr/bin/env python
"""
Quick API test script for Herfa Marketplace
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, ArtisanProfile, ClientProfile
from apps.marketplace.models import ServiceRequest, Offer
from apps.payments.models import Wallet
from apps.marketplace.ai_services import PriceEstimationService

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_application():
    print_section("HERFA MARKETPLACE - API TEST")
    
    # 1. Check existing users
    print_section("1. Checking Users")
    admin = User.objects.filter(username='admin').first()
    if admin:
        print(f"[OK] Admin user exists: {admin.username} ({admin.role})")
    else:
        print("[ERROR] Admin user not found")
    
    clients = User.objects.filter(role='CLIENT')
    artisans = User.objects.filter(role='ARTISAN')
    print(f"[OK] Clients: {clients.count()}")
    print(f"[OK] Artisans: {artisans.count()}")
    
    # 2. Create test client if doesn't exist
    print_section("2. Creating Test Client")
    client, created = User.objects.get_or_create(
        username='test_client',
        defaults={
            'email': 'client@test.com',
            'role': 'CLIENT'
        }
    )
    if created:
        client.set_password('test123')
        client.save()
        ClientProfile.objects.create(user=client, display_name='Test Client')
        Wallet.objects.get_or_create(user=client, defaults={'balance': 0.00})
        print(f"[OK] Created test client: {client.username}")
    else:
        print(f"[OK] Test client already exists: {client.username}")
    
    # 3. Create test artisan if doesn't exist
    print_section("3. Creating Test Artisan")
    artisan, created = User.objects.get_or_create(
        username='test_artisan',
        defaults={
            'email': 'artisan@test.com',
            'role': 'ARTISAN'
        }
    )
    if created:
        artisan.set_password('test123')
        artisan.save()
        profile = ArtisanProfile.objects.create(
            user=artisan,
            display_name='Test Artisan',
            verification_status='VERIFIED'  # Auto-verify for testing
        )
        Wallet.objects.get_or_create(user=artisan, defaults={'balance': 0.00})
        print(f"[OK] Created test artisan: {artisan.username} (VERIFIED)")
    else:
        # Ensure artisan is verified
        profile, _ = ArtisanProfile.objects.get_or_create(user=artisan)
        profile.verification_status = 'VERIFIED'
        profile.save()
        print(f"[OK] Test artisan exists: {artisan.username} (VERIFIED)")
    
    # 4. Create a test service request
    print_section("4. Creating Service Request")
    service_request, created = ServiceRequest.objects.get_or_create(
        client=client,
        category='Plumbing',
        defaults={
            'description': 'Fix leaking pipe in kitchen sink',
            'budget_min': 100.00,
            'budget_max': 300.00,
            'status': 'OPEN'
        }
    )
    
    if created:
        # Get AI price suggestion
        ai_price = PriceEstimationService.estimate_price(
            service_request.category,
            service_request.description
        )
        service_request.ai_suggested_price = ai_price
        service_request.save()
        print(f"[OK] Created service request: {service_request.id}")
        print(f"  Category: {service_request.category}")
        print(f"  Description: {service_request.description}")
        print(f"  AI Suggested Price: {service_request.ai_suggested_price}")
        print(f"  Budget: {service_request.budget_min} - {service_request.budget_max} EGP")
    else:
        print(f"[OK] Service request already exists: {service_request.id}")
    
    # 5. Create an offer
    print_section("5. Creating Offer")
    offer, created = Offer.objects.get_or_create(
        request=service_request,
        artisan=artisan,
        defaults={
            'price': 150.00,
            'message': 'I can fix this today!',
            'status': 'PENDING'
        }
    )
    if created:
        print(f"[OK] Created offer: {offer.id}")
        print(f"  Artisan: {artisan.username}")
        print(f"  Price: {offer.price} EGP")
        print(f"  Message: {offer.message}")
    else:
        print(f"[OK] Offer already exists: {offer.id}")
    
    # 6. Check wallets
    print_section("6. Wallet Status")
    client_wallet, _ = Wallet.objects.get_or_create(user=client)
    artisan_wallet, _ = Wallet.objects.get_or_create(user=artisan)
    print(f"[OK] Client wallet balance: {client_wallet.balance} EGP")
    print(f"[OK] Artisan wallet balance: {artisan_wallet.balance} EGP")
    
    # 7. Summary
    print_section("SUMMARY")
    print("[OK] Test data created successfully!")
    print("\nTest Credentials:")
    print(f"  Client:  username='test_client', password='test123'")
    print(f"  Artisan: username='test_artisan', password='test123'")
    print(f"  Admin:   username='admin', password='admin123'")
    print("\nAPI Endpoints:")
    print(f"  Base URL: http://localhost:8000/api/")
    print(f"  Admin:    http://localhost:8000/admin/")
    print(f"  Service Request ID: {service_request.id}")
    print(f"  Offer ID: {offer.id}")
    print("\nNext Steps:")
    print("  1. Login as client: POST /api/auth/login/")
    print("  2. Deposit funds: POST /api/payments/deposit/")
    print("  3. Accept offer: POST /api/offers/{offer_id}/accept/")
    print("  4. Complete service: POST /api/requests/{request_id}/complete/")

if __name__ == '__main__':
    test_application()

