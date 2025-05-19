# sensores/urls.py

from django.urls import path
from .views import dashboard, latest_readings, update_actuator, sensor_readings_range

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('api/latest-readings/', latest_readings,  name='latest_readings'),
    path('api/update-actuator/', update_actuator, name='update_actuator'),
    path('api/sensor-readings/', sensor_readings_range, name='sensor_readings_range'),
]
