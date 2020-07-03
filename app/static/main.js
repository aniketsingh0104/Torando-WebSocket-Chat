// Create a new Websocket
var APP = {
    wsURL: 'ws://' + window.location.host + '/ws',   // url of websocket
    connected: false,
    roomOn: false,
    roomId: null,
    isPaired: false,

    sendMessage: function(data) {
        APP.socket.send(JSON.stringify(data));
        console.log(data);
    },

    appendChatMessage: function(message, owner) {
        let messageELement = null;
        if(owner === "user") {
            messageELement = '<div class="column is-full"><span class="tag is-primary chat-tag">' + message + '</span></div>'
        } else {
            messageELement = '<div class="column is-full"><span class="tag is-info chat-tag">' + message + '</span></div>'
        }
        $("#chat-room").append(messageELement);
    },

    messageUpdate: function(message) {
        console.log(APP.roomId)
        if(APP.roomId) {
            message = "Room: " + APP.roomId + " " + message;
            console.log(message);
        }
        $("#message").text(message);
    },

    initialize: function() {
        APP.socket = new WebSocket(APP.wsURL); // create a new websocket

        // Show a connected message when the WebSocket is opened.
        APP.socket.onopen = function(event) {
            APP.connected = true;
            APP.messageUpdate('Connected to Room Server');
        };

        // Show a disconnected message when the WebSocket is closed.
        APP.socket.onclose = function(event) {
            APP.connected = false;
            APP.messageUpdate('Disconnected from Room Server');
            APP.roomEnded();  // Room Ended - Disconnected from Server
    
        };

        // Handle any errors that occur.
        APP.socket.onerror = function(error) {
            APP.connected = false;
            APP.roomOn = false;
            APP.isPaired = false;
            APP.messageUpdate('Connection Error');
        };

        // Handle messages sent by the server.
        APP.socket.onmessage = function(event) {
            let payload = JSON.parse(event.data);
            let action = payload.action;
            let data = payload.data;
            APP.serverMessage(action, data);
        };

    },

    roomStarted: function(roomId) {
        APP.roomOn = true;
        APP.roomId = roomId;
        // APP.resetBoard();
        $("#room-submit")[0].style.backgroundColor = "red";
        $("#room-submit").val("End Chat");
    },

    roomEnded: function() {
        $("#chat-room").val("");
        $("#room-submit")[0].style.backgroundColor = "";
        $("#room-submit").val("New Room");
        APP.roomOn = false;
        APP.isPaired = false;
        APP.roomId = null;
    },

    abortRoom: function() {
        // End Room/Chat
        let data = {
            action: "abort",
            room_id: APP.roomId
        };
        APP.sendMessage(data);
    },

    newRoom: function() {
        if(!APP.connected) {
            APP.initialize();
        }

        let data = {
            action: "new"
        };

        APP.sendMessage(data);
    },

    joinRoom: function(roomId) {
        if(!APP.connected) {
            APP.initialize();
        }

        let data = {
            action: "join",
            room_id: roomId
        };
        APP.sendMessage(data);
    },

    newMesage: function(data) {
        // ... do something
        let message = data.remote_message;
        if(message) {
            APP.appendChatMessage(message, "remote");
        }
    },

    serverMessage: function(action, data) {
        switch (action) {
            case "open": // socket connection established
                APP.messageUpdate("Connected to Room Server")
                break;
            case "wait-pair": // wait for other user
                APP.roomStarted(data.room_id);
                APP.messageUpdate("Waiting for Pair to join..");
                break;
            case "paired": // both users have joined
                APP.roomStarted(data.room_id);
                APP.isPaired = true;
                APP.messageUpdate("Start Chatting....");
                break;
            case "message":
                APP.newMesage(data);
                break;
            case "end":
                APP.roomEnded();
                APP.messageUpdate("Room Closed. Thankyou!");
                break;
            case "error":
                if (data.message) {
                    APP.messageUpdate(data.message);
                } else {
                    APP.messageUpdate("Opps!...Error Occured");
                }
                break;
            default:
                APP.messageUpdate("Unknown Action: " + action);
        }
    },

    sendUserMessage: function(message) {
        // ... append message in the chat box
        APP.appendChatMessage(message, "user");
        let data = {
            action: "message",
            user_message: message
        };
        APP.sendMessage(data);
    }

};

// on typying anything on room-id input change the state of button
$("#room-id").on("change paste keyup", function() {
    var value = $(this).val();
    if (value) {
      $("#room-submit").val("Join Room");
    } else {
      $("#room-submit").val("New Room");
    }
});

APP.initialize();

$("#room-submit").click(function() {
    if(APP.roomOn) {
        APP.abortRoom();
    } else {
        // New/Join Room
        let roomId = $("#room-id").val();
        if(roomId) {
            // console.log
            APP.joinRoom(roomId);
        } else {
            APP.newRoom();
        }
    }
});

function messageSender() {
    let message  = $("#chat-message").val();
    // console.log("Message value: " + message);
    if(message && APP.isPaired) {
        $("#chat-message").val('');
        APP.sendUserMessage(message);
    }
}

$("#send").click(messageSender);






