# sensores/urls.py

from django.urls import path
from .views import dashboard, latest_readings

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('api/latest-readings/', latest_readings,  name='latest_readings'),
]
