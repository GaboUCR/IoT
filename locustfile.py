import random
import string
import datetime as dt
import time

from locust import HttpUser, task, between
from bs4 import BeautifulSoup
import itertools

# Lista de topics “oficiales” de sensores en tu sistema
SENSORS = [
    "sensor/temp_int",
    "sensor/temp_ext",
    "sensor/humedad",
    "sensor/co2",
    "sensor/presion",
    "sensor/luz",
    "sensor/movimiento",
    "sensor/agua",
    "sensor/gas",
    "sensor/sonido",
]

# Lista de topics “oficiales” de actuadores en tu sistema
ACTUATOR_TOPICS = [
    "actuador/ventilador",
    "actuador/luz_principal",
    "actuador/bomba_agua",
    "actuador/sirena",
    "actuador/cerradura",
    "actuador/lcd",
    "actuador/push",
    "actuador/hvac",
    "actuador/color",
    "actuador/comando",
]

def rand_str(n=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

class StressUser(HttpUser):
    wait_time = between(2.5, 3)
    _last_big_range = 0
    _big_range_interval = 30 * 60  # 30 minutos
    _user_counter = itertools.count(1)

    def on_start(self):
        # — LOGIN —
        idx = next(StressUser._user_counter)
        user = f"test{idx}"
        passwd = "konoha.12"

        # GET form + CSRF
        login_page = self.client.get("/accounts/login/", name="GET /accounts/login/")
        soup = BeautifulSoup(login_page.text, "html.parser")
        token_tag = soup.find("input", {"name": "csrfmiddlewaretoken"})
        csrftoken = token_tag["value"] if token_tag else None

        # POST credenciales
        payload = {"username": user, "password": passwd}
        headers = {}
        if csrftoken:
            payload["csrfmiddlewaretoken"] = csrftoken
            headers["X-CSRFToken"] = csrftoken
            headers["Referer"] = "/accounts/login/"

        resp = self.client.post(
            "/accounts/login/",
            data=payload,
            headers=headers,
            allow_redirects=True,
            name="POST /accounts/login/"
        )
        if resp.status_code not in (200, 302):
            raise RuntimeError(f"Login failed for {user}: {resp.status_code}")

        # Crear 5 sensores y 5 actuadores iniciales
        for _ in range(5): self._create_sensor_initial()
        for _ in range(5): self._create_actuator_initial()

        # Refrescar catálogo
        self._refresh_catalog()

    def _create_sensor_initial(self):
        topic = random.choice(SENSORS)
        r = self.client.get("/sensors/new/", name="GET /sensors/new/")
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        payload = {
            "csrfmiddlewaretoken": token,
            "name": f"StressSensor-{rand_str(4)}",
            "sensor_type": random.choice(["temperatura","humedad","gas"]),
            "unit": random.choice(["°C","%","ppm"]),
            "topic": topic,
        }
        self.client.post(
            "/sensors/new/",
            data=payload,
            headers={"X-CSRFToken": token, "Referer": "/sensors/new/"},
            allow_redirects=False,
            name="POST /sensors/new/"
        )

    def _create_actuator_initial(self):
        topic = random.choice(ACTUATOR_TOPICS)
        r = self.client.get("/actuators/new/", name="GET /actuators/new/")
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        act_type = random.choice(["binario","texto"])
        payload = {
            "csrfmiddlewaretoken": token,
            "name": f"StressActuator-{rand_str(4)}",
            "actuator_type": act_type,
            "topic": topic,
        }
        self.client.post(
            "/actuators/new/",
            data=payload,
            headers={"X-CSRFToken": token, "Referer": "/actuators/new/"},
            allow_redirects=False,
            name="POST /actuators/new/"
        )

    def _refresh_catalog(self):
        r = self.client.get("/api/latest-readings/", name="GET /api/latest-readings/")
        data = r.json()
        self.sensor_ids   = [s["id"] for s in data["sensors"]]
        self.actuator_ids = [a["id"] for a in data["actuators"]]

    @task(5)
    def latest_readings(self):
        # agrupado por nombre fijo
        self.client.get("/api/latest-readings/", name="GET /api/latest-readings/")

    @task(1)
    def delete_and_subscribe_sensor(self):
        # DELETE sensor aleatorio
        if not self.sensor_ids:
            return
        sid = random.choice(self.sensor_ids)
        resp = self.client.post(
            f"/api/sensors/{sid}/delete/",
            name="POST /api/sensors/:id/delete/"
        )
        if resp.status_code == 200:
            self.sensor_ids.remove(sid)

        # POST nuevo sensor
        topic = random.choice(SENSORS)
        r = self.client.get("/sensors/new/", name="GET /sensors/new/")
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        payload = {
            "csrfmiddlewaretoken": token,
            "name": f"Stress-{rand_str(4)}",
            "sensor_type": random.choice(["temperatura","humedad","gas"]),
            "unit": random.choice(["°C","%","ppm"]),
            "topic": topic,
        }
        post = self.client.post(
            "/sensors/new/",
            data=payload,
            headers={"X-CSRFToken": token, "Referer": "/sensors/new/"},
            allow_redirects=False,
            name="POST /sensors/new/"
        )
        if post.status_code in (301, 302):
            self._refresh_catalog()

    @task(2)
    def update_actuator(self):
        if not self.actuator_ids:
            return
        aid = random.choice(self.actuator_ids)
        if random.random() < 0.5:
            val = random.choice([True, False])
        else:
            val = f"MSG-{rand_str(3)}"
        self.client.post(
            "/api/update-actuator/",
            json={"id": aid, "value": val},
            name="POST /api/update-actuator/"
        )

    @task(1)
    def delete_and_subscribe_actuator(self):
        if not self.actuator_ids:
            return
        aid = random.choice(self.actuator_ids)
        resp = self.client.post(
            f"/api/actuators/{aid}/delete/",
            name="POST /api/actuators/:id/delete/"
        )
        if resp.status_code == 200:
            self.actuator_ids.remove(aid)

        topic = random.choice(ACTUATOR_TOPICS)
        r = self.client.get("/actuators/new/", name="GET /actuators/new/")
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        act_type = random.choice(["binario","texto"])
        payload = {
            "csrfmiddlewaretoken": token,
            "name": f"ActuatorStress-{rand_str(4)}",
            "actuator_type": act_type,
            "topic": topic,
        }
        post = self.client.post(
            "/actuators/new/",
            data=payload,
            headers={"X-CSRFToken": token, "Referer": "/actuators/new/"},
            allow_redirects=False,
            name="POST /actuators/new/"
        )
        if post.status_code in (301, 302):
            self._refresh_catalog()

    @task
    def maybe_big_sensor_range(self):
        now = time.time()
        if now - self._last_big_range < self._big_range_interval:
            return
        self._last_big_range = now
        if not self.sensor_ids:
            return
        sid = random.choice(self.sensor_ids)
        to_dt = dt.datetime.utcnow()
        from_dt = to_dt - dt.timedelta(days=7)
        self.client.get(
            "/api/sensor-readings/",
            params={
                "sensor_id": sid,
                "from": from_dt.isoformat(),
                "to":   to_dt.isoformat(),
                "buckets": 1000
            },
            name="GET /api/sensor-readings/"
        )
