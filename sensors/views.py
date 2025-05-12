# sensors/views/dashboard.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sensors.models import Sensor, SensorReading, Actuator
from django.http       import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  
import json


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
    Devuelve:
    - Última lectura de cada sensor (timestamp en zona local)
    - Valor actual de cada actuador
    """
    sensor_data = []
    for sensor in Sensor.objects.all():
        last = sensor.readings.first()
        if last:
            local_ts = timezone.localtime(last.timestamp)
            ts_iso   = local_ts.isoformat()
            val      = last.value
        else:
            ts_iso = None
            val    = None

        sensor_data.append({
            "id":        sensor.id,
            "name":      sensor.name,
            "value":     val,
            "timestamp": ts_iso,
        })

    actuator_data = []
    for actuator in Actuator.objects.all():
        # Selecciona el campo correcto según el tipo
        if actuator.actuator_type == "texto":
            act_val = actuator.value_text
        else:
            act_val = actuator.value_boolean

        actuator_data.append({
            "id":    actuator.id,
            "name":  actuator.name,
            "type":  actuator.actuator_type,
            "value": act_val,
        })

    return JsonResponse({
        "sensors":   sensor_data,
        "actuators": actuator_data,
    })

@csrf_exempt
@require_POST
@login_required
def update_actuator(request):
    try:
        data = json.loads(request.body)
        actuator_id = data.get("id")
        value = data.get("value")

        actuator = Actuator.objects.get(id=actuator_id)

        if actuator.actuator_type == "binario":
            if not isinstance(value, bool):
                return JsonResponse({"error": "Se esperaba un valor booleano."}, status=400)
            actuator.value_boolean = value

        elif actuator.actuator_type == "texto":
            if not isinstance(value, str):
                return JsonResponse({"error": "Se esperaba un string."}, status=400)
            actuator.value_text = value.strip()

        else:
            return JsonResponse({"error": "Tipo de actuador no soportado."}, status=400)

        actuator.save()
        return JsonResponse({"success": True, "id": actuator.id})

    except Actuator.DoesNotExist:
        return JsonResponse({"error": "Actuador no encontrado."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)