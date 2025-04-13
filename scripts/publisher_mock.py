
import time
import random
import json
import paho.mqtt.client as mqtt
from datetime import datetime

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
client = mqtt.Client()
client.connect("localhost", 1883, 60)

def simulate_sensor_value(sensor_type):
    # Rangos simulados por tipo
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
        payload = {
            "value": value,
            "unit": UNITS[sensor_type],
            "timestamp": datetime.utcnow().isoformat()
        }
        client.publish(topic, json.dumps(payload))
        print(f"[MQTT] Sent to {topic}: {payload}")

    time.sleep(2)  # Espera entre publicaciones
