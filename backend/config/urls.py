"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.http import HttpResponse

def home_view(request):
    return HttpResponse(render_to_string('index.html', request=request))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('api/auth/', include('apps.users.urls')),
    path('api/profiles/', include(('apps.users.urls', 'profiles'), namespace='profiles')),
    path('api/', include('apps.marketplace.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/chat/', include('apps.chat.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
