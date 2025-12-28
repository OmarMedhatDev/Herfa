import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.users.models import User


class ServiceRequest(models.Model):
    """Service requests posted by clients"""
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    CATEGORY_CHOICES = [
        ('Plumbing', 'Plumbing'),
        ('Carpentry', 'Carpentry'),
        ('Electrical', 'Electrical'),
        ('Painting', 'Painting'),
        ('Cleaning', 'Cleaning'),
        ('HVAC', 'HVAC'),
        ('General', 'General'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    media_url = models.URLField(blank=True, null=True, help_text="URL to uploaded image/video")
    budget_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    budget_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    ai_suggested_price = models.CharField(max_length=50, blank=True, help_text="e.g., '150-200 EGP'")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    assigned_artisan = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_requests'
        ordering = ['-created_at']
        verbose_name = 'Service Request'
        verbose_name_plural = 'Service Requests'
    
    def __str__(self):
        return f"{self.category} - {self.client.username}"


class Offer(models.Model):
    """Offers/bids made by artisans on service requests"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='offers')
    artisan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'offers'
        ordering = ['-created_at']
        unique_together = ['request', 'artisan']  # One offer per artisan per request
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'
    
    def __str__(self):
        return f"{self.artisan.username} - {self.price} EGP"
