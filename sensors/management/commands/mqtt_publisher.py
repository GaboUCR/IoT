# sensors/management/commands/mqtt_publisher.py

from django.core.management.base import BaseCommand
from sensors.models import Actuator
import paho.mqtt.client as mqtt
from datetime import datetime
import pytz
import json
import time


class Command(BaseCommand):
    help = (
        "Publica el estado de los actuadores (usando el campo `topic`) "
        "y se suscribe para actualizar la DB si llega un nuevo valor por MQTT."
    )

    def handle(self, *args, **options):
        # 1) Preparar zona horaria y cliente MQTT
        tz = pytz.timezone("America/Costa_Rica")
        client = mqtt.Client()

        # 2) Caché local: actuator.id → último valor publicado/recibido
        last_values = {}

        # 3) Conjunto de topics a los que ya estamos suscritos
        subscribed_topics = set()

        # ----- CALLBACK: on_connect -----
        def on_connect(mosq, userdata, flags, rc):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS("Conectado a broker MQTT (localhost:1883)"))

                # Nos suscribimos a todos los topics distintos de Actuator en BD
                distinct_topics = set(
                    Actuator.objects.values_list("topic", flat=True).distinct()
                )
                for top in distinct_topics:
                    client.subscribe(top)
                subscribed_topics.update(distinct_topics)

                self.stdout.write(
                    self.style.SUCCESS(f"Suscrito a tópicos de actuadores: {list(distinct_topics)}")
                )
            else:
                self.stdout.write(self.style.ERROR(f"Error de conexión MQTT, código: {rc}"))

        # ----- CALLBACK: on_message -----
        def on_message(mosq, userdata, msg):
            """
            Cuando llegue un mensaje por MQTT:
              - Buscamos TODOS los Actuator cuyo campo `topic` coincida con msg.topic
              - Leemos el payload JSON: { "id": <int>, "value": <bool|str>, "timestamp": ... }
              - Para cada Actuator, actualizamos su valor en BD SOLO si cambió
              - Actualizamos last_values para no re-publicar el mismo valor
            """
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                new_value = payload.get("value")
                if new_value is None:
                    self.stderr.write(f"[MQTT→DB] Payload inválido en {msg.topic}: {payload}")
                    return

                # Recuperar todos los actuadores que usen este topic
                actuators = Actuator.objects.filter(topic=msg.topic)
                if not actuators.exists():
                    self.stdout.write(
                        self.style.WARNING(f"[MQTT→DB] No hay actuadores con topic={msg.topic} en BD.")
                    )
                    return

                # Para cada actuador con este topic, actualizamos si el valor cambió
                for act in actuators:
                    if act.actuator_type == "binario":
                        # Convertir new_value a bool
                        valor_bool = (
                            new_value if isinstance(new_value, bool)
                            else (str(new_value).lower() in ("1", "true", "on", "sí", "si"))
                        )
                        if act.value_boolean == valor_bool:
                            continue
                        act.value_boolean = valor_bool
                        act.value_text = None  # vaciar campo texto
                    else:  # "texto"
                        valor_str = str(new_value)
                        if act.value_text == valor_str:
                            continue
                        act.value_text = valor_str
                        act.value_boolean = None  # vaciar campo binario

                    act.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"[MQTT→DB] Actuador ID={act.id} actualizado: {new_value}")
                    )

                    # Evitar que, al iterar en el bucle principal, volvamos a publicar el mismo valor
                    last_values[act.id] = new_value

            except json.JSONDecodeError:
                self.stderr.write(f"[MQTT→DB] Payload no JSON en topic {msg.topic}: {msg.payload}")
            except Exception as e:
                self.stderr.write(f"[MQTT→DB] Error procesando mensaje en {msg.topic}: {e}")

        # ----- Asignar callbacks -----
        client.on_connect = on_connect
        client.on_message = on_message

        # 4) Conectar y arrancar el loop en un hilo aparte
        client.connect("localhost", 1883, 60)
        client.loop_start()

        try:
            # 5) Bucle principal: cada 0.5 seg, revisar DB, publicar cambios y detectar nuevos topics
            while True:
                now_iso = datetime.now(tz).isoformat()

                # —————————————————————————————————————————————————————————
                # (A) Detectar nuevos actores en BD y suscribirse a sus topics
                # —————————————————————————————————————————————————————————
                current_topics = set(
                    Actuator.objects.values_list("topic", flat=True).distinct()
                )
                new_topics = current_topics - subscribed_topics
                for t in new_topics:
                    client.subscribe(t)
                if new_topics:
                    subscribed_topics.update(new_topics)
                    self.stdout.write(
                        self.style.SUCCESS(f"Se agregaron y suscribieron nuevos topics: {list(new_topics)}")
                    )

                # —————————————————————————————————————————————————————————
                # (B) Recorremos todos los actuadores para detectar cambios en BD
                # —————————————————————————————————————————————————————————
                for act in Actuator.objects.all():
                    # Obtener el valor actual desde la BD
                    if act.actuator_type == "binario":
                        current_value = act.value_boolean
                    else:
                        current_value = act.value_text

                    # Si en caché ya existe y coincide, no publicamos
                    if act.id in last_values and last_values[act.id] == current_value:
                        continue

                    # Caso contrario: publicamos en MQTT usando su topic
                    last_values[act.id] = current_value
                    topic_to_publish = act.topic
                    payload = {
                        "id":        act.id,
                        "name":      act.name,
                        "type":      act.actuator_type,
                        "value":     current_value,
                        "timestamp": now_iso
                    }

                    client.publish(topic_to_publish, json.dumps(payload))
                    self.stdout.write(
                        self.style.SUCCESS(f"[DB→MQTT] Publicado en {topic_to_publish}: {payload}")
                    )

                time.sleep(0.5)

        except KeyboardInterrupt:
            # 6) Cierre ordenado
            self.stdout.write(self.style.WARNING("Interrumpido manualmente, cerrando conexión"))
            client.loop_stop()
            client.disconnect()
