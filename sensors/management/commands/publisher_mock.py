import time
import random
import json
import paho.mqtt.client as mqtt
from datetime import datetime
import pytz  

# Zona horaria de Costa Rica
tz = pytz.timezone('America/Costa_Rica')

# --------------------------------------------------------
# Definición de sensores basados en los topics del fixture
# --------------------------------------------------------
# Cada tupla debe tener exactamente 3 valores: (topic, tipo_sensor, unidad)
SENSORS = [
    ("sensor/temp_int",   "temperatura", "°C"),    # Temperatura Interior
    ("sensor/temp_ext",   "temperatura", "°C"),    # Temperatura Exterior
    ("sensor/humedad",    "humedad",     "%"),     # Humedad
    ("sensor/co2",        "co2",         "ppm"),   # CO2
    ("sensor/presion",    "presion",     "hPa"),   # Presión
    ("sensor/luz",        "luz",         "lux"),   # Luminosidad
    ("sensor/movimiento", "movimiento", ""),      # Movimiento
    ("sensor/agua",       "agua",        "cm"),    # Nivel de Agua
    ("sensor/gas",        "gas",         "ppm"),   # Gas
    ("sensor/sonido",     "sonido",      "dB"),     # Sonido
    ("sensor/temperatura", "temperatura", "°C")
]

# --------------------------------------------------------
# Función para simular un valor según el tipo de sensor
# --------------------------------------------------------
def simulate_sensor_value(sensor_type):
    """
    Devuelve un valor simulado según el tipo de sensor.
    """
    ranges = {
        "temperatura":  (20.0, 30.0),
        "humedad":      (30.0, 80.0),
        "co2":          (400.0, 1200.0),
        "presion":      (950.0, 1050.0),   # en hPa
        "luz":          (100.0, 1000.0),
        "movimiento":   (0, 1),            # 0 = sin movimiento, 1 = movimiento detectado
        "agua":         (0.0, 100.0),      # en centímetros de nivel
        "gas":          (100.0, 300.0),
        "sonido":       (30.0, 90.0)        # en dB
    }
    low, high = ranges.get(sensor_type, (0.0, 100.0))
    if sensor_type == "movimiento":
        return random.choice([0, 1])
    return round(random.uniform(low, high), 2)

# --------------------------------------------------------
# Conexión al broker MQTT local
# --------------------------------------------------------
client = mqtt.Client()
client.connect("localhost", 1883, 60)

# --------------------------------------------------------
# Bucle principal: cada 2 segundos publica todas las lecturas
# --------------------------------------------------------
try:
    while True:
        for topic, sensor_type, unit in SENSORS:
            value = simulate_sensor_value(sensor_type)
            now_cr = datetime.now(tz)

            payload = value
            client.publish(topic, payload)
            print(f"[MQTT] Enviado a {topic}: {payload}")

        time.sleep(2)

except KeyboardInterrupt:
    print("Interrumpido por el usuario, finalizando publicación.")
    client.disconnect()
