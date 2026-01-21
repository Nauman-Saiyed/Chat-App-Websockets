from fastapi import FastAPI , WebSocket , Request , WebSocketDisconnect
from fastapi.responses import  HTMLResponse , RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles 
from dataclasses import dataclass
from typing import Dict
import uuid
import json

templates = Jinja2Templates(directory="templates")
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
        print(self.active_connections)
        # print(send_personal_message)
        await websocket.send_text(message)

    # async def display(self , message : str , websocket : WebSocket):
    #     decoded_data = json.loads(message) 
        
    #     for connection in self.active_connections.values():
    #         is_me = False
    #         if(connection == websocket):
    #             is_me = True    
            
    #         msg = json.dumps({"isMe" : is_me , "data" : decoded_data['message'] , 'username' : decoded_data['username']})
    #         await connection.send_text(msg)

    async def broadcast(self, webSocket: WebSocket, data: str):
        # print(data)
        decoded_data = json.loads(data)
        # print(webSocket)
        # self.active_connections
        # print(decoded_data)
        for connection in self.active_connections.values():
            print(connection)
            is_me = False
            if connection == webSocket:
                print(connection)
                is_me = True

            await connection.send_text(json.dumps({"isMe": is_me, "data": decoded_data['message'], "username": decoded_data['username']}))




app = FastAPI()
app.mount("/static" , StaticFiles(directory="static") , name="static")
connection_manager = ConnectionManager()

@app.get("/" , response_class=HTMLResponse)
async def get_chat_room(request :  Request):
    return templates.TemplateResponse("index.html" , {"request" : request})

@app.websocket("/message") 
async def websocket_endpoint(websocket :  WebSocket):
    await connection_manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await connection_manager.broadcast(websocket , data)
    except WebSocketDisconnect:
        return RedirectResponse("/")