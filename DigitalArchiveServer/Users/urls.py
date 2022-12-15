from django.urls import path

from .views import register

urlpatterns = [
    path('accounts/register', register, name='register'),
]