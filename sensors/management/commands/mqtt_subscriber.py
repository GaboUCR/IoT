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
        Al conectar, nos suscribimos a cada tópico que exista en la DB.
        De esta manera, no necesitamos dividir tópicos por tipo/nombre: 
        simplemente cada Sensor tiene su `topic` configurado.
        """
        if rc != 0:
            self.stderr.write(f"Error al conectar (rc={rc})")
            return

        # Recuperar todos los sensores activos para suscribirnos
        sensores = Sensor.objects.all().values_list("topic", flat=True)
        if not sensores:
            self.stdout.write(self.style.WARNING("No hay sensores en la base de datos para suscribir."))
        else:
            for top in sensores:
                client.subscribe(top)
            self.stdout.write(self.style.SUCCESS(f"Suscrito a tópicos de sensores: {list(sensores)}"))

    def on_message(self, client, userdata, msg):
        """
        Cada vez que llega un mensaje por MQTT:
          - Buscamos en la BD el Sensor cuyo campo `topic` coincida con msg.topic
          - Parseamos el payload JSON (debe contener 'value' y 'timestamp')
          - Creamos un SensorReading
        """
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            value = payload.get("value")
            timestamp_str = payload.get("timestamp")
            ts = parse_datetime(timestamp_str)

            if value is None or ts is None:
                # Si no vienen ambos campos, no persistimos
                self.stderr.write(f"[MQTT→DB] Payload incompleto en topic {msg.topic}: {payload}")
                return

            # Buscar el sensor en la base de datos por su campo `topic`
            try:
                sensor = Sensor.objects.get(topic=msg.topic)
            except Sensor.DoesNotExist:
                self.stderr.write(f"[MQTT→DB] No se encontró Sensor con topic = {msg.topic}")
                return

            # Crear y guardar la lectura
            SensorReading.objects.create(
                sensor=sensor,
                value=value,
                timestamp=ts
            )

            self.stdout.write(self.style.SUCCESS(
                f"[MQTT→DB] Guardada lectura: Sensor ID={sensor.id} ({sensor.name}), Valor={value}, Timestamp={ts}"
            ))

        except json.JSONDecodeError:
            self.stderr.write(f"[MQTT→DB] Payload no JSON en topic {msg.topic}: {msg.payload}")
        except Exception as e:
            self.stderr.write(f"[MQTT→DB] Error procesando mensaje en {msg.topic}: {e}")
