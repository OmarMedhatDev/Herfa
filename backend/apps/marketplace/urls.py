from django.urls import path
from .views import (
    ServiceRequestListCreateView, ServiceRequestDetailView,
    OfferCreateView, accept_offer, complete_service
)

app_name = 'marketplace'

urlpatterns = [
    path('requests/', ServiceRequestListCreateView.as_view(), name='request-list-create'),
    path('requests/<uuid:pk>/', ServiceRequestDetailView.as_view(), name='request-detail'),
    path('requests/<uuid:request_id>/bid/', OfferCreateView.as_view(), name='create-offer'),
    path('offers/<uuid:offer_id>/accept/', accept_offer, name='accept-offer'),
    path('requests/<uuid:request_id>/complete/', complete_service, name='complete-service'),
]

