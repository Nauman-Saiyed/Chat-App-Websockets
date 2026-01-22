from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json 
import uuid
from dataclasses import dataclass


class RoomConnectionManager:
    
    def __init__(self):
        self.rooms = {}  # room_id -> set of websockets

    async def connect(self, room_id, websocket):
        self.rooms.setdefault(room_id, set()).add(websocket)

    def disconnect(self, room_id, websocket):
        self.rooms.get(room_id, set()).discard(websocket)

    async def broadcast(self, room_id, message):
        for ws in self.rooms.get(room_id, set()):
            await ws.send_json(message)

    async def close_room(self, room_id):
        for ws in self.rooms.get(room_id, set()):
            await ws.close()
        self.rooms.pop(room_id, None)

room_manager = RoomConnectionManager()

@dataclass
class ConnectionManager:
    
    def __init__(self):
        self.active_connections : dict = {}

    async def connect(self , websocket : WebSocket):
            await websocket.accept()
            id = str(uuid.uuid4())
            
            self.active_connections[id] = websocket
            
            message = json.dumps({"isMe" : True , "data" : "Have Joined!!" , "username" : "You"} )
            await self.send_personal_message(message  , websocket)

    def find_id(self , websocket : WebSocket):
        websocket_list = list(self.active_connections.values())
        id_list = list(self.active_connections.keys())
        
        pos = websocket_list.index(websocket)
        return id_list[pos]


    def disconnect(self , websocket : WebSocket):
        id = self.find_id(websocket)
        self.active_connections.remove(id)
        
        return id

    async def send_personal_message(self , message : str , websocket : WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, webSocket: WebSocket, data: str):
        decoded_data = json.loads(data)
        for connection in self.active_connections.values():
            print(connection)
            is_me = False
            if connection == webSocket:
                print(connection)
                is_me = True

            await connection.send_text(json.dumps({"isMe": is_me, "data": decoded_data['message'], "username": decoded_data['username']}))


