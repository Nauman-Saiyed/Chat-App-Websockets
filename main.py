from datetime import datetime , UTC
import json
from fastapi import FastAPI , WebSocket , Request , WebSocketDisconnect , Depends
from fastapi.responses import  HTMLResponse 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles 
from core.connection_manager import room_manager
from middleware.auth import get_current_user, get_user_from_token
from routes import auth, messages , users , rooms
from core.config import settings
from core.database import get_db


templates = Jinja2Templates(directory="templates")

app = FastAPI(title=settings.APP_NAME)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(messages.router)

app.mount("/static" , StaticFiles(directory="static") , name="static")

@app.get("/" , response_class=HTMLResponse)
async def get_chat_room(request :  Request):
    return templates.TemplateResponse("index.html" , {"request" : request})

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str , db=Depends(get_db)):

    # user_id = websocket.query_params.get("user_id", str(uuid.uuid4()))
    user_id = websocket.query_params.get("user_id")
    username = websocket.query_params.get("username", f"User_{user_id[:8]}")

    user = await db.users.find_one({"username": username})
    if not user:
        await websocket.close(code=1008)
        return
    user_id = str(user["_id"])

    await room_manager.connect(websocket, room_id, user_id, username)

    await room_manager.broadcast_to_room(room_id, {
        "type": "user_joined",
        "username": username,
        "message": f"{username} joined the room",
        # "room_members": list(room_manager.room_members.get(room_id, []))
        "room_members": room_manager.members_payload(room_id)
    })

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "chat_message":
                content = message_data.get("message", "").strip()
                
                if not content:
                    continue
                
                await db.messages.insert_one({
                    "room_id": room_id,
                    "user_id": user_id,
                    "username": username,
                    "message": content,
                    "created_at": datetime.now(UTC)
                })

                await room_manager.broadcast_to_room(room_id, {
                    "type": "chat_message",
                    "username": username,
                    "user_id": user_id,
                    "message": content,
                    "room_id": room_id,
                    # "room_members": list(room_manager.room_members.get(room_id, []))
                    "room_members": room_manager.members_payload(room_id)

                })

            elif message_data.get("type") == "typing":
                typing_message = {
                    "type": "typing",
                    "username": username,
                    "is_typing": message_data.get("is_typing", False)
                }
                
                for connection in room_manager.active_rooms.get(room_id, []):
                    if connection != websocket:
                        try:
                            await connection.send_text(json.dumps(typing_message))
                        except:
                            pass

    except WebSocketDisconnect:
        room_id2, username2 = await room_manager.disconnect(websocket)
        if room_id2 and username2:
            await room_manager.broadcast_to_room(room_id2, {
                "type": "user_left",
                "username": username2,
                "message": f"{username2} left the room",
                # "room_members": list(room_manager.room_members.get(room_id2, []))
                "room_members": room_manager.members_payload(room_id2)
            })

