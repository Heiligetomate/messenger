import jsonpickle
import json
import definitions as df
from messagedto import MessageDto


def send_login_result(success: bool, user_name="") -> str:
    if success:
        return json.dumps({"type": df.SEND_USER_LOGIN_RESULT, "success": True, "user": user_name})
    return json.dumps({"type": df.SEND_USER_LOGIN_RESULT, "success": False})


def send_registration_result(is_success) -> str:
    return json.dumps({"type": df.SEND_USER_REGISTRATION_RESULT, "is_success": is_success})


def send_chat_message(msg: MessageDto) -> str:
    json_message = jsonpickle.encode(msg)
    return json.dumps({"type": df.SEND_CHAT_MESSAGE, "payload": json_message})


def send_init(messages: list[MessageDto], channel_names: list[str]) -> str:
    messages = jsonpickle.encode(messages)
    return json.dumps({"type": df.SEND_INIT, "messages": messages, "channelNames": channel_names})


def send_channel_messages(messages: list[MessageDto]) -> str:
    json_string = jsonpickle.encode(messages)
    return json.dumps({"type": df.SEND_CHANNEL_MESSAGES, "messages": json_string})


def send_new_channel_created_result(success, channel_name=None, fail_message="") -> str:
    if success:
        return json.dumps({"type": df.SEND_CHANNEL_CREATED_RESULT, "success": True, "channelName": channel_name})
    else:
        return json.dumps({"type": df.SEND_CHANNEL_CREATED_RESULT, "success": False, "failMessage": fail_message})


def send_channel_join_result(success, channel_name=None, fail_message="") -> str:
    if success:
        return json.dumps({"type": df.SEND_USER_JOIN_CHANNEL_RESULT, "success": True, "channelName": channel_name})
    else:
        return json.dumps({"type": df.SEND_USER_JOIN_CHANNEL_RESULT, "success": False, "failMessage": fail_message})


def send_delete_message_result(success, message_id):
    return json.dumps({"type": df.SEND_MESSAGE_DELETE_RESULT, "success": success, "message_id": message_id})
