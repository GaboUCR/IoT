from django.core.management.base import BaseCommand
from django.utils import timezone

from sensors.models import SensorReading

class Command(BaseCommand):
    help = "Elimina todas las lecturas del día más antiguo registrado."

    def handle(self, *args, **options):
        # Lista de días con lecturas ordenada ascendente
        dates = SensorReading.objects.dates('timestamp', 'day', order='ASC')
        if len(dates) < 2:
            self.stdout.write("No hay suficiente historial para purgar.")
            return

        oldest = dates[0]
        qs = SensorReading.objects.filter(timestamp__date=oldest)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.WARNING(f"[PURGE] Eliminadas {count} lecturas del día {oldest.isoformat()}"))
        self.stdout.write(self.style.SUCCESS("Purge completado."))
