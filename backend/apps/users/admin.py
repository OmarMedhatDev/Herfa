from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ArtisanProfile, ClientProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'phone_number']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'role')}),
    )


@admin.register(ArtisanProfile)
class ArtisanProfileAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'user', 'verification_status', 'rating_avg', 'id_confidence_score']
    list_filter = ['verification_status', 'created_at']
    search_fields = ['display_name', 'user__username', 'user__email']
    readonly_fields = ['id_confidence_score', 'rating_avg', 'created_at', 'updated_at']
    
    actions = ['approve_verification', 'reject_verification']
    
    def approve_verification(self, request, queryset):
        updated = queryset.update(verification_status='VERIFIED')
        self.message_user(request, f'{updated} artisan(s) verified successfully.')
    approve_verification.short_description = "Approve verification for selected artisans"
    
    def reject_verification(self, request, queryset):
        updated = queryset.update(verification_status='REJECTED')
        self.message_user(request, f'{updated} artisan(s) rejected.')
    reject_verification.short_description = "Reject verification for selected artisans"


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'user', 'created_at']
    search_fields = ['display_name', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
