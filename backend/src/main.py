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
    return json.dumps({"type": "message", "message": event["message"], "sender": event["sender"],
                       "timestamp": time.strftime("%H:%M")})


def old_messages_event():
    json_string = jsonpickle.encode(messages)
    print(json_string)
    return json.dumps({"type": "init", "messages": json_string})


async def counter(websocket):
    global USERS, VALUE
    try:
        # Register user
        USERS.add(websocket)
        broadcast(USERS, users_event())
        # Send current state to user
        # await websocket.send(value_event()) FÜR WAS?
        # Manage state changes
        async for message in websocket:
            event = json.loads(message)
            if event["action"] == "username":
                print(f"new login: {event['username']}")
            elif event["action"] == "message":
                #print(f"{event['sender']}: {event['message']}")
                message = Message(event["sender"], event["message"], time.strftime("%H:%M"))
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