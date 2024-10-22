//import { getFromStorage, save } from "shared";

import {save} from "./shared.js";

const messengerUrl = "/messenger/messenger.html"
const currentUrl = "index.html";

function goToRoute(target){
    let path = window.location.pathname;
    window.location.href = path.replace(currentUrl, target);
}


document.querySelector("#switch-to-login").addEventListener("click", () => {
    document.getElementById("loginForm").style.display = "block";
    document.getElementById("registerForm").style.display = "none";
})

document.querySelector("#switch-to-register").addEventListener("click", () => {
    document.getElementById("loginForm").style.display = "none";
    document.getElementById("registerForm").style.display = "block";
})

function getUserAndPassword(websocket, action, userId, passwordId){
    let user = document.getElementById(userId).value;
    let password = document.getElementById(passwordId).value;
    console.log(user, password);
    return JSON.stringify({action: action, user: user, password: password});
}

window.addEventListener("DOMContentLoaded", () => {
    let url = window.location.hostname === "localhost"
        ? `http://localhost:6789`
        : `wss://api.${window.location.hostname}`;
    console.log("WebSocket URL:", url);
    let websocket;
    try {
        websocket = new WebSocket(url);
    } catch (e) {
        console.log(e);
    }

document.getElementById("confirm-login").addEventListener("click", () => {
    websocket.send(getUserAndPassword(websocket, "login", "login-name", "login-password"));
});

document.getElementById("confirm-register").addEventListener("click", () => {
   websocket.send(getUserAndPassword(websocket, "register", "register-name", "register-password"));
});

websocket.onmessage = onMessageReceived;

function onMessageReceived({data}){
  const event = JSON.parse(data);
  switch (event.type) {

      case "registration":
        const registration = JSON.parse(event.registration);
        window.alert(registration.success_message);
        break;

      case "login":
          if (event.success === true){
              save(1, event.user)
              goToRoute(messengerUrl);
          }
          save(true, event.user);
          break;
    default:
      console.error("unsupported event", event);
  }
}});