class MessageDto:
    def __init__(self, content, user, timestamp, message_id, channel_id):
        self.content = content
        self.user = user
        self.timestamp = timestamp
        self.message_id = message_id
        self.channel_id = channel_id
