//import { getFromStorage, save } from "shared";

import {save} from "./application/shared.js";
import {WebsocketConnector} from "./application/websocketConnector.js";
import {EventDefinitions} from "./definitions.js";

const messengerUrl = "/messenger/messenger.html"
let currentUrl = "index.html";
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
    let message = getUserAndPassword(ws, EventDefinitions.sendUserLoginRequest, "login-name", "login-password");
    ws.send(message);
});

document.getElementById("confirm-register").addEventListener("click", () => {
    let message = getUserAndPassword(ws, EventDefinitions.sendUserRegisterRequest, "register-name", "register-password");
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

      case EventDefinitions.onUserRegisterResult:
        if (event.is_success === true){
            window.alert("Created new account successfully")
        }
        else {
            window.alert("Could not create new account")
        }
        break;

      case EventDefinitions.onUserLoginResult:
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
