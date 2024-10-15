

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

function getValueAndDeleteContent(elementId){
  let elementValue = document.getElementById(elementId).value;
  document.getElementById(elementId).value = "";
  return elementValue;
}

function setCookie(cookieName, cookieValue, expireDays){
  const expireTime = new Date();
  expireTime.setTime(expireTime.getTime() + (expireDays*24*60*60*1000));
  let expireDate = "expires="+ expireTime.toUTCString();
  document.cookie = `${cookieName}=${cookieValue};${expireDate};path=/`
}

function getCookie(name) {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

function changeUserDisplay(user){
   document.getElementById("display-username").innerHTML = "logged in as: " + user;
}

function logout(){
  changeUserDisplay("");
  return "";
}

function deleteCookie(name) {
  setCookie(name, "", {
    'max-age': -1
  })
}

function getUserCookies(){
  let user;
  let password;
  try{
   user = getCookie("user");
   password = getCookie("password");
  } catch (e){
    user = "";
  }
  console.log(user);
  return [user, password];
}

function scrollToBottom(childContainer, parentContainer){
  let child = document.getElementById(childContainer);
  let height = child.clientHeight;
  let parent = document.getElementById(parentContainer);
  console.log(height);
  //scrollBar.scrollTo(0, height);
  parent.scrollTo({
  top: height + 500,
  behavior: "smooth",
});
}

// Global ids



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

  let cookieUser = getUserCookies();
  document.getElementById("username").value = cookieUser[0]
  document.getElementById("password").value = cookieUser[1]


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



document.querySelector("#confirm-login-or-register").addEventListener("click", () => {
  let usersPassword = getValueAndDeleteContent("password");
  let userLogin = getValueAndDeleteContent("username");
  let dropBarAction = document.getElementById("login-or-register").value
  switch (dropBarAction) {

    case "login":
      websocket.send(JSON.stringify({ action: "login", user: userLogin, password: usersPassword }));
      setCookie("user", userLogin, 1);
      setCookie("password", usersPassword, 1);
      break;

    case "register":
      websocket.send(JSON.stringify({ action: "register", user: userLogin, password: usersPassword }));
      break;

    case "logout":
      currentUser = logout();
      document.getElementById("messages").innerHTML = "";
      deleteCookie("user")
      break;

    default:
      console.error("unsupported option", dropBarAction);
  }
});


let currentUser;
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
      scrollToBottom("messages", "message-container")
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
        changeUserDisplay(event.user)
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