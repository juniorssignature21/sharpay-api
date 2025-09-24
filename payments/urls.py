from django.urls import path
from . import views

urlpatterns = [
    path('initialize/', views.initialize_payment, name='initialize-payment'),
    path('verify/<str:reference>/', views.verify_payment, name='verify-payment'),
    path('list/', views.payment_list, name='payment-list'),
    path('webhook/', views.paystack_webhook, name='paystack-webhook'),
    ]
