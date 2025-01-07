class Channel:
    def __init__(self, name, public_private, password=""):
        self.name = name
        self.messages = []
        self.password = password
        self.public_private = public_private
