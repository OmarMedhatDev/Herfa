#!/usr/bin/env python
"""
Script to verify Herfa backend setup
"""
import os
import sys
import django

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import ArtisanProfile, ClientProfile
from apps.payments.models import Wallet
from apps.marketplace.models import ServiceRequest, Offer

User = get_user_model()

def verify_setup():
    """Verify that the setup is correct"""
    print("Verifying Herfa Backend Setup...")
    print("=" * 50)
    
    # Check models
    print("\n✓ Models imported successfully")
    
    # Check if we can create a test user
    try:
        test_user = User.objects.filter(username='test_user').first()
        if not test_user:
            test_user = User.objects.create_user(
                username='test_user',
                email='test@example.com',
                password='testpass123',
                role='CLIENT'
            )
            print("✓ Test user created")
        else:
            print("✓ Test user exists")
    except Exception as e:
        print(f"✗ Error creating test user: {e}")
        return False
    
    # Check wallet creation
    try:
        wallet, created = Wallet.objects.get_or_create(user=test_user)
        if created:
            print("✓ Wallet created for test user")
        else:
            print("✓ Wallet exists for test user")
    except Exception as e:
        print(f"✗ Error creating wallet: {e}")
        return False
    
    # Check profile creation
    try:
        if test_user.role == 'CLIENT':
            profile, created = ClientProfile.objects.get_or_create(user=test_user)
            if created:
                print("✓ Client profile created")
            else:
                print("✓ Client profile exists")
    except Exception as e:
        print(f"✗ Error creating profile: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Setup verification complete!")
    print("\nTo start the server:")
    print("  python manage.py runserver")
    print("\nTo create a superuser:")
    print("  python manage.py createsuperuser")
    print("\nTo run migrations:")
    print("  python manage.py migrate")
    
    return True

if __name__ == '__main__':
    verify_setup()

