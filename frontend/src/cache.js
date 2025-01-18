import { Message } from "./message.js";


export class Cache {
  constructor(username) {
    this.username = username;
    this.messages = [];
    this.available_channels = []
  }

  getMessages(){
    return this.messages;
  }

  addMessage(rawMessages){
    let msg = new Message(rawMessages, this.username);
    this.messages.push(msg)
  }

  addChannels(channel){
    this.available_channels.push(channel)
  }

  initMessages(rawMessages){
    for (let i = 0; i < rawMessages.length; i++) {
      let msg = new Message(rawMessages[i], this.username);
      this.messages.push(msg);
    }
  }

  initChannels(channels){
    this.available_channels = channels;
  }
}