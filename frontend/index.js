let currentUser = "";

  function createParagraph(content){
    	let p = document.createElement("p");
    	p.append(content);
        return p;
    }

  function addContent(content, elementId, isOwnMessage){
        let elem = document.getElementById(elementId);
        let p = createParagraph(content)
        let cssClass = isOwnMessage ? "p-left" : "p-right";
        p.classList.add(cssClass);
        elem.append(p)
  }

window.addEventListener("DOMContentLoaded", () => {
  const websocket = new WebSocket("ws://localhost:6789/");


document.querySelector("#confirm-send").addEventListener("click", () => {
  let message = document.getElementById("send-message").value
  let msg = { action: "message", message: message, sender: currentUser };
  if (currentUser !== "" && message !== ""){
    websocket.send(JSON.stringify(msg));
    document.getElementById("send-message").value = "";
  }

});

document.querySelector("#user-confirm").addEventListener("click", () => {
  currentUser = document.getElementById("username").value;
  document.getElementById("username").value = "";
  document.querySelector("#name-box").textContent = "name: " + currentUser;
  websocket.send(JSON.stringify({ action: "username", username: currentUser }));
});


  websocket.onmessage = onMessageReceived;

  function onMessageReceived({data}){
    const event = JSON.parse(data);
    switch (event.type) {
      case "users":
        //const users = `${event.count} user${event.count == 1 ? "" : "s"}`;
        const users = `${event.count} user${event.count == 1 ? "" : "s"}`;
        document.querySelector(".users").textContent = users;
        break;
      case "message":
        console.log(event.sender);
        console.log(currentUser);
        let isSelf = event.sender === currentUser;
        addContent(`${event.sender}(${event.timestamp}) : ${event.message}`, "messages", isSelf);
        break;
      default:
        console.error("unsupported event", event);
    }
  }
});