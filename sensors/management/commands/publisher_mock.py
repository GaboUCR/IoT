import time
import random
import json
import paho.mqtt.client as mqtt
from datetime import datetime
import pytz  
import os

# Zona horaria de Costa Rica
tz = pytz.timezone('America/Costa_Rica')
print("hola")
# Lista de sensores simulados
SENSORS = [
    ("temperatura", "Sensor de Temperatura"),
    ("humedad", "Sensor de Humedad"),
    ("voltaje", "Sensor de Voltaje"),
    ("presion", "Sensor de Presión"),
    ("luminosidad", "Sensor de Luminosidad"),
    ("ph", "Sensor de pH"),
    ("co2", "Sensor de CO₂"),
    ("gas", "Sensor de Gas"),
    ("proximidad", "Sensor de Proximidad"),
    ("ambiente", "Tarjeta de Lectura de Sensor Ambiental")
]

# Unidades por tipo
UNITS = {
    "temperatura": "°C",
    "humedad": "%",
    "voltaje": "V",
    "presion": "Pa",
    "luminosidad": "lx",
    "ph": "pH",
    "co2": "ppm",
    "gas": "ppm",
    "proximidad": "cm",
    "ambiente": "°C"
}

# Conexión al broker local
mqtt_host = os.environ.get("MQTT_HOST", "localhost")
print("pepa")
print("pepino:"+mqtt_host)
client = mqtt.Client()
client.connect(mqtt_host, 1883, 60)

def simulate_sensor_value(sensor_type):
    ranges = {
        "temperatura": (20, 30),
        "humedad": (30, 80),
        "voltaje": (0, 5),
        "presion": (90000, 110000),
        "luminosidad": (100, 1000),
        "ph": (5.5, 7.5),
        "co2": (400, 1200),
        "gas": (100, 300),
        "proximidad": (0, 200),
        "ambiente": (20, 30)
    }
    low, high = ranges.get(sensor_type, (0, 100))
    return round(random.uniform(low, high), 2)

while True:
    for sensor_type, sensor_name in SENSORS:
        topic = f"sensors/{sensor_type}/{sensor_name.replace(' ', '_')}"
        value = simulate_sensor_value(sensor_type)
        now_cr = datetime.now(tz)  # 👈 timestamp con hora local
        payload = {
            "value": value,
            "unit": UNITS[sensor_type],
            "timestamp": now_cr.isoformat()
        }
        client.publish(topic, json.dumps(payload))
        print(f"[MQTT] Sent to {topic}: {payload}")

    time.sleep(2)
