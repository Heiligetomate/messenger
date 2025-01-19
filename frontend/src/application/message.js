export class Message {
  constructor(rawMessage, currentUser) {
    //this.content = rawMessage["content"];
    this.content = rawMessage.content;
    this.timestamp = rawMessage.timestamp;
    this.id = rawMessage.message_id;
    this.owner = rawMessage.user;
    this.channel_id = rawMessage.channel_id;
    this.isOwner = rawMessage.user ===  currentUser;
    this.concatenatedContent = `${rawMessage.user}(${rawMessage.timestamp}) : ${rawMessage.content}`;
  }
}