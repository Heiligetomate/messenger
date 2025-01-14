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
from data_base_models import UserAccount
from messenger_repository import MessengerRepository


cnx = MessengerRepository()


def users_event() -> str:
    return json.dumps({"type": "users", "users": len(users())})


def login_event(success: bool, user_name="") -> str:
    if success:
        return json.dumps({"type": "login", "user": user_name, "success": True})
    return json.dumps({"type": "login", "success": False})


def login_failed_event() -> str:
    return json.dumps({"type": "login", "success": False})


def registration_event(user_name, success) -> str:
    return json.dumps({"type": "registration", "user": user_name, "success": success})


def messages_event(event) -> str:
    return json.dumps({"type": "message", "content": event["content"], "user": event["user"], "channel": event["channel"],
                       "timestamp": time.strftime("%H:%M")})


def old_messages_event(message_set, channel_name) -> str:
    json_string = jsonpickle.encode(message_set)
    return json.dumps({"type": "init", "messages": json_string, "channelName": channel_name})


def channel_messages_event(channel) -> str:
    json_string = jsonpickle.encode(channel.messages)
    print(f'channel_messages_event: {json_string})')
    return json.dumps({"type": "channel_messages", "messages": json_string})


def new_channel_event(success, channel_name=None, fail_message="") -> str:
    if success:
        return json.dumps({"type": "new_channel", "success": True, "channelName": channel_name})
    else:
        return json.dumps({"type": "new_channel", "success": False, "failMessage": fail_message})


def join_channel_event(success, channel=None, fail_message="") -> str:
    if success:
        return json.dumps({"type": "join_new_channel", "success": True, "channelName": channel.name})
    else:
        return json.dumps({"type": "join_new_channel", "success": False, "failMessage": fail_message})


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


def registration(event, websocket) -> None:
    user_name = event["user"]
    password = event["password"]
    registration_success = cnx.is_new_user_created(user_name, password)
    broadcast([websocket], registration_event(user_name, registration_success))


def login(event, websocket) -> None:
    user_name = event["user"]
    password = event["password"]

    is_found, user = cnx.is_user_found(user_name)
    if is_found and password == user.password:
        broadcast([websocket], login_event(True, user_name=user_name))
    else:
        broadcast([websocket], login_event(False))

    #for channel in CLIENTS[websocket.id].channels:
    #        broadcast([websocket], old_messages_event(channel.messages, channel.name))
    #else:
    #    broadcast([websocket], login_failed_event())


def message(event) -> None:
    if cnx.is_new_message_created(event["user"], event["content"], channel=event["channel"]):
        user_name: list = cnx.get_all_users_by_channel(event["channel"])
        message_content = messages_event(event)
        broadcast(get_websockets_by_user_name(user_name), message_content)


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


def get_users_with_channel(channel: str) -> list:
    valid_users = []
    for k, v in CLIENTS.items():
        for c in v.channels:
            print(f'channel to compare: {c}')
            if c.name == channel:
                valid_users.append(v.websocket)
    return valid_users


def get_websockets_by_user_name(user_name: list) -> list:
    websockets = []
    for user in user_name:
        for k, v in CLIENTS.items():
            if v.username == user:
                websockets.append(v.websocket)
                break
    return websockets

# def join_channel(event, websocket) -> None:
#    CLIENTS[websocket.id].channels.append(event["channel"])
#    CLIENTS[websocket.id].check_for_double_channels()


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
    join_success = False
    is_found, channel = cnx.is_channel_found(event["channelName"])
    is_user_already_joined = cnx.is_user_in_channel(event["user"], event["channelName"])

    if is_found:
        if channel.is_public:
            join_success = True
        else:
            if channel.password == event["password"]:
                join_success = True
            fail_message = "wrong password"
    if not is_user_already_joined:
        fail_message = "Already joined"
    if join_success:
        broadcast([websocket], join_channel_event(True, channel=event["channelName"]))
    else:
        broadcast([websocket], join_channel_event(False, fail_message=fail_message))


def new_channel(event, websocket) -> None:
    channel_name = event["channelName"]
    channel_password = event["channelPassword"]
    user = event["user"]
    if event["publicPrivate"] == "public":
        cnx.is_new_channel_created(channel_name, channel_password, True)
        cnx.is_joined_channel(channel_name, user)
    else:
        cnx.is_new_channel_created(channel_name, channel_password, False)
        cnx.is_joined_channel(channel_name, user)

    broadcast([websocket], new_channel_event(True, channel_name=channel_name))

VALUE = 0


global_channel = Channel("global", "public")
channels = [global_channel]


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
                CLIENTS[websocket.id] = Client("", websocket, [global_channel])
                print("created new client")
            event = json.loads(msg)
            print(
                f"before {len(users())} | action: {event["action"]} | name: {CLIENTS[websocket.id].username} | Clients: "
                f"{user_names()} ")

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
