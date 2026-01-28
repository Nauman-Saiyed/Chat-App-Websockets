import json
from fastapi import WebSocket
from typing import Dict , List , Set


class RoomConnectionManager:
    
    def __init__(self):
        self.active_rooms : Dict[str , List[WebSocket]] = {}
        self.user_info : Dict[WebSocket , dict] = {}
        # self.room_members : Dict[str , Set[str]] = {}
        self.room_members: Dict[str, Dict[str, str]] = {}

    
    async def connect(
        self,
        websocket : WebSocket,
        room_id : str ,
        user_id : str,
        username : str 
    ):
        await websocket.accept()
        
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []
            self.room_members[room_id] = {}
        
        self.active_rooms[room_id].append(websocket)
        
        self.user_info[websocket] = {
            "user_id" : user_id,
            "username" : username,
            "room_id" : room_id
        }
        
        # self.room_members[room_id].add(username)
        self.room_members[room_id][user_id] = username
    
    
    async def disconnect(self ,websocket : WebSocket):
        user_info = self.user_info.get(websocket)
        if not user_info:
            return None , None
        
        room_id = user_info["room_id"]
        user_id = user_info["user_id"]
        username = user_info["username"]

        if room_id in self.active_rooms and websocket in self.active_rooms[room_id]:
            self.active_rooms[room_id].remove(websocket)    
        
        # self.room_members.get(room_id, {}).pop(user_id, None)
        # self.user_info.pop(websocket, None)
        
        if room_id in self.room_members:
            # self.room_members[room_id].discard(username)
            self.room_members[room_id].pop(user_info["user_id"], None)
            
        self.user_info.pop(websocket, None)
        
        if room_id in self.active_rooms and not self.active_rooms[room_id]:
            self.active_rooms.pop(room_id, None)
            self.room_members.pop(room_id, None)
        
        return room_id , username
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_room(self , room_id : str , message : dict):
        if room_id not in self.active_rooms:
            return
        
        message_str = json.dumps(message)
        dead_connections = []
        
        for connection in list(self.active_rooms[room_id]):
            try:
                await connection.send_text(message_str)
            except :
                dead_connections.append(connection)
    
        for dead_ws in dead_connections:
            await self.disconnect(dead_ws)
    
    
    def get_active_user_id(self, room_id: str):
        return list(self.room_members.get(room_id, {}).keys())
    
    def get_active_username(self, room_id: str):
        return list(self.room_members.get(room_id, {}).values())


    
    def members_payload(self, room_id: str):
        return [
            {"user_id": uid, "username": uname}
            for uid, uname in self.room_members.get(room_id, {}).items()
        ]



room_manager = RoomConnectionManager()


