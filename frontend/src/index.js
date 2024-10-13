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

  function getValueAndDeleteContent(elementId){
    let elementValue = document.getElementById(elementId).value;
    document.getElementById(elementId).value = "";
    return elementValue;
  }


window.addEventListener("DOMContentLoaded", () => {
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
    let message = document.getElementById("send-message").value;
    let msg = {action: "message", content: message, user: currentUser};
    if (currentUser.trim() !== "" && message !== "") {
      websocket.send(JSON.stringify(msg));
      document.getElementById("send-message").value = "";
    }
  }
});



document.querySelector("#confirm-login-or-register").addEventListener("click", () => {
  let usersPassword = getValueAndDeleteContent("password");
  let userLogin = getValueAndDeleteContent("username");
  let loginOrRegister = document.getElementById("login-or-register").value
  if (loginOrRegister === "login"){
    websocket.send(JSON.stringify({ action: "login", user: userLogin, password: usersPassword }));
  }
  else {
    websocket.send(JSON.stringify({ action: "register", user: userLogin, password: usersPassword }));
  }
});

//document.querySelector("#get-old-messages").addEventListener("click", () => {
//  document.getElementById("messages").innerHTML = "";
//  websocket.send(JSON.stringify({action: "init"}));
//  let button = document.getElementById("get-old-messages");
//  button.setAttribute("disabled", "true");
//
//})

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
        break;
      case "init":
        document.getElementById("messages").innerHTML = "";
        const jsonArray = JSON.parse(event.messages);
        jsonArray.forEach((item, _) => {
          let isOwn = item.user === currentUser;
          addContent(`${item.user}(${item.timestamp}) : ${item.content}`, "messages", isOwn);

        });
        break;
      case "login":
        if(event.success === true){
          currentUser = event.user
          document.getElementById("display-username").innerHTML = "logged in as: " + currentUser;
          break;
        }
        window.alert("Wrong login data. Please try again")
        break;

      case "registration":
        const registration = JSON.parse(event.registration);
        window.alert(registration.success_message);
        break;

      default:
        console.error("unsupported event", event);
    }
  }
});