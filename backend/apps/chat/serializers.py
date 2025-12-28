from rest_framework import serializers
from .models import ChatMessage
from apps.users.serializers import UserSerializer
from apps.marketplace.serializers import ServiceRequestSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for Chat Message"""
    sender = UserSerializer(read_only=True)
    request = ServiceRequestSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'request', 'sender', 'content',
            'is_flagged', 'flag_reason', 'sent_at'
        ]
        read_only_fields = ['id', 'sender', 'is_flagged', 'flag_reason', 'sent_at']


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Chat Message"""
    class Meta:
        model = ChatMessage
        fields = ['content']

