export class WebsocketConnector {

    static #ws = null;
    static websocket(){
        if (WebsocketConnector.#ws == null){
            let url = window.location.hostname === "localhost"
                ? `http://localhost:6789`
                : `wss://api.${window.location.hostname}`;
            WebsocketConnector.#ws = new WebSocket(url);
        }
        return WebsocketConnector.#ws;
    }

    connect() {
        WebsocketConnector.websocket.onopen = function() {
            console.log("Server connection established succesfully")
          WebsocketConnector.websocket.send(JSON.stringify({ action: "connect" }));
        };

        WebsocketConnector.websocket.onclose = function(e) {
          console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
          window.alert("Connection to server lost. Please reload to try again.")
          setTimeout(function() {
            //connect();
          }, 1000);
        };

        WebsocketConnector.websocket.onerror = function(err) {
          console.error('Socket encountered error: ', err.message, 'Closing socket');
          this.ws.close();
        };
    }
}