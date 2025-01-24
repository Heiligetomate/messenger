import { Message } from "./message.js";
import { Channel } from "./channel.js";


export class Cache {
  constructor(username) {
    this.username = username;
    this.messages = [];
    this.available_channels = []
    this.currentChannel = "global"
  }

  switchChannel(channel){
    this.currentChannel = channel;
  }

  getMessages(){
    return this.messages;
  }

  addMessage(rawMessages){
    let msg = new Message(rawMessages, this.username);
    this.messages.push(msg)
    return msg;
  }

  deleteAllMessagesInCurrentChannel(){
    let keepMessages = []
    this.messages.forEach(m => {
      if (!m.channel_id === this.currentChannel){
        keepMessages.push(m)
      }
    })
    this.messages = keepMessages;
  }

  addChannel(channelName){
    let channel = new Channel(channelName);
    this.available_channels.push(channel);
  }

  initMessages(rawMessages){
    for (let i = 0; i < rawMessages.length; i++) {
      let msg = new Message(rawMessages[i], this.username);
      this.messages.push(msg);
    }
  }

  isUserInChannel(channelName) {
    for (let i = 0; i < this.available_channels.length; i++) {
      console.log(this.available_channels[i])
      console.log(this.available_channels[i].name)
      if (this.available_channels[i].name === channelName) {
        return true
      }
    }
    return false
  }

  delete_message_by_id(message_id){
    for (let i = 0; i < this.messages.length; i++) {
      if (this.messages[i].id === message_id){
        this.messages.splice(i, 1);
        console.log("DELETED")
      }
  }
}}