# sensors/admin.py
from django.contrib import admin
from .models import Sensor, SensorReading, Actuator

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sensor_type", "unit")
    search_fields = ("name", "sensor_type")

@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("sensor", "value", "timestamp")
    list_filter = ("sensor",)
    search_fields = ("sensor__name",)
    date_hierarchy = "timestamp"

@admin.register(Actuator)
class ActuatorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "actuator_type", "value_boolean", "value_text")
    search_fields = ("name", "actuator_type")