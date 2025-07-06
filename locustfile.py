import random
import string
import datetime as dt
import time

from locust import HttpUser, task, between
from bs4 import BeautifulSoup
import itertools

BASE = "https://iotlab201.eie.ucr.ac.cr"

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
        passwd = "contraseña"
        login_path = "/accounts/login/"
        login_url = BASE + login_path

        # GET form + CSRF
        resp_page = self.client.get(login_url, name="GET /accounts/login/")
        soup = BeautifulSoup(resp_page.text, "html.parser")
        token_tag = soup.find("input", {"name": "csrfmiddlewaretoken"})
        csrftoken = token_tag["value"] if token_tag else None

        # POST credenciales
        payload = {"username": user, "password": passwd}
        headers = {}
        if csrftoken:
            payload["csrfmiddlewaretoken"] = csrftoken
            headers["X-CSRFToken"] = csrftoken
            headers["Referer"] = login_url

        resp = self.client.post(
            login_url,
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
        path = "/sensors/new/"
        url = BASE + path
        r = self.client.get(url, name="GET /sensors/new/")
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        payload = {
            "csrfmiddlewaretoken": token,
            "name": f"StressSensor-{rand_str(4)}",
            "sensor_type": random.choice(["temperatura","humedad","gas"]),
            "unit": random.choice(["°C","%","ppm"]),
            "topic": random.choice(SENSORS),
        }
        self.client.post(
            url,
            data=payload,
            headers={"X-CSRFToken": token, "Referer": url},
            allow_redirects=False,
            name="POST /sensors/new/"
        )

    def _create_actuator_initial(self):
        path = "/actuators/new/"
        url = BASE + path
        r = self.client.get(url, name="GET /actuators/new/")
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        payload = {
            "csrfmiddlewaretoken": token,
            "name": f"StressActuator-{rand_str(4)}",
            "actuator_type": random.choice(["binario","texto"]),
            "topic": random.choice(ACTUATOR_TOPICS),
        }
        self.client.post(
            url,
            data=payload,
            headers={"X-CSRFToken": token, "Referer": url},
            allow_redirects=False,
            name="POST /actuators/new/"
        )

    def _refresh_catalog(self):
        api_url = BASE + "/api/latest-readings/"
        r = self.client.get(api_url, name="GET /api/latest-readings/")
        data = r.json()
        self.sensor_ids   = [s["id"] for s in data["sensors"]]
        self.actuator_ids = [a["id"] for a in data["actuators"]]
        self.text_actuator_ids = [a["id"] for a in data["actuators"] if a.get("type") == "texto"]

    @task(5)
    def latest_readings(self):
        url = BASE + "/api/latest-readings/"
        self.client.get(url, name="GET /api/latest-readings/")

    @task(1)
    def delete_and_subscribe_sensor(self):
        if not self.sensor_ids:
            return
        sid = random.choice(self.sensor_ids)
        self.client.post(
            BASE + f"/api/sensors/{sid}/delete/",
            name="POST /api/sensors/:id/delete/"
        )
        self.sensor_ids.remove(sid)
        # Crear nuevo sensor
        self._create_sensor_initial()
        self._refresh_catalog()

    @task(2)
    def update_actuator(self):
        if not self.actuator_ids:
            return
        aid = random.choice(self.actuator_ids)
        val = random.choice([True, False, f"MSG-{rand_str(3)}"])
        self.client.post(
            BASE + "/api/update-actuator/",
            json={"id": aid, "value": val},
            name="POST /api/update-actuator/"
        )

    @task(1)
    def delete_and_subscribe_actuator(self):
        if not self.actuator_ids:
            return
        aid = random.choice(self.actuator_ids)
        self.client.post(
            BASE + f"/api/actuators/{aid}/delete/",
            name="POST /api/actuators/:id/delete/"
        )
        self.actuator_ids.remove(aid)
        self._create_actuator_initial()
        self._refresh_catalog()

    @task(1)
    def toggle_store_readings(self):
        if not self.sensor_ids:
            return
        sid = random.choice(self.sensor_ids)
        new_store = random.choice([True, False])
        path = f"/api/sensors/{sid}/store/"
        url = BASE + path
        csrftoken = self.client.cookies.get("csrftoken", "")
        headers = {"X-CSRFToken": csrftoken, "Referer": BASE + "/dashboard/"}
        self.client.post(
            url,
            json={"store": new_store},
            headers=headers,
            name="POST /api/sensors/:id/store/"
        )

    @task(1)
    def send_text_command(self):
        if not getattr(self, "text_actuator_ids", []):
            return
        aid = random.choice(self.text_actuator_ids)
        msg = f"CMD-{rand_str(5)}"
        path = "/api/actuator-text/"
        url = BASE + path
        csrftoken = self.client.cookies.get("csrftoken", "")
        headers = {"X-CSRFToken": csrftoken, "Accept": "application/json", "Content-Type": "application/json", "Referer": BASE + "/dashboard/"}
        self.client.post(
            url,
            json={"id": aid, "message": msg},
            headers=headers,
            name="POST /api/actuator-text/"
        )

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
        params = {"sensor_id": sid, "from": from_dt.isoformat(), "to": to_dt.isoformat(), "buckets": 1000}
        self.client.get(
            BASE + "/api/sensor-readings/",
            params=params,
            name="GET /api/sensor-readings/"
        )
