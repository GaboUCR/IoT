FROM python:3.10-alpine

WORKDIR /app

# 1) Instalamos dependencias de compilación
RUN apk add --no-cache --virtual .build-deps \
        build-base \
        linux-headers \
        python3-dev

# 2) Instalamos las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) (Opcional) Eliminamos dependencias de compilación
RUN apk del .build-deps

# 4) Copiamos el código y definimos CMD
COPY . .

ENV DJANGO_SETTINGS_MODULE=iot_ucr.settings.base \
    PYTHONUNBUFFERED=1

CMD ["gunicorn", "iot_ucr.wsgi:application", "--bind", "0.0.0.0:8000"]
