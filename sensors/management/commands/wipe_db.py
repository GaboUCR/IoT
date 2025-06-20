# sensors/management/commands/wipe_db.py
from django.core.management.base import BaseCommand
from django.db import transaction
from sensors.models import (
    Sensor,
    SensorReading,
    Actuator,
    ActuatorMessage,
)

class Command(BaseCommand):
    help = "💀 Elimina **todo** el contenido de la base de datos (sensores, lecturas y actuadores)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            "\n⚠️  ESTO BORRARÁ PERMANENTEMENTE TODOS LOS DATOS.\n"
            "   • Sensores\n"
            "   • Lecturas históricas\n"
            "   • Actuadores y mensajes\n"
        ))
        confirm = input("Escribe «yes» para continuar: ").strip().lower()
        if confirm != "yes":
            self.stdout.write(self.style.NOTICE("Operación cancelada."))
            return

        with transaction.atomic():
            total_readings  = SensorReading.objects.count()
            total_messages  = ActuatorMessage.objects.count()
            total_sensors   = Sensor.objects.count()
            total_actuators = Actuator.objects.count()

            SensorReading.objects.all().delete()
            ActuatorMessage.objects.all().delete()
            Sensor.objects.all().delete()
            Actuator.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(
            f"🗑️  Base de datos limpiada:\n"
            f"   • {total_readings:>7} lecturas\n"
            f"   • {total_messages:>7} mensajes\n"
            f"   • {total_sensors:>7} sensores\n"
            f"   • {total_actuators:>7} actuadores"
        ))
