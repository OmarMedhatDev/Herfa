from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import ServiceRequest, Offer
from .serializers import (
    ServiceRequestSerializer, ServiceRequestCreateSerializer,
    OfferSerializer, OfferCreateSerializer
)
from .ai_services import PriceEstimationService
from apps.users.models import ArtisanProfile
from apps.payments.models import Wallet, Transaction
from apps.chat.models import ChatMessage


class ServiceRequestListCreateView(generics.ListCreateAPIView):
    """List and create service requests"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ServiceRequest.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category
        category_filter = self.request.query_params.get('category', None)
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        # Filter by user role
        if self.request.user.role == 'CLIENT':
            queryset = queryset.filter(client=self.request.user)
        # Artisans see all open requests
        
        return queryset.select_related('client', 'assigned_artisan').prefetch_related('offers')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ServiceRequestCreateSerializer
        return ServiceRequestSerializer
    
    def perform_create(self, serializer):
        if self.request.user.role != 'CLIENT':
            raise permissions.PermissionDenied("Only clients can create service requests")
        
        request_obj = serializer.save(client=self.request.user)
        
        # Get AI price suggestion
        try:
            ai_price = PriceEstimationService.estimate_price(
                request_obj.category,
                request_obj.description
            )
            request_obj.ai_suggested_price = ai_price
            request_obj.save()
        except Exception:
            # If AI service fails, continue without suggestion
            pass


class ServiceRequestDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update service request"""
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'CLIENT':
            return ServiceRequest.objects.filter(client=self.request.user)
        return ServiceRequest.objects.all()


class OfferCreateView(generics.CreateAPIView):
    """Create an offer on a service request"""
    serializer_class = OfferCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        if request.user.role != 'ARTISAN':
            return Response(
                {'error': 'Only artisans can create offers'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if artisan is verified
        try:
            profile = request.user.artisan_profile
            if not profile.is_verified:
                return Response(
                    {'error': 'You must be verified to submit offers. Please complete ID verification.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except ArtisanProfile.DoesNotExist:
            return Response(
                {'error': 'Artisan profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        request_id = kwargs.get('request_id')
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Check if request is open
        if service_request.status != 'OPEN':
            return Response(
                {'error': 'This service request is no longer accepting offers'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if artisan already made an offer
        if Offer.objects.filter(request=service_request, artisan=request.user).exists():
            return Response(
                {'error': 'You have already submitted an offer for this request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        offer = serializer.save(
            request=service_request,
            artisan=request.user
        )
        
        return Response(
            OfferSerializer(offer).data,
            status=status.HTTP_201_CREATED
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_offer(request, offer_id):
    """Client accepts an offer and moves funds to escrow"""
    if request.user.role != 'CLIENT':
        return Response(
            {'error': 'Only clients can accept offers'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    offer = get_object_or_404(Offer, id=offer_id)
    
    # Verify the offer belongs to a request owned by the client
    if offer.request.client != request.user:
        return Response(
            {'error': 'You can only accept offers for your own requests'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if offer is still pending
    if offer.status != 'PENDING':
        return Response(
            {'error': 'This offer has already been processed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if request is still open
    if offer.request.status != 'OPEN':
        return Response(
            {'error': 'This service request is no longer accepting offers'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    with transaction.atomic():
        # Get client wallet
        client_wallet, _ = Wallet.objects.get_or_create(user=request.user)
        
        # Check if client has sufficient balance
        if not client_wallet.has_sufficient_balance(offer.price):
            return Response(
                {
                    'error': 'Insufficient balance',
                    'required': float(offer.price),
                    'current_balance': float(client_wallet.balance)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Move funds to escrow (deduct from client wallet)
        client_wallet.withdraw(offer.price)
        
        # Create transaction record
        Transaction.objects.create(
            wallet=client_wallet,
            amount=-offer.price,  # Negative for debit
            transaction_type='HOLD_ESCROW',
            related_request=offer.request,
            description=f'Escrow hold for offer {offer.id}'
        )
        
        # Update offer status
        offer.status = 'ACCEPTED'
        offer.save()
        
        # Reject other offers for this request
        Offer.objects.filter(
            request=offer.request,
            status='PENDING'
        ).exclude(id=offer.id).update(status='REJECTED')
        
        # Update service request
        offer.request.status = 'IN_PROGRESS'
        offer.request.assigned_artisan = offer.artisan
        offer.request.save()
    
    return Response({
        'message': 'Offer accepted. Funds moved to escrow.',
        'offer': OfferSerializer(offer).data,
        'service_request': ServiceRequestSerializer(offer.request).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_service(request, request_id):
    """Client confirms service completion and releases payment"""
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    if request.user.role != 'CLIENT':
        return Response(
            {'error': 'Only clients can confirm completion'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if service_request.client != request.user:
        return Response(
            {'error': 'You can only complete your own service requests'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if service_request.status != 'IN_PROGRESS':
        return Response(
            {'error': 'Service request is not in progress'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    accepted_offer = service_request.offers.filter(status='ACCEPTED').first()
    if not accepted_offer:
        return Response(
            {'error': 'No accepted offer found'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    with transaction.atomic():
        # Get artisan wallet
        artisan_wallet, _ = Wallet.objects.get_or_create(user=service_request.assigned_artisan)
        
        # Release payment to artisan
        artisan_wallet.deposit(accepted_offer.price)
        
        # Create transaction record
        Transaction.objects.create(
            wallet=artisan_wallet,
            amount=accepted_offer.price,
            transaction_type='RELEASE_PAYMENT',
            related_request=service_request,
            description=f'Payment release for completed service {service_request.id}'
        )
        
        # Update service request status
        service_request.status = 'COMPLETED'
        service_request.save()
    
    return Response({
        'message': 'Service completed. Payment released to artisan.',
        'service_request': ServiceRequestSerializer(service_request).data
    }, status=status.HTTP_200_OK)
