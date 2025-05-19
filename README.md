
## 🛰️ Topología MQTT y Estructura de Tópicos

Este proyecto utiliza el protocolo **MQTT** para la recolección de datos desde sensores físicos (o simulados) mediante el broker **Mosquitto**.

### 🧭 Convención de Tópicos

Todos los sensores publican datos utilizando la siguiente estructura:

```
sensors/<tipo>/<nombre>
```

Donde:
- `<tipo>`: categoría del sensor (por ejemplo, `temperatura`, `humedad`, `ph`, etc.)
- `<nombre>`: nombre o identificador único del sensor (ej. `lab1`, `plantaA`, `entrada`)

#### 📌 Ejemplos

| Tópico                            | Descripción                             |
|----------------------------------|-----------------------------------------|
| `sensors/temperatura/lab1`       | Sensor de temperatura en el Laboratorio 1 |
| `sensors/humedad/plantaA`        | Sensor de humedad en planta A             |
| `sensors/ph/cultivo1`            | Sensor de pH en cultivo 1                 |
| `sensors/luminosidad/entrada`    | Sensor de luz en zona de entrada          |

---

### 📦 Payload Esperado

Cada mensaje publicado por un sensor debe seguir el formato JSON siguiente:

```json
{
  "value": 23.5,
  "unit": "°C",
  "timestamp": "2025-04-12T16:12:00Z"
}
```

**Campos esperados:**

| Campo     | Tipo   | Descripción                                  |
|-----------|--------|----------------------------------------------|
| `value`   | float  | Valor numérico medido                        |
| `unit`    | string | Unidad de medida (`°C`, `%`, `ppm`, etc.)    |
| `timestamp` | string | Fecha y hora en formato ISO 8601 UTC         |


```bash
    python3 manage.py runserver --settings=iot_ucr.settings.dev
```