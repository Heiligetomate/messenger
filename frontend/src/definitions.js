export class EventDefinitions{
    static onChatMessageSend = "message"
    static onChatMessageReceived = "message"

    static onUserRegisterResult = "registration"
    static sendUserRegisterRequest = "register"

    static onChannelJoinResult = "join_new_channel"
    static sendChannelJoinRequest = "join-new-channel"

    static onChannelCreateResult = "new_channel"
    static sendChannelCreateRequest = "new-channel"

    static onInitReceive = "init"
    static sendInitRequest = "init"

    static onMessageDeleteResult = "delete_message"
    static sendMessageDeleteRequest = "delete-message"

    static onUserLoginResult = "login"
    static sendUserLoginRequest = "login"

    static onChannelMessageReceived = "channel_messages"
    static sendChannelChange = "select-channel"
}
