import { getFromStorage } from "../application/shared.js";
import { Cache } from "../application/cache.js"
import {WebsocketConnector} from "../application/websocketConnector.js";
import {EventDefinitions} from "../definitions.js";


let cache = null;
let ws = WebsocketConnector.websocket();
ws.onmessage = (e) => { onMessageReceived(e); }

ws.onopen = function() {
  let currentUser = getFromStorage(true)
  changeUserDisplay(currentUser);
  console.log(currentUser)
  cache = new Cache(currentUser);
  ws.send(JSON.stringify({ action: EventDefinitions.sendInitRequest, user: currentUser }));
}

document.querySelector("#confirm-send").addEventListener("click", () => {
  let message = document.getElementById("send-message").value
  let msg = { action: EventDefinitions.onChatMessageSend, content: message, user: cache.username, channel: cache.currentChannel};
  if (cache.username.trim() !== "" && message !== ""){
    ws.send(JSON.stringify(msg));
    document.getElementById("send-message").value = "";
  console.log(cache.currentChannel)
}});

document.querySelector('#send-message').addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    let content = document.getElementById("send-message").value;
    let msg = { action: EventDefinitions.onChatMessageSend, content: content, user: cache.username, channel: cache.currentChannel };
    if (cache.username.trim() !== "" && content !== "") {
      ws.send(JSON.stringify(msg));
      document.getElementById("send-message").value = "";
    }
  }
  console.log(cache.currentChannel)
});

document.querySelector("#new-channel").addEventListener("click", () => {
  hideAndDisplay(["messenger"], "channel")
});

document.querySelector("#go-back").addEventListener("click", () => {
  hideAndDisplay(["channel", "join-channel"], "messenger")
});

document.querySelector("#confirm-channel").addEventListener("click", () => {
  let channelName = document.getElementById("channel-name").value;
  let channelPassword = document.getElementById("channel-password").value;
  let isPublic =  document.querySelector('input[name="is-public"]:checked').value === "1";
  ws.send(JSON.stringify( {action: EventDefinitions.sendChannelCreateRequest, channelName: channelName, channelPassword:channelPassword, isPublic: isPublic, user: cache.username} ))
});

document.querySelector("#channel-select").addEventListener('change', () => {
  deleteMessages("messages")
  let currentChannel = document.getElementById("channel-select").value;
  cache.switchChannel(currentChannel);
  if (cache.isUserInChannel(cache.currentChannel)){
    ws.send(JSON.stringify( {action: EventDefinitions.sendChannelChange , currentChannel: cache.currentChannel} ));
  }
  else{
    window.alert("NICE TRY!")
  }
});

document.querySelector("#public-channel").addEventListener("click", () => {
  document.getElementById("channel-password").style.display = "None";
  document.getElementById("channel-password-label").style.display = "None";
});

document.querySelector("#private-channel").addEventListener("click", () => {
  document.getElementById("channel-password").style.display = "Block";
  document.getElementById("channel-password-label").style.display = "Block";
});

document.querySelector("#join-new-channel").addEventListener("click", () => {
  hideAndDisplay(["messenger", "channel"], "join-channel");
});

document.querySelector("#join-channel-go-back").addEventListener("click", () => {
  hideAndDisplay(["channel", "join-channel"], "messenger");
});

document.querySelector("#confirm-join-channel").addEventListener("click", () => {
  let channelName = document.getElementById("join-channel-name").value;
  let channelPassword = document.getElementById("join-channel-password").value;
  ws.send(JSON.stringify({ action: EventDefinitions.sendChannelJoinRequest, channelName: channelName, channelPassword: channelPassword, user: cache.username } ));
});




function instantiateMultipleMessages(messages){
  cache.initMessages(messages)
  cache.getMessages().forEach((m, _) => {
    addMessageElementToDOM(m, "messages", ws)
  });
}


function createParagraph(content){
  let p = document.createElement("p");
  p.append(content);
    return p;
}

function onDeleteMessageButtonClicked(messageId, ws){
  console.log("delete message with id clicked " + messageId)
  ws.send(JSON.stringify({action: EventDefinitions.sendMessageDeleteRequest, messageId: messageId, channel: cache.currentChannel}))
}

function addMessageElementToDOM(message, elementId, ws){
   let elem = document.getElementById(elementId);
   let isOwner = message.isOwner;
   let p = createParagraph(message.concatenatedContent)
  console.log(message.concatenatedContent)
   let cssClass = message.isOwner ?  "p-right" : "p-left";
   p.classList.add(cssClass);
   if (isOwner){
     let container = document.createElement("div");
     let containerCss= "message-container";
     let buttonCss = "message-delete-button"
     let button = document.createElement("button");
     button.onclick = function () {
       onDeleteMessageButtonClicked(message.id, ws) }
     button.classList.add(buttonCss);
     button.append("delete");
     container.classList.add(containerCss);
     container.append(button);
     container.append(p);
     elem.append(container);
   } else {
    elem.append(p)
   }
}

function deleteMessages(elementId) {
    document.getElementById(elementId).innerHTML = ""
    cache.deleteAllMessagesInCurrentChannel();
}

function changeUserDisplay(user){
   document.getElementById("display-username").innerHTML = "logged in as: " + user;
}

function logout(){
  changeUserDisplay("");
  return "";
}

function scrollToBottom(childContainer, parentContainer){
  let child = document.getElementById(childContainer);
  let height = child.clientHeight;
  let parent = document.getElementById(parentContainer);
  console.log(height);
  parent.scrollTo({
  top: height + 500,
  behavior: "smooth",
});
}

function hideAndDisplay(hideElementIds, displayElementId){
  for (const x of hideElementIds){
    document.getElementById(x).style.display = "none";
  }
  document.getElementById(displayElementId).style.display = "block";
}

function createNewOption(selectId, optionValue){
  const option = document.createElement("option");
  let select = document.getElementById(selectId);
  option.value = optionValue;
  option.text = optionValue;
  select.add(option, select.options[-1]);
}

function onMessageReceived({data}) {
  const event = JSON.parse(data);
  console.log(event.type)
  switch (event.type) {

    case "users":
      const users = `${event.users} user${event.users === 1 ? "" : "s"}`; //ahhhhhh das ist müll ab in die tonne
      document.querySelector(".users").textContent = users;
      break;

    case EventDefinitions.onChatMessageReceived:
      console.log("message received in channel: " + event.payload)

      let msg = JSON.parse(event.payload);
      let transformedMessage = cache.addMessage(msg)
      if (transformedMessage.channel_id === cache.currentChannel) {

        console.log("message after parse:" + transformedMessage)
        addMessageElementToDOM(transformedMessage, "messages", ws)
      }
      //scrollToBottom("messages", "message-container");
      break;

    case EventDefinitions.onInitReceive:
      event.channelNames.forEach((item, _) => {
        createNewOption("channel-select", item.channel_fk);
        cache.addChannel(item.channel_fk)
      });

      document.getElementById("messages").innerHTML = "";
      const messages = JSON.parse(event.messages)
      instantiateMultipleMessages(messages)
      break;

    case EventDefinitions.onChannelMessageReceived:
      deleteMessages("messages")
      console.log("channel messages (raw): " + event.messages)
      const message = JSON.parse(event.messages)

      instantiateMultipleMessages(message)
      break;

    case EventDefinitions.onChannelCreateResult: //adasd
      if (event.success === true) {
        createNewOption("channel-select", event.channelName)
        hideAndDisplay(["channel", "join-channel"], "messenger")
        cache.addChannel(event.channelName) //HÄ? er switcht doch nur
      } else {
        window.alert(event.failMessage)
      }
      break;

    case EventDefinitions.onChannelJoinResult:
      if (event.success === true) {
        createNewOption("channel-select", event.channelName)
        hideAndDisplay(["channel", "join-channel"], "messenger")
        cache.addChannel(event.channelName)
      } else {
        window.alert(event.failMessage)
      }
      break;

    case EventDefinitions.onMessageDeleteResult:
      if (event.success) {
        cache.delete_message_by_id(event.message_id);
        document.getElementById("messages").innerHTML = ""
        console.log(cache.messages.length)
        for (let i = 0; i < cache.messages.length; i++) {
          addMessageElementToDOM(cache.messages[i], "messages", ws)
        }
      }
      break;

    default:
      console.error("unsupported event", event);
  }
}