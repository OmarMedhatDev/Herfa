from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer, DepositSerializer


class WalletView(generics.RetrieveAPIView):
    """Get user wallet"""
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        wallet, created = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


class TransactionListView(generics.ListAPIView):
    """List user transactions"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return Transaction.objects.filter(wallet=wallet).select_related('related_request')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def deposit_funds(request):
    """Deposit funds to user wallet"""
    serializer = DepositSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    amount = serializer.validated_data['amount']
    
    with transaction.atomic():
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.deposit(amount)
        
        # Create transaction record
        Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type='DEPOSIT',
            description=f'Wallet deposit of {amount} EGP'
        )
    
    return Response({
        'message': 'Funds deposited successfully',
        'wallet': WalletSerializer(wallet).data
    }, status=status.HTTP_200_OK)
