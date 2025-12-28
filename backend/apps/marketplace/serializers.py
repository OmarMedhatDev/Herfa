from rest_framework import serializers
from .models import ServiceRequest, Offer
from apps.users.serializers import UserSerializer


class ServiceRequestSerializer(serializers.ModelSerializer):
    """Serializer for Service Request"""
    client = UserSerializer(read_only=True)
    assigned_artisan = UserSerializer(read_only=True)
    offers_count = serializers.IntegerField(read_only=True, source='offers.count')
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'client', 'category', 'description', 'media_url',
            'budget_min', 'budget_max', 'ai_suggested_price', 'status',
            'assigned_artisan', 'offers_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'ai_suggested_price', 'status', 'assigned_artisan', 'created_at', 'updated_at']


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Service Request"""
    class Meta:
        model = ServiceRequest
        fields = ['category', 'description', 'media_url', 'budget_min', 'budget_max']
    
    def validate(self, attrs):
        if attrs['budget_min'] > attrs['budget_max']:
            raise serializers.ValidationError("budget_min cannot be greater than budget_max")
        return attrs


class OfferSerializer(serializers.ModelSerializer):
    """Serializer for Offer"""
    artisan = UserSerializer(read_only=True)
    request = ServiceRequestSerializer(read_only=True)
    
    class Meta:
        model = Offer
        fields = [
            'id', 'request', 'artisan', 'price', 'message',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'artisan', 'status', 'created_at', 'updated_at']


class OfferCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Offer"""
    class Meta:
        model = Offer
        fields = ['price', 'message']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value

