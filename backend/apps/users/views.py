from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from .models import User, ArtisanProfile, ClientProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    ArtisanProfileSerializer, ClientProfileSerializer, ProfileSerializer
)
from apps.payments.models import Wallet
from apps.marketplace.tasks import process_id_verification


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create wallet for the user
        Wallet.objects.create(user=user, balance=0.00)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """User login endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Try to authenticate with username or email
    user = None
    if '@' in username:
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            pass
    else:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
    
    if user and user.check_password(password):
        if not user.is_active:
            return Response(
                {'error': 'User account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        user = self.request.user
        if user.role == 'ARTISAN':
            return ArtisanProfileSerializer
        elif user.role == 'CLIENT':
            return ClientProfileSerializer
        return ProfileSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ARTISAN':
            return ArtisanProfile.objects.filter(user=user)
        elif user.role == 'CLIENT':
            return ClientProfile.objects.filter(user=user)
        return User.objects.filter(id=user.id)
    
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if user.role == 'ARTISAN' and hasattr(user, 'artisan_profile'):
            serializer = ArtisanProfileSerializer(user.artisan_profile)
        elif user.role == 'CLIENT' and hasattr(user, 'client_profile'):
            serializer = ClientProfileSerializer(user.client_profile)
        else:
            serializer = ProfileSerializer(user)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        user = request.user
        if user.role == 'ARTISAN' and hasattr(user, 'artisan_profile'):
            profile = user.artisan_profile
            serializer = ArtisanProfileSerializer(profile, data=request.data, partial=True)
        elif user.role == 'CLIENT' and hasattr(user, 'client_profile'):
            profile = user.client_profile
            serializer = ClientProfileSerializer(profile, data=request.data, partial=True)
        else:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_national_id(request):
    """Upload National ID photo for artisan verification"""
    if request.user.role != 'ARTISAN':
        return Response(
            {'error': 'Only artisans can upload National ID'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        profile = request.user.artisan_profile
    except ArtisanProfile.DoesNotExist:
        return Response(
            {'error': 'Artisan profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if 'national_id_photo' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    photo = request.FILES['national_id_photo']
    profile.national_id_photo = photo
    profile.save()
    
    # Process ID verification asynchronously
    process_id_verification.delay(str(profile.id))
    
    return Response({
        'message': 'National ID uploaded successfully. Verification in progress.',
        'profile': ArtisanProfileSerializer(profile).data
    }, status=status.HTTP_200_OK)
