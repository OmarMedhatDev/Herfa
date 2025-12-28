from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatMessageCreateSerializer
from apps.marketplace.models import ServiceRequest
from apps.marketplace.ai_services import ChatSafetyService


class ChatMessageListView(generics.ListAPIView):
    """List chat messages for a service request"""
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        request_id = self.kwargs.get('request_id')
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Verify user has access to this chat
        user = self.request.user
        if user.role == 'CLIENT' and service_request.client != user:
            raise permissions.PermissionDenied("You don't have access to this chat")
        elif user.role == 'ARTISAN' and service_request.assigned_artisan != user:
            raise permissions.PermissionDenied("You don't have access to this chat")
        
        return ChatMessage.objects.filter(request=service_request).select_related('sender', 'request')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request, request_id):
    """Send a chat message"""
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    user = request.user
    
    # Verify user has access to this chat
    # Chat is only available after offer is accepted
    if service_request.status != 'IN_PROGRESS':
        return Response(
            {'error': 'Chat is only available for in-progress services'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if user.role == 'CLIENT' and service_request.client != user:
        return Response(
            {'error': 'You don\'t have access to this chat'},
            status=status.HTTP_403_FORBIDDEN
        )
    elif user.role == 'ARTISAN' and service_request.assigned_artisan != user:
        return Response(
            {'error': 'You don\'t have access to this chat'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ChatMessageCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Check message safety
    content = serializer.validated_data['content']
    is_safe, flag_reason = ChatSafetyService.check_message_safety(content)
    
    message = ChatMessage.objects.create(
        request=service_request,
        sender=user,
        content=content,
        is_flagged=not is_safe,
        flag_reason=flag_reason
    )
    
    response_data = ChatMessageSerializer(message).data
    
    if not is_safe:
        response_data['warning'] = flag_reason
    
    return Response(response_data, status=status.HTTP_201_CREATED)
