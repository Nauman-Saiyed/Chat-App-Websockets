from pydantic import BaseModel

class Message(BaseModel):
    content : str
    

class MessageResponse(BaseModel):
    id : str
    content : str
    room_id : str
    user_id : str