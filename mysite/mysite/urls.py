from django.contrib import admin
from django.urls import path, include
from .views import register

urlpatterns = [
    path('', include('stocktrader.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', register, name='register'),
    path('admin/', admin.site.urls),
]
