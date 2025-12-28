from django.urls import path
from .views import ChatMessageListView, send_message

app_name = 'chat'

urlpatterns = [
    path('requests/<uuid:request_id>/messages/', ChatMessageListView.as_view(), name='message-list'),
    path('requests/<uuid:request_id>/send/', send_message, name='send-message'),
]

