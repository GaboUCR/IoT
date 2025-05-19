# sensors/tests.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from datetime import datetime, timedelta
import json

from sensors.models import Sensor, SensorReading, Actuator


class SensorModelsTest(TestCase):
    def test_str(self):
        s = Sensor.objects.create(name="S1", sensor_type="temp", unit="°C")
        self.assertEqual(str(s), "S1 (temp)")

    def test_reading_ordering_and_index(self):
        s = Sensor.objects.create(name="S1", sensor_type="temp", unit="°C")
        now = timezone.now()
        old = SensorReading.objects.create(sensor=s, value=1.0, timestamp=now)
        recent = SensorReading.objects.create(sensor=s, value=2.0, timestamp=now + timezone.timedelta(hours=1))
        # ordering = ['-timestamp']
        readings = list(s.readings.all())
        self.assertEqual(readings, [recent, old])

class ActuatorModelsTest(TestCase):
    def test_str(self):
        a = Actuator.objects.create(name="A1", actuator_type="binario", value_boolean=True)
        self.assertEqual(str(a), "A1 (binario)")

class LatestReadingsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="u", password="p")
        self.client.login(username="u", password="p")
        # sensor + reading
        self.s = Sensor.objects.create(name="S1", sensor_type="temp", unit="°C")
        self.r = SensorReading.objects.create(sensor=self.s, value=5.5, timestamp=timezone.now())
        # actuator
        self.a = Actuator.objects.create(name="A1", actuator_type="binario", value_boolean=False)

    def test_latest_readings_returns_structure(self):
        resp = self.client.get(reverse("latest_readings"))
        data = resp.json()
        self.assertIn("sensors", data)
        self.assertIn("actuators", data)
        self.assertEqual(data["sensors"][0]["value"], 5.5)
        self.assertEqual(data["actuators"][0]["value"], False)

class SensorReadingsRangeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

        self.sensor = Sensor.objects.create(name="Test Sensor", sensor_type="temp", unit="°C")

        # Fecha fija: 1 de enero de 2000, 12:00 PM UTC
        base_time = timezone.make_aware(datetime(2000, 1, 1, 12, 0, 0))

        self.readings = [
            SensorReading.objects.create(sensor=self.sensor, value=20.5, timestamp=base_time - timedelta(minutes=90)),
            SensorReading.objects.create(sensor=self.sensor, value=21.0, timestamp=base_time - timedelta(minutes=60)),
            SensorReading.objects.create(sensor=self.sensor, value=22.0, timestamp=base_time - timedelta(minutes=30)),
        ]
        self.base_time = base_time

    def test_missing_params(self):
        resp = self.client.get(reverse("sensor_readings_range"))
        self.assertEqual(resp.status_code, 400)

    def test_valid_range(self):
        start = (self.base_time - timedelta(hours=2)).isoformat()
        end   = self.base_time.isoformat()

        url = f"{reverse('sensor_readings_range')}?sensor_id={self.sensor.id}&from={start}&to={end}"
        resp = self.client.get(url)
        data = resp.json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(data["data"]), 3)


class UpdateActuatorViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(username="u", password="p")
        self.client.login(username="u", password="p")
        self.a = Actuator.objects.create(name="A1", actuator_type="binario", value_boolean=False)

    def test_update_binario_valid(self):
        resp = self.client.post(
            reverse("update_actuator"),
            json.dumps({"id": self.a.id, "value": True}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.a.refresh_from_db()
        self.assertTrue(self.a.value_boolean)

    def test_update_binario_invalid_type(self):
        resp = self.client.post(
            reverse("update_actuator"),
            json.dumps({"id": self.a.id, "value": "not_bool"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)


class ActuatorUpdateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="admin123")
        self.client.login(username="admin", password="admin123")

        self.binary = Actuator.objects.create(name="Relay", actuator_type="binario", value_boolean=False)
        self.textual = Actuator.objects.create(name="Display", actuator_type="texto", value_text="off")

        self.url = reverse("update_actuator")

    def test_update_binary_actuator_valid(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"id": self.binary.id, "value": True}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.binary.refresh_from_db()
        self.assertTrue(self.binary.value_boolean)

    def test_update_textual_actuator_valid(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"id": self.textual.id, "value": "ON"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.textual.refresh_from_db()
        self.assertEqual(self.textual.value_text, "ON")

    def test_invalid_binary_type(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"id": self.binary.id, "value": "not_bool"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_text_type(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"id": self.textual.id, "value": 123}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_nonexistent_actuator(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"id": 9999, "value": True}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_missing_fields(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"id": self.binary.id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

