from django.db import models
from django.utils import timezone

class Sensor(models.Model):
    name = models.CharField(max_length=64)
    sensor_type = models.CharField(max_length=32)
    unit = models.CharField(max_length=8)
    topic = models.CharField(max_length=128, default="sensor/null", help_text="Tópico MQTT asociado")

    store_readings = models.BooleanField(
        default=True,
        help_text="Si se desactiva, las lecturas entrantes no se almacenan en BD"
    )

    def __str__(self):
        return f"{self.name} ({self.sensor_type})"


class SensorReading(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings')
    value = models.FloatField()
    timestamp = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["sensor"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.sensor.name}: {self.value} @ {self.timestamp}"

class Actuator(models.Model):
    ACTUATOR_TYPE_CHOICES = [
        ("binario", "Binario"),
        ("texto", "Texto"),
    ]

    name = models.CharField(max_length=64)
    actuator_type = models.CharField(max_length=16, choices=ACTUATOR_TYPE_CHOICES)
    topic = models.CharField(max_length=128, default="sensor/null", help_text="Tópico MQTT asociado")

    value_boolean = models.BooleanField(null=True, blank=True)
    value_text = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.actuator_type})"


class ActuatorMessage(models.Model):
    """
    Historial de mensajes enviados a actuadores de tipo «texto».
    """
    actuator   = models.ForeignKey(
        Actuator,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    message    = models.CharField(max_length=256)
    timestamp  = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.actuator.name}: {self.message[:20]}… @ {self.timestamp}"