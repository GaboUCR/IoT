from collections import defaultdict
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from sensors.models import Sensor, SensorReading

class Command(BaseCommand):
    help = "Compacta lecturas de los últimos 10 minutos en promedios por minuto."

    def handle(self, *args, **options):
        now    = timezone.now()
        cutoff = now - timedelta(minutes=10)

        for sensor in Sensor.objects.all():
            # 1) QuerySet de lecturas entre [cutoff, now]
            recent_qs = SensorReading.objects.filter(
                sensor=sensor,
                timestamp__gte=cutoff,
                timestamp__lte=now
            ).order_by("timestamp")

            recent_ids = list(recent_qs.values_list('id', flat=True))
            total      = len(recent_ids)
            if total == 0:
                continue

            self.stdout.write(
                f"[COMPACT] Sensor {sensor.name}: {total} lecturas en los últimos 10 minutos"
            )

            # 2) Agrupar valores por minuto
            buckets = defaultdict(list)
            for r in recent_qs:
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

            # 4) Borrar solo las originales de este período
            deleted, _ = SensorReading.objects.filter(id__in=recent_ids).delete()
            self.stdout.write(
                f"  → Eliminadas {deleted} originales, creadas {created} promedios"
            )

        self.stdout.write(self.style.SUCCESS("Compactación de últimos 10 minutos completada."))
