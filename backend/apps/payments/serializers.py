from rest_framework import serializers
from .models import Wallet, Transaction
from apps.users.serializers import UserSerializer


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for Wallet"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'balance', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction"""
    wallet = WalletSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'wallet', 'amount', 'transaction_type',
            'related_request', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'wallet', 'created_at']


class DepositSerializer(serializers.Serializer):
    """Serializer for wallet deposit"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value

