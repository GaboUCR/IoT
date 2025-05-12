from django.db import models

class Sensor(models.Model):
    name = models.CharField(max_length=64, unique=True)
    sensor_type = models.CharField(max_length=32)
    unit = models.CharField(max_length=8)

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

    name = models.CharField(max_length=64, unique=True)
    actuator_type = models.CharField(max_length=16, choices=ACTUATOR_TYPE_CHOICES)

    value_boolean = models.BooleanField(null=True, blank=True)
    value_text = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.actuator_type})"