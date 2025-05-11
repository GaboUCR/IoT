# sensors/views/dashboard.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sensors.models import Sensor, Actuator

@login_required(login_url='login')
def dashboard(request):
    # Consultar todos los sensores y actuadores
    sensors = Sensor.objects.all()
    actuators = Actuator.objects.all()

    return render(request, "sensors/dashboard.html", {
        "sensors": sensors,
        "actuators": actuators
    })
