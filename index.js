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


  //websocket.onmessage = ({ data }) => {
  //  const event = JSON.parse(data);
  //  switch (event.type) {
  //    case "value":
  //      document.querySelector(".value").textContent = event.value;
  //      break;
  //    case "users":
  //      const users = `${event.count} user${event.count == 1 ? "" : "s"}`;
  //      document.querySelector(".users").textContent = users;
  //      break;
  //    default:
  //      console.error("unsupported event", event);
  //  }
  //};

  //websocket.onmessage = (x) => onMessageReceiced(x, "hello");
  websocket.onmessage = (x) => onMessageReceiced(x);
  websocket.onmessage = onMessageReceiced;

  function onMessageReceiced({data}){
    const event = JSON.parse(data);
    switch (event.type) {
      case "value":
        document.querySelector(".value").textContent = event.value + "hello";
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