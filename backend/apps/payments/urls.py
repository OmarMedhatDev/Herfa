from django.urls import path
from .views import WalletView, TransactionListView, deposit_funds

app_name = 'payments'

urlpatterns = [
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('deposit/', deposit_funds, name='deposit'),
]

