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


def users_event() -> str:
    return json.dumps({"type": "users", "users": len(users())})


def login_event(username: str) -> str:
    return json.dumps({"type": "login", "user": username, "success": True})


def login_failed_event() -> str:
    return json.dumps({"type": "login", "success": False})


def registration_event(user_registration: Registration) -> str:
    json_string = jsonpickle.encode(user_registration)
    return json.dumps({"type": "registration", "registration": json_string})


def messages_event(event) -> str:
    return json.dumps({"type": "message", "content": event["content"], "user": event["user"],
                       "timestamp": time.strftime("%H:%M")})


def old_messages_event() -> str:
    json_string = jsonpickle.encode(messages)
    return json.dumps({"type": "init", "messages": json_string})


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
        broadcast([websocket], old_messages_event())
    else:
        broadcast([websocket], login_failed_event())


def message(event) -> None:
    channel = event["channel"]
    message_content = messages_event(event)
    broadcast(get_user_with_channel(channel), message_content)
    msg = Message(event["content"], event["user"], time.strftime("%H:%M"))
    messages.append(msg)


def init(event, websocket) -> None:
    broadcast([websocket], old_messages_event())
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


def get_user_with_channel(channel: str) -> list:
    valid_users = []
    for k, v in CLIENTS.items():
        for n in v.channels:
            if n == channel:
                valid_users.append(v.websocket)
    return valid_users


def join_channel(event, websocket) -> None:
    CLIENTS[websocket.id].channels.append(event["channel"])
    CLIENTS[websocket.id].check_for_double_channels()


# def matching_users(usernames: list[str]) -> set:
#    global CLIENTS
#    res = set()
#    for k, v in CLIENTS.items():
#        if v.username in usernames:
#            res.add(v.websocket)
#    return res


VALUE = 0

messages: list[Message] = []

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
                CLIENTS[websocket.id] = Client("", websocket, [])
                print("created new client")
            event = json.loads(msg)
            print(
                f"before {len(users())} | action: {event["action"]} | name: {CLIENTS[websocket.id].username} | Clients: {user_names()}")
            if event["action"] == "register":
                registration(event, websocket)

            elif event["action"] == "login":
                login(event, websocket)

            elif event["action"] == "message":
                message(event)

            elif event["action"] == "init":
                init(event, websocket)

            elif event["action"] == "join-channel":
                join_channel(event, websocket)

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
