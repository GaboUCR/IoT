# sensors/management/commands/mqtt_subscriber.py

from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from sensors.models import Sensor, SensorReading
from django.utils.dateparse import parse_datetime
import json

class Command(BaseCommand):
    help = "Se suscribe a MQTT usando el campo `topic` de cada Sensor y persiste las lecturas en BD."

    def handle(self, *args, **options):
        # 1) Configurar cliente MQTT
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # 2) Conectar al broker local
        client.connect("localhost", 1883, 60)
        self.stdout.write(self.style.SUCCESS("Conectado a MQTT broker en localhost:1883"))

        # 3) Loop infinito para recibir mensajes (los callbacks harán el trabajo)
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            client.disconnect()
            self.stdout.write(self.style.WARNING("Desconectado del broker MQTT"))

    def on_connect(self, client, userdata, flags, rc):
        """
        Al conectar, nos suscribimos a cada topic distinto que exista en la BD.
        """
        if rc != 0:
            self.stderr.write(f"Error al conectar (rc={rc})")
            return

        # Recuperar todos los topics distintos de Sensor para suscribirnos
        temas = Sensor.objects.values_list("topic", flat=True).distinct()
        if not temas:
            self.stdout.write(self.style.WARNING("No hay sensores en la base de datos para suscribir."))
        else:
            for top in temas:
                client.subscribe(top)
            self.stdout.write(self.style.SUCCESS(f"Suscrito a topics de sensores: {list(temas)}"))

    def on_message(self, client, userdata, msg):
        """
        Cada vez que llega un mensaje por MQTT:
          - Buscamos en la BD todos los Sensor cuyo campo `topic` coincida con msg.topic
          - Parseamos el payload JSON (debe contener 'value' y 'timestamp')
          - Creamos un SensorReading para cada sensor encontrado
        """
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            value = payload.get("value")
            timestamp_str = payload.get("timestamp")
            ts = parse_datetime(timestamp_str)

            if value is None or ts is None:
                self.stderr.write(f"[MQTT→DB] Payload incompleto en topic {msg.topic}: {payload}")
                return

            # Buscar todos los sensores en la base de datos cuyo topic coincida
            sensores = Sensor.objects.filter(topic=msg.topic)
            if not sensores.exists():
                self.stderr.write(f"[MQTT→DB] No se encontró ningún Sensor con topic = {msg.topic}")
                return

            # Para cada sensor encontrado, creamos y guardamos una lectura
            for sensor in sensores:
                SensorReading.objects.create(
                    sensor=sensor,
                    value=value,
                    timestamp=ts
                )
                self.stdout.write(self.style.SUCCESS(
                    f"[MQTT→DB] Guardada lectura: Sensor ID={sensor.id} ({sensor.name}), "
                    f"Valor={value}, Timestamp={ts}"
                ))

        except json.JSONDecodeError:
            self.stderr.write(f"[MQTT→DB] Payload no JSON en topic {msg.topic}: {msg.payload}")
        except Exception as e:
            self.stderr.write(f"[MQTT→DB] Error procesando mensaje en {msg.topic}: {e}")
