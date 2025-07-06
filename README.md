## Índice

- [📘 Reinicio de servicios IoT](#reinicio-de-servicios-iot)
  - [🛠 Cómo usarlo](#cómo-usarlo)
- [📄 Actualización de la licencia de la aplicación](#actualización-de-la-licencia-de-la-aplicación)
- [Cuenta de Mosquitto](#cuenta-de-mosquitto)
  - [Como cambiar la cuenta de Mosquitto](#como-cambiar-la-cuenta-de-mosquitto)
  - [Reiniciar toda la aplicación](#reiniciar-toda-la-aplicación)
- [Migrar y borrar base de datos](#migrar-y-borrar-base-de-datos)
  - [📄 `wipe_db`](#wipe_db)
    - [Uso](#uso)
  - [💾 `export_to_csv`](#export_to_csv)
    - [Uso básico](#uso-básico)
    - [Opciones](#opciones)
    - [Ejemplo completo](#ejemplo-completo)
- [Volumen de datos por sensor](#volumen-de-datos-por-sensor)
- [Comunicacion Mosquitto → Django](#comunicacion-mosquitto--django)
  - [1. Sensores → Django (subscriber)](#1-sensores-django-subscriber)
  - [2. Django → Actuadores (publisher)](#2-django-actuadores-publisher)
  - [Resumen de flujo](#resumen-de-flujo)


### 📘 Reinicio de servicios IoT

Puedes usar el script `restart_all.sh` ubicado en la carpeta `scripts/` para reiniciar todos los servicios del backend de esta aplicación. Esto es útil luego de cambios en el código, ajustes de configuración o variables de entorno.

#### 🛠 Cómo usarlo

```bash
cd /home/apps/IoT/scripts
chmod +x restart_all.sh     # Solo la primera vez
./restart_all.sh
```

El script reinicia, en este orden:

1. `iot-web.service` – El servidor Gunicorn (interfaz web + API)
2. `iot-mqtt-subscriber.service` – Suscripción a sensores vía MQTT
3. `iot-mqtt-publisher.service` – Publicación de comandos a actuadores

Cada reinicio se valida individualmente y se reporta si hubo errores.

---

> 🔐 **Nota**: Asegúrate de tener privilegios de `sudo` o bien ejecuta con `sudo ./restart_all.sh` si no estás como root.


# 📄 Actualización de la licencia de la aplicación

La aplicación lee el código de licencia de la variable de entorno `SIGNUP_LICENSE_CODE`. Para cambiarla debes:

1. **Editar el fichero de entorno**
   Abre tu archivo `.env` (en `/home/apps/IoT/.env` o donde lo tengas configurado) y modifica la línea:

   ```dotenv
   SIGNUP_LICENSE_CODE=TU_NUEVO_CÓDIGO_DE_LICENCIA
   ```

   Ejemplo completo:

   ```dotenv
   SECRET_KEY=<tu_secret_key_segura>
   ALLOWED_HOSTS=127.0.0.1,localhost
   SIGNUP_LICENSE_CODE=ABCDEF-123456-GHIJKL-789012
   Environment=DJANGO_SETTINGS_MODULE=iot_ucr.settings.prod
   ```

2. **Guardar los cambios**
   Asegúrate de no introducir espacios al final de la línea y de que el fichero tenga permisos de lectura para el usuario que corre el servicio (`iot`).

3. **Reiniciar el servicio web**
   Para que Gunicorn vuelva a cargar las variables de entorno y empiece a usar tu nuevo `SIGNUP_LICENSE_CODE`, ejecuta:

   ```bash
   sudo systemctl restart iot-web.service
   ```

   Esto provoca que:

   * systemd lea de nuevo tu archivo `.env`
   * Gunicorn y Django arranquen con la nueva configuración

4. **Verificar el estado**
   Comprueba que el servicio se levantó correctamente y no hay errores en los logs:

   ```bash
   sudo systemctl status iot-web.service
   journalctl -u iot-web.service --since "1 minute ago"
   ```

# Cuenta de Mosquitto

## Como cambiar la cuenta de Mosquitto

La aplicación **usa una cuenta global** para todas sus conexiones MQTT. Esa cuenta se define en tu fichero de entorno y **no** se crean usuarios adicionales ni en comando ni en cada suscriptor.

1. Abre tu archivo `.env` en la raíz del proyecto y localiza las siguientes variables:

   ```dotenv
   SECRET_KEY=<enter a safe and long password>
   ALLOWED_HOSTS=127.0.0.1,localhost
   SIGNUP_LICENSE_CODE=<enter license code>
   Environment=DJANGO_SETTINGS_MODULE=iot_ucr.settings.prod

   # ← credenciales globales MQTT:
   MQTT_USER=<mqtt user>
   MQTT_PASSWORD=<mqtt pass>
   ```

2. Sustituye `<mqtt user>` y `<mqtt pass>` por el usuario y la contraseña de la cuenta que configuraste en tu broker Mosquitto.

---

## Reiniciar toda la aplicación

Cada vez que modifiques las variables de entorno, debes reiniciar **todo** el stack para que los cambios sean efectivos. Para ello, ejecuta:

```bash
./scripts/restart_all.sh
```

Este script detiene y arranca de nuevo todos los servicios (Django, MQTT subscriber, etc.), recargando las credenciales desde el `.env`.


# Migrar y borrar base de datos
## 📄 `wipe_db`

> **Ruta:** `manage.py wipe_db`
> **Qué hace:**
> Borra **todo** el contenido de la base de datos en una sola operación.
>
> * Sensores
> * Lecturas históricas
> * Actuadores y mensajes

### Uso

```bash
# Desde la raíz del proyecto Django
python manage.py wipe_db
```

Al ejecutarlo verás en pantalla un mensaje de advertencia y se te pedirá que confirmes escribiendo `yes`.

* Si escribes `yes` y presionas Enter, se eliminarán todos los registros.
* Si introduces cualquier otra cosa, la operación se cancelará y nada cambiará.

---

## 💾 `export_to_csv`

> **Ruta:** `manage.py export_to_csv`
> **Qué hace:**
> Genera tres archivos CSV en un directorio (por defecto `./exports/`):
>
> 1. `sensors.csv` — catálogo de sensores
> 2. `sensor_readings.csv` — lecturas históricas (usa el **nombre** del sensor)
> 3. `actuators.csv` — catálogo de actuadores

### Uso básico

```bash
# Exporta a ./exports/ y usa zona UTC
python manage.py export_to_csv
```

### Opciones

* `--outdir DIR`
  Directorio destino donde se guardan los CSV.

  ```bash
  python manage.py export_to_csv --outdir=/ruta/a/mis_datos
  ```
* `--tz ZONA`
  Zona horaria para normalizar los timestamps (por defecto `UTC`).

  ```bash
  python manage.py export_to_csv --tz=America/Costa_Rica
  ```

### Ejemplo completo

```bash
python manage.py export_to_csv \
  --outdir=/home/usuario/backups_iot \
  --tz=America/Costa_Rica
```

Al terminar verás un mensaje “✅ Exportación completa.” y los ficheros `.csv` en la carpeta deseada.


# Volumen de datos por sensor

Suponiendo un polling cada 3 s y que cada lectura ocupa **exactamente 16 bytes** (8 B para el valor + 8 B para la marca de tiempo), tenemos:

| Intervalo          | Nº lecturas $N=\frac{\Delta t}{3\,\mathrm{s}}$ |      Bytes $B=N×16$      | MB ($B/10^6$) |
| ------------------ | :--------------------------------------------: | :----------------------: | :-----------: |
| 1 hora (3600 s)    |                 3600 ÷ 3 = 1200                |    1200×16 = 19 200 B    |   0.0192 MB   |
| 1 día (86 400 s)   |               86 400 ÷ 3 = 28 800              |   28 800×16 = 460 800 B  |   0.4608 MB   |
| 7 días (604 800 s) |              604 800 ÷ 3 = 201 600             | 201 600×16 = 3 225 600 B |   3.2256 MB   |

**Fórmula general (bytes):**

$$
B = \frac{\Delta t}{3\,\mathrm{s}} \times 16
$$

**Y en MB (dividiendo entre $10^6$):**

$$
B_{\rm MB} = \frac{B}{10^6}
$$
# Comunicacion Mosquitto → Django

Para intercambiar datos entre tus dispositivos y el backend de Django utilizamos MQTT de la siguiente manera:

- El **nombre del tópico** se envía en la cabecera del paquete MQTT y Django lo recibe sin que tú tengas que añadirlo al payload.
- El **payload** siempre contiene únicamente el dato en crudo (por ejemplo, un número o una cadena), sin envoltorios JSON ni metadatos.

## 1. Sensores → Django (subscriber)

- **Tópico**: `sensor/<nombre>`  
  Ejemplos: `sensor/temp_int`, `sensor/humedad`, `sensor/agua`
- **Payload**: un entero que represente la lectura (por ejemplo **42**)

Django se suscribe a cada tópico de sensor configurado con `store_readings=True`, extrae el valor del payload y lo almacena en la base de datos junto con la marca de tiempo.

## 2. Django → Actuadores (publisher)

- **Tópico**: `actuador/<nombre>`  
  Ejemplos: `actuador/ventilador`, `actuador/luz_principal`
- **Payload**:  
  - **Binario**: `0` (off) o `1` (on)  
  - **Texto**: cualquier comando libre (por ejemplo `INICIAR` o `Hola Mundo`)

Cuando el estado de un actuador cambia (desde la interfaz web o por lógica interna), Django publica en el tópico correspondiente para que el dispositivo actuador reciba la orden.

### Resumen de flujo

1. **Dispositivo sensor** publica un entero en `sensor/...`.  
2. **Django** recibe el mensaje, identifica el tópico (desde la cabecera MQTT) y guarda la lectura.  
3. Al producirse un cambio de actuador, **Django** publica en `actuador/...`.  
4. **Dispositivo actuador** recibe el mensaje y actúa según el valor (`0/1` o texto).

### Resumen de flujo

1. **Dispositivo sensor**
   Publica **solo** un entero en `sensor/...`.
2. **Servidor Django**
   • Recibe ese entero y lo guarda (si `store_readings=True`).
   • Cuando un actuador cambia, publica en `actuador/...`.
3. **Dispositivo actuador**
   Suscrito a su tópico, recibe `0/1` o texto y actúa en consecuencia.
