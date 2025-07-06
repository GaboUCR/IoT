# sensors/management/commands/mqtt_subscriber.py
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
import uuid
import pytz
from datetime import datetime
from sensors.models import Sensor, SensorReading
from django.utils.dateparse import parse_datetime
from django.db import (
    connection, close_old_connections,
    OperationalError, IntegrityError,
)
import json, time


class Command(BaseCommand):
    help = "Escucha MQTT y persiste lecturas (solo store_readings=True)."

    def handle(self, *args, **opts):
        # 1) Activa WAL
        close_old_connections()
        with connection.cursor() as c:
            c.execute("PRAGMA journal_mode=WAL;")
            
        # ————— 2) Configurar cliente MQTT con client_id —————
        client_id = f"iot-subscriber-{uuid.uuid4()}"
        client = mqtt.Client(client_id=client_id, clean_session=True)
        client.on_connect    = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message    = self.on_message

        # ————— 3) Conectar al broker local —————
        client.connect("localhost", 1883, keepalive=60)
        self.stdout.write(self.style.SUCCESS(
            f"Conectado a MQTT broker en localhost:1883 con client_id={client_id}"
        ))

        # 3) Variables de suscripción
        self.subscribed = set()
        refresh_interval = 1.0  # segundos
        next_refresh = time.time()

        try:
            # 4) Bucle principal: mezcla red + refresher
            while True:
                # ——— 4.1) Procesa mensajes MQTT hasta 1 s ———
                client.loop(timeout=1.0)

                # ——— 4.2) Cada refresh_interval s, ajusta suscripciones ———
                now = time.time()
                if now >= next_refresh:
                    next_refresh = now + refresh_interval
                    self._refresh_subscriptions(client)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("👋 Interrumpido, desconectando…"))
            client.disconnect()

    def _refresh_subscriptions(self, client):
        """Comprueba los topics en BD y subscribe/unsubscribe según cambios."""

        close_old_connections()
        current = set(
            Sensor.objects.values_list("topic", flat=True).distinct()
        )
        # nuevos →
        for t in current - self.subscribed:
            client.subscribe(t)
            self.subscribed.add(t)
            self.stdout.write(self.style.SUCCESS(f"🟢 Subscribed → {t}"))
        # eliminados →
        for t in self.subscribed - current:
            client.unsubscribe(t)
            self.subscribed.remove(t)
            self.stdout.write(self.style.WARNING(f"⚪️ Unsubscribed ← {t}"))

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.stdout.write(self.style.SUCCESS("✅ MQTT conectado OK"))
            # re-suscribirse por si hace falta
            for t in self.subscribed:
                client.subscribe(t)
        else:
            self.stderr.write(f"❌ MQTT rc={rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.stderr.write("⚠️ Desconexión inesperada, intentando reconectar…")

    def on_message(self, client, userdata, msg):
        # idéntico a tu lógica actual: parseo, reintentos y filtro store_readings=True
        try:
            v = msg.payload.decode()
            tz = pytz.timezone("America/Costa_Rica")
            ts = datetime.now(tz).isoformat()
            if v is None or ts is None:
                return

        except Exception as e:
            #  ⛔ Klaro y con contexto
            self.stderr.write(self.style.ERROR(
                f"[MQTT→DB] Error procesando mensaje "
                f"topic='{msg.topic}', payload={msg.payload[:80]!r} → {e}"
            ))
            return

        for attempt in range(5):
            try:
                close_old_connections()
                ids = (
                    Sensor.objects
                          .filter(topic=msg.topic, store_readings=True)
                          .values_list("id", flat=True)
                )
                if not ids:
                    return
                for sid in ids:
                    try:
                        SensorReading.objects.create(
                            sensor_id=sid, value=v, timestamp=ts
                        )

                        self.stdout.write(self.style.SUCCESS(
                            f"Guardada lectura: Sensor ID={sid}, Valor={v}, Timestamp={ts}"
                        ))  
                    
                    except IntegrityError as ie:
                        #  ⚠️  Ya existía una lectura con la misma PK/UNIQUE ó el sensor fue
                        #  eliminado mientras llegaba el mensaje.
                        self.stderr.write(self.style.WARNING(
                            f"[MQTT→DB] IntegrityError – lectura ignorada "
                            f"(topic='{msg.topic}', sensor_id={sensor.id}) → {ie}"
                        ))
                        # no lanzamos la excepción: solo saltamos a la siguiente lectura
                        continue
                        
                break

            except OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < 4:
                    time.sleep(0.1 * 2**attempt)
                else:
                    self.stderr.write(f"[ERROR] {e}")
                    return
