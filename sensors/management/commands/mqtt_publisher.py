# sensors/management/commands/mqtt_publisher.py

from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from sensors.models import Actuator
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
        # 1) Activar WAL
        close_old_connections()
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL;")

        # 2) Preparar zona horaria y cliente MQTT
        tz = pytz.timezone("America/Costa_Rica")
        client = mqtt.Client()

        # Asociar callbacks
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # Conectar y arrancar loop en segundo plano
        client.connect("localhost", 1883, 60)
        self.stdout.write(self.style.SUCCESS("Conectado al broker MQTT localhost:1883"))
        client.loop_start()

        # Estado interno
        self.last_values = {}
        self.subscribed_topics = set()

        try:
            while True:
                # A) Sincronizar dinámicamente suscripciones MQTT
                close_old_connections()
                current_topics = set(
                    Actuator.objects.values_list("topic", flat=True).distinct()
                )

                # Suscribir a nuevos topics
                for topic in current_topics - self.subscribed_topics:
                    client.subscribe(topic)
                    self.stdout.write(self.style.SUCCESS(f"[MQTT→PUB] Suscrito a: {topic}"))

                # Desuscribir de topics eliminados
                for topic in self.subscribed_topics - current_topics:
                    client.unsubscribe(topic)
                    self.stdout.write(self.style.WARNING(f"[MQTT→PUB] Desuscrito de: {topic}"))

                self.subscribed_topics = current_topics

                # B) Publicar estado de actuadores
                now_iso = datetime.now(tz).isoformat()
                close_old_connections()
                actuators = Actuator.objects.all()

                for act in actuators:
                    # Valor actual según tipo
                    current_value = act.value_boolean if act.actuator_type == "binario" else act.value_text

                    # Si no cambió, saltar
                    prev = self.last_values.get(act.id)
                    if prev == current_value:
                        continue

                    self.last_values[act.id] = current_value
                    payload = {
                        "id":        act.id,
                        "name":      act.name,
                        "type":      act.actuator_type,
                        "value":     current_value,
                        "timestamp": now_iso
                    }

                    # Intentar publicación con backoff
                    max_retries = 5
                    backoff = 0.1
                    for _ in range(max_retries):
                        try:
                            client.publish(act.topic, json.dumps(payload))
                            self.stdout.write(self.style.SUCCESS(
                                f"[DB→MQTT] Publicado en {act.topic}: {payload}"
                            ))
                            break
                        except Exception:
                            time.sleep(backoff)
                            backoff *= 2

                # Pausa antes del siguiente ciclo
                time.sleep(0.5)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Interrumpido, cerrando MQTT..."))
            client.loop_stop()
            client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.stdout.write(self.style.SUCCESS("Callback: conectado exitosamente al broker MQTT."))
        else:
            self.stderr.write(f"Callback: error de conexión MQTT, rc={rc}")

    def on_message(self, client, userdata, msg):
        # Procesa mensajes entrantes para actualizar actuadores en BD
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            new_value = payload.get("value")
            if new_value is None:
                return
        except Exception:
            return

        max_retries = 5
        backoff = 0.1
        for attempt in range(max_retries):
            try:
                close_old_connections()
                actuators = Actuator.objects.filter(topic=msg.topic)
                if not actuators.exists():
                    return

                for act in actuators:
                    # Convierte y asigna valor
                    if act.actuator_type == "binario":
                        valor_bool = (
                            new_value if isinstance(new_value, bool)
                            else str(new_value).lower() in ("1","true","on","sí","si")
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
                    # Actualiza caché local
                    self.last_values[act.id] = new_value
                    self.stdout.write(self.style.SUCCESS(
                        f"[MQTT→DB] Actuador {act.id} actualizado: {new_value}"
                    ))
                break

            except OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    self.stderr.write(
                        f"[ERROR] No se pudo actualizar actuadores tras {max_retries} intentos: {e}"
                    )
                    return
