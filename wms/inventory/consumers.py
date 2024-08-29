import json
from channels.generic.websocket import WebsocketConsumer
from .views import StatusPageView

class StatusConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = StatusPageView().get_system_performance()
        self.send(text_data=json.dumps(data))