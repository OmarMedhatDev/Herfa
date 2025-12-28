from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'request', 'is_flagged', 'sent_at']
    list_filter = ['is_flagged', 'sent_at']
    search_fields = ['content', 'sender__username', 'request__description']
    readonly_fields = ['id', 'sent_at']
    raw_id_fields = ['sender', 'request']
