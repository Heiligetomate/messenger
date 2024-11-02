class Message:
    def __init__(self, content, user, timestamp, channel="welcome"):
        self.content = content
        self.user = user
        self.timestamp = timestamp
        self.channel = channel
