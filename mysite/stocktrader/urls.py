from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('buy/', views.BuyView.as_view(), name='buy'),
    path('sell/', views.SellView.as_view(), name='sell'),
]
