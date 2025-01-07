from websockets.asyncio.server import ServerConnection


class Client:
    def __init__(self, username: str, websocket: ServerConnection, channels: list, dm_channels):
        self.username = username
        self.websocket = websocket
        self.channels = channels
        self.dm_channels = dm_channels

    def check_for_double_channels(self) -> None:
        unique_channels = []
        for channel in self.channels:
            if channel not in unique_channels:
                unique_channels.append(channel)
        self.channels = unique_channels
