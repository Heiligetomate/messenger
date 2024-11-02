from websockets.asyncio.server import ServerConnection

class Client:
    def __init__(self, username: str, websocket: ServerConnection):
        self.username = username
        self.websocket = websocket
