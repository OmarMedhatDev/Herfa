from django.urls import path
from .views import (
    RegisterView, login_view, ProfileView, upload_national_id
)

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('upload-id/', upload_national_id, name='upload-id'),
]

