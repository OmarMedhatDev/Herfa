from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'transaction_type', 'related_request', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__user__username', 'description']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['wallet', 'related_request']
