import uuid
from django.db import models
from apps.users.models import User
from apps.marketplace.models import ServiceRequest


class ChatMessage(models.Model):
    """Chat messages between clients and artisans"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_flagged = models.BooleanField(default=False, help_text="If AI detects safety violation")
    flag_reason = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['sent_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
    
    def __str__(self):
        return f"{self.sender.username} - {self.request.id}"
