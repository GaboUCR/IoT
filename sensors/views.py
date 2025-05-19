# sensors/views/dashboard.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sensors.models import Sensor, SensorReading, Actuator
from django.http       import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  
from django.views.decorators.http import require_GET
from django.utils.dateparse import parse_datetime

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


@require_GET
@login_required
def sensor_readings_range(request):
    """
    Retorna lecturas de un sensor específico en un rango de tiempo.
    Parámetros GET:
      - sensor_id: ID del sensor
      - from: fecha-hora inicio (ISO 8601)
      - to: fecha-hora fin (ISO 8601)
      - buckets (opcional): número máximo de puntos agregados.
    """
    sensor_id = request.GET.get("sensor_id")
    start_str = request.GET.get("from")
    end_str   = request.GET.get("to")
    buckets   = request.GET.get("buckets")

    if not all([sensor_id, start_str, end_str]):
        return JsonResponse({"error": "Parámetros incompletos"}, status=400)

    try:
        start = parse_datetime(start_str)
        end   = parse_datetime(end_str)
        sensor = Sensor.objects.get(id=sensor_id)
    except Sensor.DoesNotExist:
        return JsonResponse({"error": "Sensor no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    qs = sensor.readings.filter(timestamp__range=(start, end)).order_by("timestamp")
    total = qs.count()

    # Si no pedimos buckets, devolvemos TODAS las lecturas
    try:
        n_buckets = int(buckets) if buckets is not None else 0
    except ValueError:
        n_buckets = 0

    if n_buckets and total > n_buckets:
        # calculamos tamaño de cada “trozo”
        step = total / n_buckets
        aggregated = []
        for i in range(n_buckets):
            # índices de slice
            start_idx = int(i * step)
            end_idx = int((i + 1) * step)
            chunk = list(qs[start_idx:end_idx])
            if not chunk:
                continue
            # tomo timestamp “central” y valor promedio
            mid = chunk[len(chunk)//2].timestamp
            avg = sum(r.value for r in chunk) / len(chunk)
            aggregated.append({
                "timestamp": timezone.localtime(mid).isoformat(),
                "value": round(avg, 2),
            })
        data = aggregated
    else:
        # fallback: todas las lecturas
        data = [
            {
                "timestamp": timezone.localtime(r.timestamp).isoformat(),
                "value": r.value
            }
            for r in qs
        ]

    return JsonResponse({
        "sensor": sensor.name,
        "unit":   sensor.unit,
        "data":   data
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