from dataclasses import dataclass


@dataclass
class UserAccount:
    user_name: str
    password: str


@dataclass
class Channel:
    channel_name: str
    is_public: bool
    password: str


