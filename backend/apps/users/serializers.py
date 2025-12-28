from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, ArtisanProfile, ClientProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password')
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='CLIENT')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'phone_number', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', ''),
            role=validated_data.get('role', 'CLIENT')
        )
        
        # Create profile based on role
        if user.role == 'ARTISAN':
            ArtisanProfile.objects.create(
                user=user,
                display_name=user.username
            )
        elif user.role == 'CLIENT':
            ClientProfile.objects.create(
                user=user,
                display_name=user.username
            )
        
        return user


class ArtisanProfileSerializer(serializers.ModelSerializer):
    """Serializer for Artisan Profile"""
    user = UserSerializer(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ArtisanProfile
        fields = [
            'id', 'user', 'display_name', 'bio', 'national_id_photo',
            'verification_status', 'rejection_reason', 'id_confidence_score',
            'rating_avg', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'verification_status', 'rejection_reason',
            'id_confidence_score', 'rating_avg', 'created_at', 'updated_at'
        ]


class ClientProfileSerializer(serializers.ModelSerializer):
    """Serializer for Client Profile"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ClientProfile
        fields = ['id', 'user', 'display_name', 'address', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProfileSerializer(serializers.Serializer):
    """Combined profile serializer that returns appropriate profile based on user role"""
    def to_representation(self, instance):
        if instance.role == 'ARTISAN':
            if hasattr(instance, 'artisan_profile'):
                return ArtisanProfileSerializer(instance.artisan_profile).data
        elif instance.role == 'CLIENT':
            if hasattr(instance, 'client_profile'):
                return ClientProfileSerializer(instance.client_profile).data
        return {'user': UserSerializer(instance).data}

