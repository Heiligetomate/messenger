import { getFromStorage } from "../shared.js";
import { Cache } from "../cache.js"


let cache = null;


function createParagraph(content){
  let p = document.createElement("p");
  p.append(content);
    return p;
}

function onDeleteMessageButtonClicked(messageId){
  console.log("delete message with id clicked " + messageId)
}

function addMessageElementToDOM(message, elementId){
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
     button.onclick = function(){ onDeleteMessageButtonClicked(message.id) }
     button.classList.add(buttonCss);
     button.append("löschen");
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

let currentChannel = "global";
let dmStatus = false;

window.addEventListener("load", () => {
   let url = window.location.hostname === "localhost"
       ? `http://localhost:6789`
       : `wss://api.${window.location.hostname}`;
  console.log("WebSocket URL:", url);
  let websocket;
  try{
    websocket = new WebSocket(url);
  } catch (e){
    console.log(e);
  }
  let currentUser = getFromStorage(true)
  changeUserDisplay(currentUser);
  console.log(currentUser)
  cache = new Cache(currentUser);
  websocket.onopen = () => websocket.send(JSON.stringify({ action: "init", user: currentUser }));



document.querySelector("#confirm-send").addEventListener("click", () => {
  let message = document.getElementById("send-message").value
  let msg = { action: "message", content: message, user: currentUser, channel: currentChannel};
  if (currentUser.trim() !== "" && message !== ""){
    websocket.send(JSON.stringify(msg));
    document.getElementById("send-message").value = "";
  console.log(currentChannel)
}
});

document.querySelector('#send-message').addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    let content = document.getElementById("send-message").value;
    let msg = { action: "message", content: content, user: currentUser, channel: currentChannel };
    console.log(msg);
    if (currentUser.trim() !== "" && content !== "") {
      websocket.send(JSON.stringify(msg));
      document.getElementById("send-message").value = "";
    }
  }
  console.log(currentChannel)
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
  console.log(channelName, channelPassword, isPublic)
  websocket.send(JSON.stringify( {action: "new-channel", channelName: channelName, channelPassword:channelPassword, isPublic: isPublic, user: currentUser} ))
});

document.querySelector("#channel-select").addEventListener('change', () => {
  currentChannel = document.getElementById("channel-select").value;
  websocket.send(JSON.stringify( {action: "select-channel", channel: currentChannel, currentChannel: currentChannel} )); //joa wa Keule guck mal an und vergiss nicht
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
  websocket.send(JSON.stringify({ action: "join-new-channel", channelName: channelName, channelPassword: channelPassword, user: currentUser } ));
});


websocket.onmessage = onMessageReceived;


function instantiateMultipleMessages(messages){
  cache.initMessages(messages)
  cache.getMessages().forEach((m, _) => {
    console.log(m)
    addMessageElementToDOM(m, "messages")
  });
}

function onMessageReceived({data}){
  const event = JSON.parse(data);
  console.log(event.type)
  switch (event.type) {

    case "users":
      const users = `${event.users} user${event.users === 1 ? "" : "s"}`;
      document.querySelector(".users").textContent = users;
      break;

    case "message":
      //let isOwn = event.user === currentUser;
      console.log(event)
      if (event.channel === currentChannel){
        //addMessageElementToDOM(`${event.user}(${event.timestamp}) : ${event.content}`, "messages", isOwn);
        let message = JSON.parse(event.message);
        addMessageElementToDOM(message, "messages")
      }
      //scrollToBottom("messages", "message-container");
      break;

    case "init":
      console.log(event.channelNames)
      event.channelNames.forEach((item, _) => {
        createNewOption("channel-select", item.channel_fk);
      });
      cache.initChannels(event.channelNames);

      document.getElementById("messages").innerHTML = "";
      console.log("init channel messages " + event)
        console.log(event.messages);
      const messages = JSON.parse(event.messages)
      instantiateMultipleMessages(messages)
      break;

    case "channel_messages":
      deleteMessages("messages")
      const message = JSON.parse(event.message)
        console.log(message);
        console.log([message]);
      instantiateMultipleMessages([message])
      break;

    case "new_channel":
      if (event.success === true){
        createNewOption("channel-select", event.channelName)
        hideAndDisplay(["channel", "join-channel"], "messenger")
      }
      else{
        window.alert(event.failMessage)
      }
      break;

    case "join_new_channel":
      if (event.success === true) {
        createNewOption("channel-select", event.channelName)
        hideAndDisplay(["channel", "join-channel"], "messenger")
      }
      else{
        window.alert(event.failMessage)
      }
      break;

    default:
      console.error("unsupported event", event);
  }
}
});