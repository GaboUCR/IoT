# sensors/management/commands/mqtt_publisher.py

from django.core.management.base import BaseCommand
from sensors.models import Actuator
import paho.mqtt.client as mqtt
from datetime import datetime
import pytz
import json
import time

from django.db import connection, close_old_connections, OperationalError

class Command(BaseCommand):
    help = (
        "Publica el estado de los actuadores y actualiza la BD si llega un nuevo valor por MQTT."
    )

    def handle(self, *args, **options):
        # ————— 1) Activar WAL —————
        close_old_connections()
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL;")

        # ————— 2) Preparar zona horaria y cliente MQTT —————
        tz = pytz.timezone("America/Costa_Rica")
        client = mqtt.Client()

        last_values = {}
        subscribed_topics = set()

        def on_connect(mosq, userdata, flags, rc):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS("Conectado a broker MQTT (localhost:1883)"))
                # Suscribir a todos los topics existentes
                close_old_connections()
                distinct_topics = set(Actuator.objects.values_list("topic", flat=True).distinct())
                for t in distinct_topics:
                    client.subscribe(t)
                subscribed_topics.update(distinct_topics)
                self.stdout.write(self.style.SUCCESS(f"Suscrito a: {list(distinct_topics)}"))
            else:
                self.stdout.write(self.style.ERROR(f"Error de conexión MQTT, código: {rc}"))

        def on_message(mosq, userdata, msg):
            """
            Encolar y actualizar la BD con reintentos para “database is locked”.
            """
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                new_value = payload.get("value")
                if new_value is None:
                    return
            except Exception:
                return

            # Reintentos si da “database is locked”
            max_retries = 5
            backoff = 0.1
            for intento in range(max_retries):
                try:
                    close_old_connections()
                    actuators = Actuator.objects.filter(topic=msg.topic)
                    if not actuators.exists():
                        return

                    for act in actuators:
                        if act.actuator_type == "binario":
                            valor_bool = (
                                new_value if isinstance(new_value, bool)
                                else str(new_value).lower() in ("1", "true", "on", "sí", "si")
                            )
                            if act.value_boolean == valor_bool:
                                continue
                            act.value_boolean = valor_bool
                            act.value_text = None
                        else:
                            valor_str = str(new_value)
                            if act.value_text == valor_str:
                                continue
                            act.value_text = valor_str
                            act.value_boolean = None

                        act.save()
                        last_values[act.id] = new_value
                        self.stdout.write(self.style.SUCCESS(f"[MQTT→DB] Actuador {act.id} = {new_value}"))
                    break

                except OperationalError as e:
                    if "database is locked" in str(e).lower():
                        if intento < max_retries - 1:
                            time.sleep(backoff)
                            backoff *= 2
                            continue
                        else:
                            self.stderr.write(f"[ERROR] No pude actualizar actuador tras {max_retries} intentos: {e}")
                            return
                    else:
                        raise

        client.on_connect = on_connect
        client.on_message = on_message

        client.connect("localhost", 1883, 60)
        client.loop_start()

        try:
            while True:
                now_iso = datetime.now(tz).isoformat()

                # (A) Suscribir a nuevos topics si apareció un actuador recientemente
                close_old_connections()
                current_topics = set(Actuator.objects.values_list("topic", flat=True).distinct())
                nuevos = current_topics - subscribed_topics
                for t in nuevos:
                    client.subscribe(t)
                if nuevos:
                    subscribed_topics.update(nuevos)
                    self.stdout.write(self.style.SUCCESS(f"Nuevo topic(s): {list(nuevos)}"))

                # (B) Publicar cambios en actuadores con reintentos
                for act in Actuator.objects.all():
                    if act.actuator_type == "binario":
                        current_value = act.value_boolean
                    else:
                        current_value = act.value_text

                    if act.id in last_values and last_values[act.id] == current_value:
                        continue

                    last_values[act.id] = current_value
                    payload = {
                        "id":        act.id,
                        "name":      act.name,
                        "type":      act.actuator_type,
                        "value":     current_value,
                        "timestamp": now_iso
                    }

                    max_retries = 5
                    backoff = 0.1
                    for intento in range(max_retries):
                        try:
                            client.publish(act.topic, json.dumps(payload))
                            self.stdout.write(self.style.SUCCESS(
                                f"[DB→MQTT] Publicado en {act.topic}: {payload}"
                            ))
                            break
                        except Exception as e:
                            # Si la publicación falla (no suele ser por SQLite),
                            # podrías reintentar igual, pero normalmente client.publish no bloquea la BD.
                            time.sleep(backoff)
                            backoff *= 2
                            continue

                time.sleep(0.5)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Interrumpido, cerrando..."))
            client.loop_stop()
            client.disconnect()
