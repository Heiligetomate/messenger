import asyncio
import json
import logging
import time
import jsonpickle

from websockets.asyncio.server import broadcast, serve
from message import Message
from user_account import User
from registration import Registration


def users_event() -> str:
    return json.dumps({"type": "users", "users": len(USERS)})


def login_event(username: str) -> str:
    return json.dumps({"type": "login", "user": username, "success": True})


def login_failed_event() -> str:
    return json.dumps({"type": "login", "success": False})


def registration_event(registration: Registration) -> str:
    json_string = jsonpickle.encode(registration)
    return json.dumps({"type": "registration", "registration": json_string})


def messages_event(event) -> str:
    return json.dumps({"type": "message", "content": event["content"], "user": event["user"],
                       "timestamp": time.strftime("%H:%M")})


def old_messages_event() -> str:
    json_string = jsonpickle.encode(messages)
    print(json_string)
    return json.dumps({"type": "init", "messages": json_string})


logging.basicConfig()

USERS = set()

VALUE = 0

messages: list[Message] = []

accounts: list[User] = []


async def counter(websocket):
    global USERS, VALUE
    try:
        USERS.add(websocket)
        async for message in websocket:
            event = json.loads(message)
            if event["action"] == "register":
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
                registration = Registration(user.username, success_message)
                broadcast([websocket], registration_event(registration))

            elif event["action"] == "login":
                username = event["user"]
                password = event["password"]
                login_success = False
                for account in accounts:
                    if account.username == username and account.password == password:
                        login_success = True
                        break
                broadcast(USERS, users_event())
                if login_success:
                    broadcast([websocket], login_event(username))
                    broadcast([websocket], old_messages_event())
                else:
                    broadcast([websocket], login_failed_event())

            elif event["action"] == "message":
                message = Message(event["content"], event["user"], time.strftime("%H:%M"))
                messages.append(message)
                broadcast(USERS, messages_event(event))
            elif event["action"] == "init":
                broadcast([websocket], old_messages_event())
            else:
                logging.error("unsupported event: %s", event)
    finally:
        # Unregister user
        USERS.remove(websocket)
        #broadcast(USERS, users_event())


async def main():
    async with serve(counter, "0.0.0.0", 6789):
        print("serving at port", 6789)
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == "__main__":
    print("starting server")
    asyncio.run(main())
