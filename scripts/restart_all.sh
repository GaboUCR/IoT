#!/bin/bash
# Reinicia todos los servicios del sistema relacionados con la aplicación IoT

echo "🔄 Reiniciando servicios IoT…"

SERVICES=(
    iot-web.service
    iot-mqtt-subscriber.service
    iot-mqtt-publisher.service
)

for svc in "${SERVICES[@]}"; do
    echo "➡️  Reiniciando $svc"
    sudo systemctl restart "$svc"

    if systemctl is-active --quiet "$svc"; then
        echo "✅ $svc está activo"
    else
        echo "❌ Error al reiniciar $svc"
    fi
done

echo "✅ Todos los servicios han sido reiniciados."
