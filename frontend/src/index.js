//import { getFromStorage, save } from "shared";

import {save} from "./application/shared.js";
import {WebsocketConnector} from "./application/websocketConnector.js";

const messengerUrl = "/messenger/messenger.html"
let currentUrl = "index.html";
let wsCnx = new WebsocketConnector();
let ws = WebsocketConnector.websocket();
ws.onmessage = (e) => { onMessageReceived(e); }


document.querySelector("#switch-to-login").addEventListener("click", () => {
    document.getElementById("loginForm").style.display = "block";
    document.getElementById("registerForm").style.display = "none";
})

document.querySelector("#switch-to-register").addEventListener("click", () => {
    document.getElementById("loginForm").style.display = "none";
    document.getElementById("registerForm").style.display = "block";
})


document.getElementById("confirm-login").addEventListener("click", () => {
    let message = getUserAndPassword(ws, "login", "login-name", "login-password");
    ws.send(message);
});

document.getElementById("confirm-register").addEventListener("click", () => {
    let message = getUserAndPassword(ws, "register", "register-name", "register-password");
    ws.send(message);
});


function getUserAndPassword(websocket, action, userId, passwordId){
    let user = document.getElementById(userId).value;
    let password = document.getElementById(passwordId).value;
    console.log(user, password);
    return JSON.stringify({action: action, user: user, password: password});
}

function onMessageReceived({data}){
  console.log(data)
  const event = JSON.parse(data);
  switch (event.type) {

      case "registration":
        const registration = JSON.parse(event.registration);
        window.alert(registration.success_message);
        break;

      case "login":
          console.log(event)
          if (event.success === true){
              save(true, event.user)
              goToRoute(messengerUrl);
          }
          else {
              window.alert("Wrong username or password")
          }
          break;
    default:
      console.error("unsupported event", event);
  }
}

function goToRoute(target){
    let path = window.location.pathname;
    window.location.href = path.replace(currentUrl, target);
}
