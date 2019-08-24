from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('buy/', views.BuyView.as_view(), name='buy'),
    path('sell/', views.SellView.as_view(), name='sell'),
    path('quote/', views.QuoteView.as_view(), name='quote'),
    path('history/', views.HistoryView.as_view(), name='history'),
]
