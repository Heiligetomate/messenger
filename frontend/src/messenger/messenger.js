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
  websocket.onopen = () => websocket.send(JSON.stringify({ action: "init"}));

  let currentUser = getFromStorage(1)
  changeUserDisplay(currentUser);


document.querySelector("#confirm-send").addEventListener("click", () => {
  let message = document.getElementById("send-message").value
  let msg = { action: "message", content: message, user: currentUser };
  if (currentUser.trim() !== "" && message !== ""){
    websocket.send(JSON.stringify(msg));
    document.getElementById("send-message").value = "";
  }

});

document.querySelector('#send-message').addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    let content = document.getElementById("send-message").value;
    let msg = {action: "message", content: content, user: currentUser};
    if (currentUser.trim() !== "" && content !== "") {
      websocket.send(JSON.stringify(msg));
      document.getElementById("send-message").value = "";
    }
  }
});

websocket.onmessage = onMessageReceived;

function onMessageReceived({data}){
  const event = JSON.parse(data);
  switch (event.type) {

    case "users":
      const users = `${event.users} user${event.users === 1 ? "" : "s"}`;
      document.querySelector(".users").textContent = users;
      break;

    case "message":
      let isSelf = event.user === currentUser;
      addContent(`${event.user}(${event.timestamp}) : ${event.content}`, "messages", isSelf);
      //scrollToBottom("messages", "message-container");
      break;

    case "init":
      document.getElementById("messages").innerHTML = "";
      const jsonArray = JSON.parse(event.messages);
      jsonArray.forEach((item, _) => {
        let isOwn = item.user === currentUser;
        addContent(`${item.user}(${item.timestamp}) : ${item.content}`, "messages", isOwn);
      });
      break;


    default:
      console.error("unsupported event", event);
  }
}
});