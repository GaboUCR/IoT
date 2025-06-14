from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from sensors.models import Sensor, SensorReading
from django.utils.dateparse import parse_datetime
import json
import time

from django.db import connection, close_old_connections, OperationalError, IntegrityError

class Command(BaseCommand):
    help = "Se suscribe a MQTT usando el campo `topic` de cada Sensor y persiste las lecturas en BD."

    def handle(self, *args, **options):
        # ————— 1) Activar WAL —————
        close_old_connections()
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL;")

        # ————— 2) Configurar cliente MQTT —————
        client = mqtt.Client()
        client.on_connect = self.on_connect  # solo para logging
        client.on_message = self.on_message

        # ————— 3) Conectar al broker local —————
        client.connect("localhost", 1883, 60)
        self.stdout.write(self.style.SUCCESS("Conectado a MQTT broker en localhost:1883"))

        # ————— 4) Suscribirse a todos los topics actuales —————
        topics = set(Sensor.objects.values_list("topic", flat=True).distinct())
        for topic in topics:
            client.subscribe(topic)
            self.stdout.write(self.style.SUCCESS(f"[MQTT→SUB] Suscrito a: {topic}"))

        # ————— 5) Iniciar el loop principal (bloqueante, sin threading) —————
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Interrumpido manualmente, cerrando conexión MQTT"))
            client.disconnect()


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.stdout.write(self.style.SUCCESS("Callback: conectado OK al broker MQTT."))
        else:
            self.stderr.write(f"Callback: error de conexión MQTT, rc={rc}")

    def on_message(self, client, userdata, msg):
        # Parseo de payload
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            value = payload.get("value")
            timestamp_str = payload.get("timestamp")
            ts = parse_datetime(timestamp_str)
            if value is None or ts is None:
                raise ValueError("payload incompleto")
        except Exception:
            return

        # Guardar lectura con reintentos ante bloqueos
        max_retries = 5
        backoff = 0.1

        for attempt in range(max_retries):
            try:
                close_old_connections()
                sensor_ids = list(
                    Sensor.objects
                        .filter(topic=msg.topic, store_readings=True)
                        .values_list("id", flat=True)
                )
                if not sensor_ids:
                    return

                for sid in sensor_ids:
                    try:
                        sensor = Sensor.objects.get(id=sid)
                    except Sensor.DoesNotExist:
                        continue

                    try:
                        SensorReading.objects.create(
                            sensor=sensor,
                            value=value,
                            timestamp=ts
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f"[MQTT→DB] Guardada lectura sensor {sensor.id}: {value} @ {ts}"
                        ))
                    except IntegrityError:
                        # FK falló, sensor borrado en carrera
                        continue

                break

            except OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    self.stderr.write(f"[ERROR] No se pudo guardar tras {max_retries} intentos: {e}")
                    return
