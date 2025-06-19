# sensors/management/commands/export_to_csv.py
import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
import pytz

from sensors.models import (
    Sensor,
    SensorReading,
    Actuator,
)


class Command(BaseCommand):
    """
    Exporta los datos de la aplicación a CSV:

        sensors.csv              → catálogo de sensores
        sensor_readings.csv      → lecturas históricas (con nombre de sensor)
        actuators.csv            → catálogo de actuadores
    """

    help = "Exporta toda la base de datos a ficheros CSV (útil para respaldos o análisis externo)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--outdir",
            default="exports",
            help="Directorio donde se guardarán los CSV (por defecto ./exports/).",
        )
        parser.add_argument(
            "--tz",
            default="UTC",
            help=(
                "Zona horaria a la que se normalizarán los timestamps "
                "(por defecto UTC, ej. 'America/Costa_Rica')."
            ),
        )

    def handle(self, *args, **opts):
        outdir = Path(opts["outdir"])
        outdir.mkdir(parents=True, exist_ok=True)

        tz = pytz.timezone(opts["tz"])

        self._export_sensors(outdir)
        self._export_sensor_readings(outdir, tz)
        self._export_actuators(outdir)

        self.stdout.write(self.style.SUCCESS("✅ Exportación completa."))

    def _export_sensors(self, outdir: Path):
        path = outdir / "sensors.csv"
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["id", "name", "sensor_type", "unit", "topic", "store_readings"])
            for s in Sensor.objects.all():
                writer.writerow([s.id, s.name, s.sensor_type, s.unit, s.topic, int(s.store_readings)])
        self.stdout.write(self.style.SUCCESS(f"• {Sensor.objects.count():>7} sensores      → {path}"))

    def _export_sensor_readings(self, outdir: Path, tz):
        path = outdir / "sensor_readings.csv"
        total = 0
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            # ahora usamos nombre de sensor en lugar de ID
            writer.writerow(["sensor_name", "value", "timestamp_iso"])
            qs = SensorReading.objects.select_related("sensor").iterator(chunk_size=10_000)
            for r in qs:
                sensor_name = r.sensor.name
                ts_iso = timezone.localtime(r.timestamp, tz).isoformat()
                writer.writerow([sensor_name, r.value, ts_iso])
                total += 1
        self.stdout.write(self.style.SUCCESS(f"• {total:>7} lecturas       → {path}"))

    def _export_actuators(self, outdir: Path):
        path = outdir / "actuators.csv"
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                ["id", "name", "actuator_type", "topic", "value_boolean", "value_text"]
            )
            for a in Actuator.objects.all():
                writer.writerow(
                    [a.id, a.name, a.actuator_type, a.topic, a.value_boolean, a.value_text]
                )
        self.stdout.write(self.style.SUCCESS(f"• {Actuator.objects.count():>7} actuadores    → {path}"))