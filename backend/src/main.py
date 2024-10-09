#!/usr/bin/env python

import asyncio
import json
import logging
import time
import jsonpickle

from websockets.asyncio.server import broadcast, serve
from message import Message

logging.basicConfig()

USERS = set()

VALUE = 0

messages = []


def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})


def messages_event(event):
    return json.dumps({"type": "message", "content": event["content"], "user": event["user"],
                       "timestamp": time.strftime("%H:%M")})


def old_messages_event():
    json_string = jsonpickle.encode(messages)
    print(json_string)
    return json.dumps({"type": "init", "messages": json_string})


async def counter(websocket):
    global USERS, VALUE
    try:
        USERS.add(websocket)
        broadcast(USERS, users_event())
        async for message in websocket:
            event = json.loads(message)
            if event["action"] == "user":
                print(f"new login: {event['user']}")
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
        broadcast(USERS, users_event())


async def main():
    async with serve(counter, "0.0.0.0", 6789):
        print("serving at port", 6789)
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == "__main__":
    print("starting server")
    asyncio.run(main())