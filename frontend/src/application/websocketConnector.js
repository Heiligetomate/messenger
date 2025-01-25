export class WebsocketConnector {

    #ws = null;
    websocket(){
        if (this.#ws == null) {
            let url = window.location.hostname === "localhost"
                ? `http://localhost:6789`
                : `wss://api.${window.location.hostname}`;
            console.log("connect to " + url);
            this.#ws = new WebSocket(url);
            this.connect();
        }
        return this.#ws;
    }

    connect() {
        this.websocket().onopen = () => {
            console.log("Server connection established succesfully")
          this.websocket().send(JSON.stringify({ action: "connect" }));
        };

        this.websocket().onclose = (e) => {
          window.alert("Connection to server lost. Please reload to try again.");         
        };

        this.websocket().onerror = (err) =>  {
          console.error('Socket encountered error: ', err.message, 'Closing socket');
          this.websocket().close();
        };
    }
}
