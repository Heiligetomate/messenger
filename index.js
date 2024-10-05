window.addEventListener("DOMContentLoaded", () => {
  const websocket = new WebSocket("ws://localhost:6789/");

  document.querySelector(".minus").addEventListener("click", () => {
    let message = { content: "abziehen", timestamp: Date.now() };
    let sendMessage = { action: "minus", user: "icke", message: message };
    let json = JSON.stringify(sendMessage);
    console.log(json);
    websocket.send(json);
  });

  document.querySelector(".plus").addEventListener("click", () => {
    websocket.send(JSON.stringify({ action: "plus" }));
  });

  //document.querySelector("#user-confirm").addEventListener("click", () => {
  //  websocket.send(JSON.stringify({ action: "username" }));
  //});

  document.querySelector("#user-confirm").addEventListener("click", () => {
    let usernameContent = document.getElementById("username").value;
    document.getElementById("username").value = "";
    document.querySelector("#name-box").textContent = "name: " + usernameContent;
    websocket.send(JSON.stringify({ action: "username", username: usernameContent }));
  });


  websocket.onmessage = (x) => onMessageReceived(x);
  websocket.onmessage = onMessageReceived;

  function onMessageReceived({data}){
    const event = JSON.parse(data);
    switch (event.type) {
      case "value":
        document.querySelector(".value").textContent = event.value;
        break;
      case "users":
        //const users = `${event.count} user${event.count == 1 ? "" : "s"}`;
        const users = `${event.count} user${event.count == 1 ? "" : "s"}`;
        document.querySelector(".users").textContent = users;
        break;
      default:
        console.error("unsupported event", event);
    }
  }
});