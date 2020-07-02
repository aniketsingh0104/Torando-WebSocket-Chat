import json
import logging

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError

from app.room_managers import InvalidRoomError

logger = logging.getLogger("app")

class IndexHandler(RequestHandler):
    #render the chat main page
    def get(self):
        self.render("index.html")

class RoomSocketHandler(WebSocketHandler):
    def initialize(self, room_manager):
        self.room_id = None
        self.room_manager = room_manager
        # super().__init__(*args, **kwargs)

    def open(self):
        # Opens a Socket Connection to client
        self.send_message(action="open", message="Connected to room Server")

    def on_message(self, message):
        # Respond to messages from connected client.
        # Messages are of form -
        # {
        #     action: <action>,
        #     <data>
        # }
        # Valid Actions: new, join, abort, move.
        # new - Request for new room
        # join - Join an existing room (but that's not been paired)
        # abort - Abort the room currently on
        # message 
        
        data = json.loads(message)
        action = data.get("action", "") #key, default value in get
        if action == "message": # if message received from one user
            user_message = data.get("user_message") # get the message
            if user_message:
                self.send_pair_message(action="message", remote_message=user_message) #send it to other pair
        elif action == "join":
            # Get the room_id
            try:
                room_id = int(data.get("room_id"))
                self.room_manager.join_room(room_id, self)
            except (ValueError, TypeError, InvalidRoomError):
                self.send_message(action="error", message="Invalid Room Id: {}".format(data.get("room_id")))
            else:
                # Joined the room.
                self.room_id = room_id
                # Tell both users that they have been paired
                self.send_message(action="paired", room_id=room_id)
                self.send_pair_message(action="paired", room_id=room_id)
        elif action == "new":
            #  Create a new room room id and respond the room id
            self.room_id = self.room_manager.new_room(self)
            self.send_message(action="wait-pair", room_id=self.room_id)
        
        elif action == "abort":
            # self.room_manager.abort_room(self.room_id)
            self.send_message(action="end", room_id=self.room_id)
            self.send_pair_message(action="end", room_id=self.room_id)
            self.room_manager.end_room(self.room_id)

        else:
            self.send_message(action="error", message="Unknown Action: {}".format(action))

    
    def on_close(self):
        # Overwrites WebSocketHandler.close.
        # Close Room, send message to Paired client that room has ended
        
        self.send_pair_message(action="end", room_id=self.room_id)
        self.room_manager.end_room(self.room_id)

    def send_pair_message(self, action, **data):
        # send message to paired Handler

        if not self.room_id:  
            return  # return if room_id is None
        try:
            paired_handler = self.room_manager.get_pair(self.room_id, self)
        except InvalidRoomError:
            logging.error("Inalid Room: {0}. Cannot send pair msg: {1}".format(self.room_id, data))
        else:
            if paired_handler:
                paired_handler.send_message(action, **data)

    def send_message(self, action, **data):
        # Sends the message to the connected client

        message = {
            "action": action,
            "data": data
        }
        try:
            self.write_message(json.dumps(message))
        except WebSocketClosedError:
            logger.warning("WS_CLOSED" + "Could Not send Message: " + json.dumps(message))
            # Send Websocket Closed Error to Paired Opponent
            self.send_pair_message(action="pair-closed")
            self.close()