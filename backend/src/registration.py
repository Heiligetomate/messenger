class Registration:
    def __init__(self, username: str, success_message: str) -> None:
        self.username = username.replace(" ", "")
        self.success_message = success_message
        if len(self.username) < 4:
            self.success_message = "Username to short. Please enter a username with at least 4 characters."
        if len(self.username) > 12:
            self.success_message = "Username to long. Please enter a username with a maximum of 12 characters."

