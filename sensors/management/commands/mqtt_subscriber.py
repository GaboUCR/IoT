# sensors/management/commands/mqtt_subscriber.py
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from sensors.models import Sensor, SensorReading
from django.utils.dateparse import parse_datetime
import json
import os

class Command(BaseCommand):
    help = "Suscribe a MQTT y persiste lecturas en BD"

    def handle(self, *args, **options):
        # Configurar cliente MQTT
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # Conectar al broker local
        mqtt_host = os.environ.get("MQTT_HOST", "localhost")
        client.connect(mqtt_host, 1883, 60)
        self.stdout.write(self.style.SUCCESS(f"Conectado a MQTT broker en {mqtt_host}:1883"))

        # Loop infinito para recibir mensajes
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            client.disconnect()
            self.stdout.write(self.style.WARNING("Desconectado del broker MQTT"))

    def on_connect(self, client, userdata, flags, rc):
        """Callback al conectar exitosamente al broker"""
        self.stdout.write(self.style.SUCCESS(f"Suscrito a topics: ['sensors/#'] (rc={rc})"))
        client.subscribe("sensors/#")

    def on_message(self, client, userdata, msg):
        """Callback al recibir mensaje MQTT"""
        try:
            data = json.loads(msg.payload)
            value = data.get("value")
            timestamp_str = data.get("timestamp")
            ts = parse_datetime(timestamp_str)

            # Extraer tipo y nombre del topic: sensors/<tipo>/<nombre>
            _, sensor_type, raw_name = msg.topic.split("/", 2)
            name = raw_name.replace("_", " ")

            # Buscar el sensor en la base de datos
            sensor = Sensor.objects.get(sensor_type=sensor_type, name=name)

            # Crear lectura y persistir
            reading = SensorReading.objects.create(
                sensor=sensor,
                value=value,
                timestamp=ts
            )

            self.stdout.write(self.style.SUCCESS(
                f"Guardada lectura: Sensor ID={sensor.id}, Valor={value}, Timestamp={ts}"
            ))
        except Sensor.DoesNotExist:
            self.stderr.write(f"Sensor no encontrado para topic {msg.topic}")
        except Exception as e:
            self.stderr.write(f"Error procesando {msg.topic}: {e}")
