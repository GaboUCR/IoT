# sensors/management/commands/mqtt_publisher.py

from django.core.management.base import BaseCommand
from sensors.models import Actuator
import paho.mqtt.client as mqtt
from datetime import datetime
import pytz
import json
import time

class Command(BaseCommand):
    help = "Publica el estado de los actuadores solo si cambia"

    def handle(self, *args, **options):
        tz = pytz.timezone("America/Costa_Rica")
        client = mqtt.Client()
        client.connect("localhost", 1883, 60)
        self.stdout.write(self.style.SUCCESS("Conectado a broker MQTT (localhost:1883)"))

        last_values = {}  # clave: actuator.id → valor actual

        try:
            while True:
                now = datetime.now(tz).isoformat()

                for actuator in Actuator.objects.all():
                    # Seleccionar el valor según tipo
                    value = actuator.value_boolean if actuator.actuator_type == "binario" else actuator.value_text

                    # Saltar si no ha cambiado
                    if actuator.id in last_values and last_values[actuator.id] == value:
                        continue

                    # Actualizar valor guardado
                    last_values[actuator.id] = value

                    topic = f"actuators/{actuator.actuator_type}/{actuator.name.replace(' ', '_')}"
                    payload = {
                        "id": actuator.id,
                        "name": actuator.name,
                        "type": actuator.actuator_type,
                        "value": value,
                        "timestamp": now
                    }

                    client.publish(topic, json.dumps(payload))
                    self.stdout.write(f"[MQTT] Publicado en {topic}: {payload}")

                time.sleep(0.5)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Interrumpido manualmente, cerrando conexión"))
            client.disconnect()
