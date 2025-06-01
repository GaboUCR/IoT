# sensors/management/commands/mqtt_publisher.py

from django.core.management.base import BaseCommand
from sensors.models import Actuator
import paho.mqtt.client as mqtt
from datetime import datetime
import pytz
import json
import time

class Command(BaseCommand):
    help = "Publica el estado de los actuadores (usando el campo `topic`) y se suscribe para actualizar la DB si llega un nuevo valor por MQTT."

    def handle(self, *args, **options):
        # 1) Preparar zona horaria y cliente MQTT
        tz = pytz.timezone("America/Costa_Rica")
        client = mqtt.Client()

        # 2) Caché local: actuator.id → último valor publicado/recibido
        last_values = {}

        # ----- CALLBACK: on_connect -----
        def on_connect(mosq, userdata, flags, rc):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS("Conectado a broker MQTT (localhost:1883)"))
                # Nos suscribimos a cada tópico definido en la tabla Actuator
                topics = Actuator.objects.all().values_list("topic", flat=True)
                if not topics:
                    self.stdout.write(self.style.WARNING("No hay actuadores en la base de datos para suscribir."))
                else:
                    for top in topics:
                        client.subscribe(top)
                    self.stdout.write(self.style.SUCCESS(f"Suscrito a tópicos de actuadores: {list(topics)}"))
            else:
                self.stdout.write(self.style.ERROR(f"Error de conexión MQTT, código: {rc}"))

        # ----- CALLBACK: on_message -----
        def on_message(mosq, userdata, msg):
            """
            Cuando llegue un mensaje por MQTT:
              - Buscamos el Actuator cuyo campo `topic` coincida con msg.topic
              - Leemos el payload JSON: { "id": <int>, "value": <bool|str>, "timestamp": ... }
              - Actualizamos el objeto Actuator en BD (value_boolean o value_text)
              - Actualizamos last_values para no re-publicar el mismo valor
            """
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                actuator_id = payload.get("id")
                new_value = payload.get("value")
                if actuator_id is None or new_value is None:
                    self.stderr.write(f"[MQTT→DB] Payload inválido en {msg.topic}: {payload}")
                    return

                # Recuperar el actuador por su campo `topic` en lugar de deducirlo
                try:
                    act = Actuator.objects.get(topic=msg.topic)
                except Actuator.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"[MQTT→DB] Actuador con topic={msg.topic} no existe en BD."))
                    return

                # Validar que el ID coincida (óptimo para detectar inconsistencias)
                if act.id != actuator_id:
                    self.stdout.write(self.style.WARNING(
                        f"[MQTT→DB] El payload ID({actuator_id}) no coincide con DB ID({act.id}). Ignorando."
                    ))
                    return

                # Dependiendo del tipo, guardamos en el campo correcto
                if act.actuator_type == "binario":
                    # Asegurar que new_value sea bool
                    valor_bool = new_value if isinstance(new_value, bool) else (str(new_value).lower() in ("1","true","on","sí","si"))
                    if act.value_boolean == valor_bool:
                        return
                    act.value_boolean = valor_bool
                    act.value_text = None  # limpiamos el campo texto
                else:  # "texto"
                    valor_str = str(new_value)
                    if act.value_text == valor_str:
                        return
                    act.value_text = valor_str
                    act.value_boolean = None  # limpiamos el campo binario

                act.save()
                self.stdout.write(self.style.SUCCESS(f"[MQTT→DB] Actuador ID={act.id} actualizado en BD: {new_value}"))

                # Evitar que, al iterar en el bucle principal, volvamos a publicar el mismo valor
                last_values[act.id] = new_value

            except json.JSONDecodeError:
                self.stderr.write(f"[MQTT→DB] Payload no JSON en topic {msg.topic}: {msg.payload}")
            except Exception as e:
                self.stderr.write(f"[MQTT→DB] Error procesando mensaje en {msg.topic}: {e}")

        # ----- Asignar callbacks -----
        client.on_connect = on_connect
        client.on_message = on_message

        # 3) Conectar y arrancar el loop en un hilo aparte
        client.connect("localhost", 1883, 60)
        client.loop_start()

        try:
            # 4) Bucle principal: cada 0.5 seg, revisar DB y publicar cambios
            while True:
                now_iso = datetime.now(tz).isoformat()

                # Recorremos todos los actuadores para detectar cambios en BD
                for act in Actuator.objects.all():
                    # Obtenemos el valor actual desde la BD
                    if act.actuator_type == "binario":
                        current_value = act.value_boolean
                    else:
                        current_value = act.value_text

                    # Si en caché ya existe y coincide, no publicamos
                    if act.id in last_values and last_values[act.id] == current_value:
                        continue

                    # Caso contrario: publicamos en MQTT usando su campo `topic`
                    last_values[act.id] = current_value

                    topic_to_publish = act.topic
                    payload = {
                        "id": act.id,
                        "name": act.name,
                        "type": act.actuator_type,
                        "value": current_value,
                        "timestamp": now_iso
                    }

                    client.publish(topic_to_publish, json.dumps(payload))
                    self.stdout.write(self.style.SUCCESS(
                        f"[DB→MQTT] Publicado en {topic_to_publish}: {payload}"
                    ))

                time.sleep(0.5)

        except KeyboardInterrupt:
            # 5) Cierre ordenado
            self.stdout.write(self.style.WARNING("Interrumpido manualmente, cerrando conexión"))
            client.loop_stop()
            client.disconnect()
