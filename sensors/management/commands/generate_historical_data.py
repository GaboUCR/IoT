# sensors/management/commands/generate_historical_data.py
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from sensors.models import Sensor, SensorReading

# Rangos por tipo de sensor, igual que tu mock original
RANGES = {
    "temperatura":  (20, 30),
    "humedad":      (30, 80),
    "voltaje":      (0, 5),
    "presion":      (90000, 110000),
    "luminosidad":  (100, 1000),
    "ph":           (5.5, 7.5),
    "co2":          (400, 1200),
    "gas":          (100, 300),
    "proximidad":   (0, 200),
    "ambiente":     (20, 30),
}

def simulate_sensor_value(sensor_type: str) -> float:
    low, high = RANGES.get(sensor_type, (0, 100))
    return round(random.uniform(low, high), 2)

class Command(BaseCommand):
    help = "Inserta lecturas históricas para los últimos 10 días, una por minuto y por sensor."

    def handle(self, *args, **options):
        sensors = list(Sensor.objects.all())
        if not sensors:
            self.stdout.write(self.style.WARNING("No se encontró ningún Sensor en la base de datos."))
            return

        now   = timezone.now()
        start = (now - timedelta(days=3)).replace(second=0, microsecond=0)

        total_inserted = 0
        current = start

        while current <= now:
            for sensor in sensors:
                value = simulate_sensor_value(sensor.sensor_type)
                # Creamos la lectura
                SensorReading.objects.create(
                    sensor=sensor,
                    value=value,
                    timestamp=current
                )
                total_inserted += 1
            # Avanzar un minuto
            current += timedelta(minutes=1)

        self.stdout.write(
            self.style.SUCCESS(
                f"Insertadas {total_inserted} lecturas "
                f"({len(sensors)} sensores × {(now-start).total_seconds()//60:.0f} min)."
            )
        )
