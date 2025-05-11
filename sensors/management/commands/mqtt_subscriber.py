from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from sensors.models import Sensor, SensorReading
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.dateparse import parse_datetime
import json

class Command(BaseCommand):
    help = "Suscribe a MQTT y persiste lecturas en BD y Channels"

    def handle(self, *args, **options):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect("localhost", 1883, 60)
        client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("sensors/#")

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
            value = data["value"]
            ts = parse_datetime(data["timestamp"])
            # Extraer tipo y nombre del topic:
            _, sensor_type, raw_name = msg.topic.split("/", 2)
            name = raw_name.replace("_", " ")
            sensor = Sensor.objects.get(sensor_type=sensor_type, name=name)
            reading = SensorReading.objects.create(
                sensor=sensor,
                value=value,
                timestamp=ts
            )

            print(str(sensor.id))
            # Notificar vía Channels
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                "sensors",
                {
                    "type":        "sensor_update",
                    "sensor_id":   sensor.id,
                    "value":       value,
                    "timestamp":   data["timestamp"],
                }
            )
            print("► Evento enviado a Channels:", {
                "sensor_id": sensor.id,
                "value":     value,
                "timestamp": data["timestamp"],
            })

        except Exception as e:
            self.stderr.write(f"Error procesando {msg.topic}: {e}")