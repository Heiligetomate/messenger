import asyncio
import json
import logging
import time
import uuid

import jsonpickle

from websockets.asyncio.server import broadcast, serve, ServerConnection
from message import Message
from user_account import User
from registration import Registration
from client import Client
from channel import Channel
from dm_channel import Dm


def users_event() -> str:
    return json.dumps({"type": "users", "users": len(users())})


def login_event(username: str) -> str:
    return json.dumps({"type": "login", "user": username, "success": True})


def login_failed_event() -> str:
    return json.dumps({"type": "login", "success": False})


def registration_event(user_registration: Registration) -> str:
    json_string = jsonpickle.encode(user_registration)
    return json.dumps({"type": "registration", "registration": json_string})


def messages_event(event, channel=None) -> str:
    if not channel == "":
        return json.dumps(
            {"type": "message", "content": event["content"], "user": event["user"], "isDm": False, "channel": channel.name,
             "timestamp": time.strftime("%H:%M")})
    return json.dumps({"type": "message", "content": event["content"], "user": event["user"], "isDm": True, "dmPartner":"s",
                       "timestamp": time.strftime("%H:%M")})


def old_messages_event(message_set, channel_name) -> str:
    json_string = jsonpickle.encode(message_set)
    return json.dumps({"type": "init", "messages": json_string, "channelName": channel_name})


def channel_messages_event(channel) -> str:
    json_string = jsonpickle.encode(channel.messages)
    print(json_string)
    return json.dumps({"type": "channel_messages", "messages": json_string})


def new_channel_event(success, channel=None, fail_message="") -> str:
    if success:
        return json.dumps({"type": "new_channel", "success": True, "channelName": channel.name})
    else:
        return json.dumps({"type": "new_channel", "success": False, "failMessage": fail_message})


def join_channel_event(success, channel=None, fail_message="") -> str:
    if success:
        return json.dumps({"type": "join_new_channel", "success": True, "channelName": channel.name})
    else:
        return json.dumps({"type": "join_new_channel", "success": False, "failMessage": fail_message})


def dm_message_event(success, user_name=None, fail_message="") -> str:
    if success:
        return json.dumps({"type": "new_dm", "success": True, "user": user_name})
    return json.dumps({"type": "new_dm", "success": False, "failMessage": fail_message})


def find_channels(user_channels) -> list[Channel]:
    valid_channels = []
    for channel in channels:
        for u_channel in user_channels:
            if channel.name == u_channel:
                valid_channels.append(channel)
    return valid_channels


def find_channel(channel_name) -> Channel:
    for channel in channels:
        if channel.name == channel_name:
            print(channel, channel_name, channel.name)
            return channel


def find_dm(dms: list):
    for channel in dm_channels:
        if dms[0] in channel.members and dms[1] in channel.members:
            return channel


def registration(event, websocket) -> None:
    user = event["user"]
    registration_success = True
    for account in accounts:
        if account.username.lower() == user.lower():
            registration_success = False
            break
    user = User(event["user"], event["password"])
    if len(event["password"]) < 4:
        registration_success = False
        success_message = "Password must be at least 4 characters long"
    elif registration_success:
        accounts.append(user)
        print(f"new register: {event['user']} password: {event['password']}")
        success_message = f"you created the account {user.username} successfully"
    else:
        success_message = "user already exists"
    new_user = Registration(user.username, success_message)
    broadcast([websocket], registration_event(new_user))


def login(event, websocket) -> None:
    user = event["user"]
    password = event["password"]
    login_success = False
    for account in accounts:
        if account.username.lower() == user.lower() and account.password == password:
            login_success = True
            break
    # broadcast(USERS, users_event())
    if login_success:
        broadcast([websocket], login_event(user))
        for channel in CLIENTS[websocket.id].channels:
            broadcast([websocket], old_messages_event(channel.messages))
    else:
        broadcast([websocket], login_failed_event())


def message(event) -> None:
    if not event["isDm"]:
        channel = find_channel(event["channel"])
        message_content = messages_event(event, channel)
        broadcast(get_us .append(msg)
    else:
        channel = find_dm(event["dmUser"])
        msg = Message(event["content"], event["user"], time.strftime("%H:%M"))
        channel.messages.append(msg)
        broadcast(channel.members, messages_event(event))


def init(event, websocket) -> None:
    valid_channels = find_channels(CLIENTS[websocket.id].channels)
    print(valid_channels)
    for channel in valid_channels:
        print(channel.name)
        broadcast([websocket], old_messages_event(channel.messages, channel.name))
    CLIENTS[websocket.id].username = event["user"]
    print(f"id on init event: {websocket.id}")


def users() -> set:
    global CLIENTS
    res = set(map(lambda x: x.websocket, CLIENTS.values()))
    return res


def user_names() -> set:
    global CLIENTS
    res = set(map(lambda x: x.username, CLIENTS.values()))
    return res


def get_user_with_channel(channel) -> list:
    valid_users = []
    for k, v in CLIENTS.items():
        for n in v.channels:
            if n == channel:
                valid_users.append(v.websocket)
    return valid_users


def get_websocket_with_name(name):
    for k, v in CLIENTS.items():
        if v.username == name:
            return v.websocket
    return None


def join_channel(event, websocket) -> None:
    for channel in channels:
        if channel.name == event["currentChannel"]:
            broadcast([websocket], channel_messages_event(channel))


def join_new_channel(event, websocket) -> None:
    fail_message = "Channel does not exist"
    for channel in channels:
        if channel.name == event["channelName"]:
            if channel.public_private == "public":
                if channel not in CLIENTS[websocket.id].channels:
                    CLIENTS[websocket.id].channels.append(channel)
                    broadcast([websocket], join_channel_event(True, channel=channel))
                    return None
                else:
                    fail_message = "Already joined"
            elif channel.public_private == "private":
                if channel.password == event["channelPassword"]:
                    if channel not in CLIENTS[websocket.id].channels:
                        CLIENTS[websocket.id].channels.append(channel)
                        broadcast([websocket], join_channel_event(True, channel=channel))
                        return None
                    else:
                        fail_message = "Already joined"
                else:
                    fail_message = "Wrong Password"
    broadcast([websocket], join_channel_event(False, fail_message=fail_message))


def new_channel(event, websocket) -> None:
    if len(event["channelName"]) < 3:
        broadcast([websocket], new_channel_event(False, fail_message="Channel name too short"))
        return None
    for channel in channels:
        if channel.name == event["channelName"]:
            broadcast([websocket], new_channel_event(False, fail_message="Channel already exists"))
            return None
    channel = Channel(event["channelName"], event["publicPrivate"], event["channelPassword"])
    channels.append(channel)
    CLIENTS[websocket.id].channels.append(channel)
    broadcast([websocket], new_channel_event(True, channel=channel))
    print("CHANNEL:", channel.name, channel.public_private, channel.password)


def new_dm(event, websocket) -> None:
    dm_user = get_websocket_with_name(event["user"])
    if dm_user is None:
        broadcast([websocket], dm_message_event(False, fail_message="User does not exist"))
        return None
    dm_channel = Dm([dm_user, CLIENTS[websocket.id]], [])
    CLIENTS[websocket.id].dm_channels.append(dm_channel)
    CLIENTS[dm_user.id].dm_channels.append(dm_channel)
    broadcast([websocket], dm_message_event(True, CLIENTS[dm_user.id].username))
    broadcast([dm_user], dm_message_event(True, CLIENTS[websocket.id].username))


VALUE = 0

messages = []

global_channel = Channel("global", "public")
channels = [global_channel]
dm_channels = []

accounts: list[User] = []

logging.basicConfig()
CLIENTS: dict[uuid.UUID, Client] = {}


async def on_message_receive(websocket: ServerConnection) -> None:
    global VALUE, CLIENTS
    try:
        # USERS.add(websocket)
        async for msg in websocket:
            if websocket.id in CLIENTS:
                CLIENTS[websocket.id].websocket = websocket
                print("changed ws")
            else:
                CLIENTS[websocket.id] = Client("", websocket, [global_channel], [])
                print("created new client")
            event = json.loads(msg)
            print(
                f"before {len(users())} | action: {event["action"]} | name: {CLIENTS[websocket.id].username} | Clients: {user_names()} channels:{CLIENTS[websocket.id].channels}")
            if event["action"] == "register":
                registration(event, websocket)

            elif event["action"] == "login":
                login(event, websocket)

            elif event["action"] == "message":
                message(event)

            elif event["action"] == "init":
                init(event, websocket)

            elif event["action"] == "select-channel":
                join_channel(event, websocket)

            elif event["action"] == "new-channel":
                new_channel(event, websocket)

            elif event["action"] == "join-new-channel":
                join_new_channel(event, websocket)

            elif event["action"] == "new-dm":
                new_dm(event, websocket)

            else:
                logging.error("unsupported event: %s", event)

    finally:
        try:
            del CLIENTS[websocket.id]
        except KeyError as e:
            print(f"ERROR: {e}")
        print(f"after {len(users())}")


async def main():
    async with serve(on_message_receive, "0.0.0.0", 6789):
        print("serving at port", 6789)
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    print("starting server")
    asyncio.run(main())
