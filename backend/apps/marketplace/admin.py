from django.contrib import admin
from .models import ServiceRequest, Offer


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['category', 'client', 'status', 'assigned_artisan', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['description', 'client__username', 'client__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'ai_suggested_price']
    raw_id_fields = ['client', 'assigned_artisan']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['artisan', 'request', 'price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['artisan__username', 'request__description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['artisan', 'request']
