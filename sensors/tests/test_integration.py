from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from sensors.models import Sensor, SensorReading

from datetime import datetime, timedelta
import pytz

class SensorIntegrationTests(TestCase):
    def setUp(self):
        # Usuario autenticado
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

        # Sensor fijo con datos históricos
        self.sensor = Sensor.objects.create(name="Sensor de Prueba", sensor_type="temperatura", unit="°C")
        tz = pytz.timezone("America/Costa_Rica")
        base_time = tz.localize(datetime(2000, 1, 1, 12, 0, 0))

        self.readings = [
            SensorReading.objects.create(sensor=self.sensor, value=20.1, timestamp=base_time),
            SensorReading.objects.create(sensor=self.sensor, value=20.5, timestamp=base_time + timedelta(minutes=30)),
            SensorReading.objects.create(sensor=self.sensor, value=21.0, timestamp=base_time + timedelta(minutes=60)),
        ]

    def test_sensor_readings_endpoint(self):
        # Rango completo
        start = "2000-01-01T12:00:00"
        end   = "2000-01-01T13:00:00"

        url = f"{reverse('sensor_readings_range')}?sensor_id={self.sensor.id}&from={start}&to={end}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data["data"]), 3)
        self.assertEqual(data["sensor"], self.sensor.name)
        self.assertEqual(data["unit"], self.sensor.unit)

        timestamps = [r["timestamp"] for r in data["data"]]
        self.assertTrue(all("2000-01-01T" in ts for ts in timestamps))
