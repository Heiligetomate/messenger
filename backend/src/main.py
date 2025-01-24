import asyncio
import json
import logging
import uuid


from websockets.asyncio.server import broadcast, serve, ServerConnection
from client import Client
from messenger_repository import MessengerRepository
import definitions as df
import events


cnx = MessengerRepository()


def registration(event, websocket) -> None:
    user_name = event["user"]
    password = event["password"]
    is_success = cnx.is_new_user_created(user_name, password)
    broadcast([websocket], events.send_registration_result(is_success))


def login(event, websocket) -> None:
    user_name = event["user"]
    password = event["password"]
    print(f'login event send to ws {websocket.id}')
    is_found, user = cnx.is_user_found(user_name)
    if is_found and password == user.password:
        broadcast([websocket], events.send_login_result(True, user_name=user_name))
        print(events.send_login_result(True, user_name=user_name))
    else:
        print("Invalid credentials or username not found")
        broadcast([websocket], events.send_login_result(False))


def message(event) -> None:
    is_created, msg = cnx.is_new_message_created(event["user"], event["content"], chn=event["channel"])
    if is_created:
        print(msg)
        user_name: list = cnx.get_all_users_by_channel(event["channel"])
        message_content = events.send_chat_message(msg)
        broadcast(get_websockets_by_user_name(user_name), message_content)
    else:
        print("Message could not be created")


def init(event, websocket) -> None:
    CLIENTS[websocket.id].username = event["user"]
    valid_channels = cnx.get_all_channels_by_user_name(CLIENTS[websocket.id].username)
    messages = cnx.get_all_messages_by_channel_name("global")
    broadcast([websocket], events.send_init(messages, valid_channels))


def get_websockets_by_user_name(user_name: list) -> list:
    websockets = []
    for user in user_name:
        for k, v in CLIENTS.items():
            if v.username == user:
                websockets.append(v.websocket)
                break
    return websockets


def join_channel(event, websocket) -> None:
    is_found, channel = cnx.is_channel_found(event["currentChannel"])
    if is_found:
        messages = cnx.get_all_messages_by_channel_name(channel.channel_name)
        broadcast([websocket], events.send_channel_messages(messages))


def join_new_channel(event, websocket) -> None:
    channel_name = event["channelName"]
    user = event["user"]
    fail_message = ""
    success = False
    is_found, channel = cnx.is_channel_found(channel_name)
    if is_found and channel.password == event["channelPassword"] and not channel.is_public:
        success = True
    elif is_found and channel.is_public:
        success = True
    elif is_found and channel.password != event["channelPassword"] and not channel.is_public:
        fail_message = "wrong password!"
    else:
        fail_message = "channel does not exist"
    if cnx.is_user_in_channel(user, channel_name):
        success = False
        fail_message = "Already joined!"
    if not cnx.is_user_joined_in_channel(user, channel_name):
        success = False
        fail_message = "Channel does not exist!"

    if success:
        broadcast([websocket], events.send_channel_join_result(True, channel_name=channel_name))
    else:
        broadcast([websocket], events.send_channel_join_result(False, fail_message=fail_message))


def new_channel(event, websocket) -> None:
    channel_name = event["channelName"]
    channel_password = event["channelPassword"]
    user = event["user"]
    is_public = event["isPublic"]
    if cnx.is_new_channel_created(channel_name, channel_password, is_public):
        cnx.is_joined_channel(channel_name, user)
    broadcast([websocket], events.send_new_channel_created_result(True, channel_name=channel_name))


def delete_message(event) -> None:
    message_id = event["messageId"]
    success = cnx.is_message_deleted_by_id(message_id)
    usernames: list = cnx.get_all_users_by_channel(event["channel"])
    websockets = get_websockets_by_user_name(usernames)
    message_event = events.send_delete_message_result(success, message_id)
    broadcast(websockets, message_event)


logging.basicConfig()
CLIENTS: dict[uuid.UUID, Client] = {}


async def on_message_receive(websocket: ServerConnection) -> None:
    global CLIENTS
    try:
        # USERS.add(websocket)
        async for msg in websocket:
            if websocket.id in CLIENTS:
                CLIENTS[websocket.id].websocket = websocket
                print(f'client updated: {websocket.id}')
            else:
                CLIENTS[websocket.id] = Client("", websocket)
                print(f'client added: {websocket.id}')

            event = json.loads(msg)
            action = event["action"]

            if event["action"] == df.ON_CONNECT:
                print("new client connected :-)")

            elif action == df.ON_USER_REGISTER:
                registration(event, websocket)

            elif action == df.ON_USER_LOGIN:
                login(event, websocket)

            elif action == df.ON_CHAT_MESSAGE_RECEIVED:
                message(event)

            elif action == df.ON_INIT_REQUEST_RECEIVED:
                init(event, websocket)

            elif action == df.ON_CURRENT_CHANNEL_CHANGED:
                join_channel(event, websocket)

            elif action == df.ON_CHANNEL_CREATED:
                new_channel(event, websocket)

            elif action == df.ON_CHANNEL_JOINED:
                join_new_channel(event, websocket)

            elif action == df.DELETE_MESSAGE:
                delete_message(event)

            else:
                logging.error("unsupported event: %s", event)

    except Exception as e:
        print(e)

    finally:
        try:
            del CLIENTS[websocket.id]
        except KeyError as e:
            print(f"ERROR: {e}")


async def main():
    async with serve(on_message_receive, "0.0.0.0", 6789):
        print("serving at port", 6789)
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    print("starting server")
    asyncio.run(main())
