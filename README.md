### Descripción de la Arquitectura

**Django + Cliente MQTT:**

- Un proceso en segundo plano (un comando de gestión de Django o un trabajador de Celery) se suscribe a temas MQTT.  
- Cuando llega un nuevo mensaje MQTT, se reenvía a Django Channels (consumidor WebSocket).  

**Django Channels (Capa WebSocket):**  

- Maneja conexiones WebSocket en tiempo real con los usuarios.  
- Al recibir un mensaje MQTT, envía el valor actualizado del tema a todos los clientes conectados.  

**Frontend (Cliente WebSocket en JavaScript):**  

- Los usuarios se suscriben a actualizaciones en tiempo real a través de WebSocket.  
- Cuando el servidor envía nuevos mensajes MQTT, la interfaz de usuario se actualiza instantáneamente.


```bash
    python3 manage.py runserver --settings=iot_ucr.settings.dev
```