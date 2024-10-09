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
  let protocol = window.location.protocol === "https:" ? "wss" : "ws";
   let url = window.location.hostname === "localhost"
       ? `${protocol}://localhost:6789/`
       : `${protocol}://${window.location.hostname}:6789/`;
  console.log("WebSocket URL:", url);
  const websocket = new WebSocket(url);



document.querySelector("#confirm-send").addEventListener("click", () => {
  let message = document.getElementById("send-message").value
  let msg = { action: "message", content: message, user: currentUser };
  if (currentUser !== "" && message !== ""){
    websocket.send(JSON.stringify(msg));
    document.getElementById("send-message").value = "";
  }

});

document.querySelector("#user-confirm").addEventListener("click", () => {
  currentUser = document.getElementById("username").value;
  document.getElementById("username").value = "";
  document.querySelector("#name-box").textContent = "name: " + currentUser;
  websocket.send(JSON.stringify({ action: "user", user: currentUser }));
});

document.querySelector("#get-old-messages").addEventListener("click", () => {
  document.getElementById("messages").innerHTML = "";
  websocket.send(JSON.stringify({action: "init"}));
})

  websocket.onmessage = onMessageReceived;

  function onMessageReceived({data}){
    const event = JSON.parse(data);
    switch (event.type) {
      case "users":
        //const users = `${event.count} user${event.count == 1 ? "" : "s"}`;
        const users = `${event.count} user${event.count === 1 ? "" : "s"}`;
        document.querySelector(".users").textContent = users;
        break;
      case "message":
        //console.log(event.sender);
        let isSelf = event.user === currentUser;

        addContent(`${event.user}(${event.timestamp}) : ${event.content}`, "messages", isSelf);
        break;
      case "init":
        const jsonArray = JSON.parse(event.messages);
        jsonArray.forEach((item, _) => {
          let isOwn = item.user === currentUser;
          console.log(isOwn);
          addContent(`${item.user}(${item.timestamp}) : ${item.content}`, "messages", isOwn);

        });
        break;
      default:
        console.error("unsupported event", event);
    }
  }
});