# sensors/views/dashboard.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard(request):
    # Simulación de sensores disponibles
    sensors = [
        {"id": "temp01", "nombre": "Sensor de Temperatura"},
        {"id": "hum01", "nombre": "Sensor de Humedad"},
        {"id": "volt01", "nombre": "Sensor de Voltaje"},
        {"id": "pres01", "nombre": "Sensor de Presión"},
        {"id": "lux01", "nombre": "Sensor de Luminosidad"},
        {"id": "ph01", "nombre": "Sensor de pH"},
        {"id": "co201", "nombre": "Sensor de CO₂"},
        {"id": "gas01", "nombre": "Sensor de Gas"},
        {"id": "prox01", "nombre": "Sensor de Proximidad"},
        {"id": "t1", "nombre": "planta1"},
        {"id": "t12", "nombre": "planta 1"},
        {"id": "t32", "nombre": "pla"},
        {"id": "t36", "nombre": "Tarjeta de Lectura de Sensor Ambiental con Visualización y Acciones"},
    ]
    actuators = [
        {"id": "light01", "nombre": "Luz Principal", "tipo": "binario"},
        {"id": "ac01",    "nombre": "Aire Acondicionado", "tipo": "texto"},
        {"id": "door01",  "nombre": "Puerta Principal",   "tipo": "binario"},
    ]
    return render(request, "sensors/dashboard.html", {"sensors": sensors, "actuators": actuators})
