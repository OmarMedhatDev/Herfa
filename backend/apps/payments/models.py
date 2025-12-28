import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.users.models import User
from apps.marketplace.models import ServiceRequest


class Wallet(models.Model):
    """User wallet for managing balance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wallets'
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
    
    def __str__(self):
        return f"{self.user.username} - {self.balance} EGP"
    
    def has_sufficient_balance(self, amount):
        """Check if wallet has sufficient balance"""
        return self.balance >= amount
    
    def deposit(self, amount):
        """Add funds to wallet"""
        self.balance += amount
        self.save()
    
    def withdraw(self, amount):
        """Deduct funds from wallet"""
        if not self.has_sufficient_balance(amount):
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.save()


class Transaction(models.Model):
    """Transaction history for wallet operations"""
    TRANSACTION_TYPE_CHOICES = [
        ('DEPOSIT', 'Deposit'),
        ('HOLD_ESCROW', 'Hold Escrow'),
        ('RELEASE_PAYMENT', 'Release Payment'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('REFUND', 'Refund'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Positive for credit, Negative for debit"
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    related_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - {self.amount} EGP"
