from managers.web_socket_manager import WebSocketManager


class UnityManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.processing_buildings = set()
