import asyncio
import json
import logging
import time
import uuid
from dbm import error
from operator import attrgetter

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
    #broadcast(USERS, users_event())
    if login_success:
        broadcast([websocket], login_event(user))
        broadcast([websocket], old_messages_event())
    else:
        broadcast([websocket], login_failed_event())


def message(event) -> None:
    u = users()
    msg = Message(event["content"], event["user"], time.strftime("%H:%M"))
    messages.append(msg)
    broadcast(users(), messages_event(event))


def init(event, websocket) -> None:
    broadcast([websocket], old_messages_event())
    CLIENTS[websocket.id].username = event["user"]


logging.basicConfig()

#USERS = set()

CLIENTS: dict[uuid.UUID, Client] = {}

#USERS: set = set(map(lambda x: x.websocket, CLIENTS.values()))


def users() -> set:
    global CLIENTS
    res = set(map(lambda x: x.websocket, CLIENTS.values()))
    return res


def matching_users(usernames: list[str]) -> set:
    global CLIENTS
    res = set()
    for k, v in CLIENTS.items():
        if v.username in usernames:
            res.add(v.websocket)
    return res





VALUE = 0

messages: list[Message] = []

accounts: list[User] = []


async def on_message_receive(websocket: ServerConnection) -> None:
    global VALUE, CLIENTS
    try:
        #USERS.add(websocket)
        async for msg in websocket:
            CLIENTS[websocket.id] = Client("", websocket)
            event = json.loads(msg)
            print(websocket.id)
            print(f"before {len(users())} time: {time.time()} action: {event["action"]}")
            if event["action"] == "register":
                registration(event, websocket)

            elif event["action"] == "login":
                login(event, websocket)

            elif event["action"] == "message":
                message(event)

            elif event["action"] == "init":
                init(event, websocket)

            else:
                logging.error("unsupported event: %s", event)
    except:
        print(f"failed to handle the event time: {time.time()}")
    finally:

        del CLIENTS[websocket.id]
        print(f"after {len(users())} time: {time.time()}")


async def main():
    async with serve(on_message_receive, "0.0.0.0", 6789):
        print("serving at port", 6789)
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    print("starting server")
    asyncio.run(main())
