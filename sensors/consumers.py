from channels.generic.websocket import JsonWebsocketConsumer

class SensorConsumer(JsonWebsocketConsumer):
    def connect(self):
        if self.scope["user"].is_authenticated:
            self.group_name = "sensors"
            self.channel_layer.group_add(self.group_name, self.channel_name)
            self.accept()
            print("WS CONNECT:", self.channel_name, "-> se unió al grupo", self.group_name)

        else:
            self.close()

    def disconnect(self, close_code):
        print("WS disconnect:", self.channel_name, "-> se deconecto del grupo: ", self.group_name)

        self.channel_layer.group_discard(self.group_name, self.channel_name)

    def sensor_update(self, event):
        # Este método recibe eventos de group_send
        self.send_json({
            "sensor_id": event["sensor_id"],
            "value":     event["value"],
            "timestamp": event["timestamp"],
        })
        print("WS EVENT sensor_update:", event)

