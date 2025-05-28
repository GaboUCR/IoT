# sensores/urls.py

from django.urls import path
from .views import dashboard, latest_readings, update_actuator, sensor_readings_range
from .views import sensor_create, actuator_create


urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('api/latest-readings/', latest_readings,  name='latest_readings'),
    path('api/update-actuator/', update_actuator, name='update_actuator'),
    path('api/sensor-readings/', sensor_readings_range, name='sensor_readings_range'),
    path('sensors/new/', sensor_create, name='sensor_create'),
    path('actuators/new/', actuator_create, name='actuator_create'),
]
