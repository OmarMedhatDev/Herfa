"""
WebSocket consumers for real-time chat
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from apps.marketplace.models import ServiceRequest
from apps.marketplace.ai_services import ChatSafetyService
from .models import ChatMessage

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.request_id = self.scope['url_route']['kwargs']['request_id']
        self.room_group_name = f'chat_{self.request_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = self.scope['user'].id
        
        # Save message to database
        await self.save_message(user_id, message)
        
        # Check message safety
        is_safe, flag_reason = await self.check_message_safety(message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': user_id,
                'is_flagged': not is_safe,
                'flag_reason': flag_reason,
            }
        )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user_id': event['user_id'],
            'is_flagged': event['is_flagged'],
            'flag_reason': event.get('flag_reason'),
        }))
    
    @database_sync_to_async
    def save_message(self, user_id, content):
        user = User.objects.get(id=user_id)
        service_request = ServiceRequest.objects.get(id=self.request_id)
        
        # Check message safety
        is_safe, flag_reason = ChatSafetyService.check_message_safety(content)
        
        ChatMessage.objects.create(
            request=service_request,
            sender=user,
            content=content,
            is_flagged=not is_safe,
            flag_reason=flag_reason
        )
    
    @database_sync_to_async
    def check_message_safety(self, message):
        return ChatSafetyService.check_message_safety(message)

