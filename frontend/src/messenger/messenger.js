import { getFromStorage } from "../shared.js";

function createParagraph(content){
  let p = document.createElement("p");
  p.append(content);
    return p;
}

function addContent(content, elementId, isOwnMessage){
   let elem = document.getElementById(elementId);
   let p = createParagraph(content)
   let cssClass = isOwnMessage ?  "p-right" : "p-left";
   p.classList.add(cssClass);
   elem.append(p)
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
  let publicPrivate =  document.querySelector('input[name="public-private"]:checked').value;
  console.log(channelName, channelPassword, publicPrivate)
  websocket.send(JSON.stringify( {action: "new-channel", channelName: channelName, channelPassword:channelPassword, publicPrivate: publicPrivate} ))
});

document.querySelector("#channel-select").addEventListener('change', () => {
  let channel = document.getElementById("channel-select").value;
  currentChannel = channel;
  websocket.send(JSON.stringify( {action: "select-channel", channel: channel, currentChannel: currentChannel} )); //joa wa Keule guck mal an und vergiss nicht
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
  websocket.send(JSON.stringify({ action: "join-new-channel", channelName: channelName, channelPassword: channelPassword } ));
});


websocket.onmessage = onMessageReceived;

function onMessageReceived({data}){
  const event = JSON.parse(data);
  console.log(event.type)
  switch (event.type) {

    case "users":
      const users = `${event.users} user${event.users === 1 ? "" : "s"}`;
      document.querySelector(".users").textContent = users;
      break;

    case "message":
      let isOwn = event.user === currentUser;
      console.log(event)
      addContent(`${event.user}(${event.timestamp}) : ${event.content}`, "messages", isOwn);
      //scrollToBottom("messages", "message-container");
      break;

    case "init":
      document.getElementById("messages").innerHTML = "";
      createNewOption("channel-select", event.channelName)
      break;

    case "channel_messages":
      deleteMessages("messages")
      const message_array = JSON.parse(event.messages)
      console.log(message_array)
      message_array.forEach((item, _) => {
        let isOwn = item.user === currentUser;
        addContent(`${item.user}(${item.timestamp}) : ${item.content}`, "messages", isOwn);
      });
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