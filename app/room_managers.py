
class InvalidRoomError(Exception):
    # Raised when room is not in registry 
    pass


class RoomManager:
    def __init__(self):
        # Records All Rooms in a Dictionary and create a sequence of room ids
        self.rooms = {}
        self.max_room_id = 100
    
    # we can improve this in future
    def _get_next_room_id(self):
        """Returns next room id
        """
        if self.max_room_id > 100000:
            self.max_room_id = 100
        self.max_room_id += 1
        return self.max_room_id

    def new_room(self, handler):
        # Creates a new Room and returns the room id
        room_id = self._get_next_room_id()

        # insert the handler of one user (user "a") -> user who created the room
        self.rooms[room_id] = {
            "handler_a": handler
        }
        return room_id
    
    def join_room(self, room_id, handler):
        # Returns room_id is join is successful
        # Raises InvalidRoomError when it could not join the room

        room = self.get_room(room_id)
        if room.get("handler_b") is None: # room has space for one person (handler_b is not present)
            room["handler_b"] = handler
            return room_id
        #  Room id not found
        raise InvalidRoomError

    def end_room(self, room_id):
        # Removes the Room from the rooms registry

        if room_id in self.rooms:
            del self.rooms[room_id]
    
    def get_pair(self, room_id, handler):
        # Returns the paired handler
        room = self.get_room(room_id)

        if handler == room.get("handler_a"): # if paired handler is reqired by a then return b's handler
            return room.get("handler_b")
        elif handler == room.get("handler_b"):
            return room.get("handler_a")
        else:
            raise InvalidRoomError

    def get_room(self, room_id):
        # Returns the room instance.  Raises Error when room not found

        room = self.rooms.get(room_id)
        if room:
            return room
        raise InvalidRoomError

