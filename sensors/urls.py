# sensores/urls.py

from django.urls import path
from .views import dashboard, latest_readings, update_actuator, sensor_readings_range, delete_sensor, delete_actuator, set_sensor_store, send_text_command
from .views import sensor_create, actuator_create


urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/?view=pub', dashboard, name="actuators"),
    path('dashboard/?view=sub', dashboard, name="subscribers"),
    path('api/latest-readings/', latest_readings,  name='latest_readings'),
    path('api/update-actuator/', update_actuator, name='update_actuator'),
    path('api/sensor-readings/', sensor_readings_range, name='sensor_readings_range'),
    path('sensors/new/', sensor_create, name='sensor_create'),
    path('actuators/new/', actuator_create, name='actuator_create'),
    path("api/sensors/<int:sensor_id>/delete/", delete_sensor, name="delete_sensor"),
    path("api/actuators/<int:actuator_id>/delete/", delete_actuator, name="delete_actuator"),
    path("api/sensors/<int:sensor_id>/store/", set_sensor_store, name="set_sensor_store"),
    path("api/actuator-text/", send_text_command, name="send_text_command"),
]
