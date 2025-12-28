"""
Signals for payments app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User
from .models import Wallet


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """Create wallet automatically when user is created"""
    if created:
        Wallet.objects.get_or_create(user=instance, defaults={'balance': 0.00})

