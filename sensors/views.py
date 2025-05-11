# sensors/views/dashboard.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sensors.models import Sensor, SensorReading, Actuator
from django.http       import JsonResponse
from django.utils import timezone

@login_required(login_url='login')
def dashboard(request):
    # Consultar todos los sensores y actuadores
    sensors = Sensor.objects.all()
    actuators = Actuator.objects.all()

    return render(request, "sensors/dashboard.html", {
        "sensors": sensors,
        "actuators": actuators
    })


@login_required
def latest_readings(request):
    """
    Devuelve para cada sensor su última lectura, 
    con el timestamp convertido a la zona horaria local.
    """
    data = []
    for sensor in Sensor.objects.all():
        last = sensor.readings.first()
        if last:
            # Convierte la fecha UTC a la zona local (según TIME_ZONE en settings)
            local_ts = timezone.localtime(last.timestamp)
            ts_iso   = local_ts.isoformat()
            value    = last.value
        else:
            ts_iso = None
            value  = None

        data.append({
            "id":        sensor.id,
            "name":      sensor.name,
            "value":     value,
            "timestamp": ts_iso,
        })

    return JsonResponse({"sensors": data})
