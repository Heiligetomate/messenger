import asyncio
import time
import keyboard

from websockets.asyncio.client import connect


async def hello():
    uri = "ws://localhost:8765"
    async with connect(uri) as websocket:
        print("get message")
        greeting = await websocket.recv()
        await asyncio.sleep(1)
        if len(greeting) != 0:
            print(f"<<< {greeting}")
            #if keyboard.read_key() == "x":
               # break



if __name__ == "__main__":
    asyncio.run(hello())
