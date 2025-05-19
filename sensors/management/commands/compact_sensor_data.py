from collections import defaultdict
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from sensors.models import Sensor, SensorReading

class Command(BaseCommand):
    help = "Compacta lecturas anteriores a hace 5 minutos en promedios por minuto."

    def handle(self, *args, **options):
        now    = timezone.now()
        cutoff = now - timedelta(minutes=5)

        for sensor in Sensor.objects.all():
            # 1) QuerySet de originales e IDs
            orig_qs = SensorReading.objects.filter(
                sensor=sensor,
                timestamp__lt=cutoff
            )
            orig_ids = list(orig_qs.values_list('id', flat=True))
            total    = len(orig_ids)
            if total == 0:
                continue

            self.stdout.write(f"[COMPACT] Sensor {sensor.name}: {total} lecturas < {cutoff.isoformat()}")

            # 2) Agrupar valores por minuto (usamos los objetos en memoria)
            buckets = defaultdict(list)
            orig_readings = SensorReading.objects.filter(id__in=orig_ids)
            for r in orig_readings:
                minute_ts = r.timestamp.replace(second=0, microsecond=0)
                buckets[minute_ts].append(r.value)

            # 3) Crear nuevas lecturas agregadas
            created = 0
            for minute_ts, vals in buckets.items():
                avg = sum(vals) / len(vals)
                SensorReading.objects.create(
                    sensor=sensor,
                    value=round(avg, 2),
                    timestamp=minute_ts
                )
                created += 1

            # 4) Borrar **solo** las originales
            deleted, _ = SensorReading.objects.filter(id__in=orig_ids).delete()
            self.stdout.write(f"  → Eliminadas {deleted} originales, creadas {created} promedios")

        self.stdout.write(self.style.SUCCESS("Compactación por minuto completada."))
