from fastapi import FastAPI , WebSocket , Request , WebSocketDisconnect
from fastapi.responses import  HTMLResponse , RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles 
from core.connection_manager import ConnectionManager
from routes import auth , users , rooms
from core.config import settings


templates = Jinja2Templates(directory="templates")

app = FastAPI(title=settings.APP_NAME)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rooms.router)

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