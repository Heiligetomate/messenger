import datetime
import uuid
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


@dataclass
class Message:
    id: uuid.UUID
    content: str
    sender_fk: str
    time_stamp: datetime.datetime
    channel_id: str

