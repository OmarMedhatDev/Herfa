import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Custom User model with role-based access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    
    ROLE_CHOICES = [
        ('CLIENT', 'Client'),
        ('ARTISAN', 'Artisan'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class ArtisanProfile(models.Model):
    """Profile for Artisan users with verification status"""
    VERIFICATION_STATUS_CHOICES = [
        ('UNVERIFIED', 'Unverified'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artisan_profile')
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    national_id_photo = models.ImageField(upload_to='national_ids/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='UNVERIFIED'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    id_confidence_score = models.FloatField(default=0.0, help_text="AI confidence score (0.0 to 1.0)")
    rating_avg = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'artisan_profiles'
        verbose_name = 'Artisan Profile'
        verbose_name_plural = 'Artisan Profiles'
    
    def __str__(self):
        return f"{self.display_name} - {self.verification_status}"
    
    @property
    def is_verified(self):
        return self.verification_status == 'VERIFIED'


class ClientProfile(models.Model):
    """Profile for Client users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    display_name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'client_profiles'
        verbose_name = 'Client Profile'
        verbose_name_plural = 'Client Profiles'
    
    def __str__(self):
        return f"{self.display_name}"
