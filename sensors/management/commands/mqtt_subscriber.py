# sensors/management/commands/mqtt_subscriber.py

from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from sensors.models import Sensor, SensorReading
from django.utils.dateparse import parse_datetime
import json
import time

from django.db import connection, close_old_connections, OperationalError

class Command(BaseCommand):
    help = "Se suscribe a MQTT usando el campo `topic` de cada Sensor y persiste las lecturas en BD."

    def handle(self, *args, **options):
        # ————— 1) Activar WAL —————
        close_old_connections()
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL;")

        # ————— 2) Configurar cliente MQTT —————
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # ————— 3) Conectar al broker local —————
        client.connect("localhost", 1883, 60)
        self.stdout.write(self.style.SUCCESS("Conectado a MQTT broker en localhost:1883"))

        # 4) Loop para callbacks
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            client.disconnect()
            self.stdout.write(self.style.WARNING("Desconectado del broker MQTT"))

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            self.stderr.write(f"Error al conectar (rc={rc})")
            return

        close_old_connections()
        temas = Sensor.objects.values_list("topic", flat=True).distinct()
        if not temas:
            self.stdout.write(self.style.WARNING("No hay sensores para suscribir."))
        else:
            for top in temas:
                client.subscribe(top)
            self.stdout.write(self.style.SUCCESS(f"Suscrito a topics de sensores: {list(temas)}"))

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            value = payload.get("value")
            timestamp_str = payload.get("timestamp")
            ts = parse_datetime(timestamp_str)

            if value is None or ts is None:
                self.stderr.write(f"[MQTT→DB] Payload incompleto en {msg.topic}: {payload}")
                return
        except Exception:
            return

        # Intentar hasta 5 veces si da “database is locked”
        max_retries = 5
        backoff = 0.1

        for intento in range(max_retries):
            try:
                close_old_connections()
                sensores = Sensor.objects.filter(topic=msg.topic)
                if not sensores.exists():
                    return

                for sensor in sensores:
                    SensorReading.objects.create(
                        sensor=sensor,
                        value=value,
                        timestamp=ts
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"[MQTT→DB] Sensor {sensor.id} guardado: {value} @ {ts}"
                    ))
                break

            except OperationalError as e:
                if "database is locked" in str(e).lower():
                    if intento < max_retries - 1:
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    else:
                        self.stderr.write(f"[ERROR] No pude guardar en DB tras {max_retries} intentos: {e}")
                        return
                else:
                    raise

