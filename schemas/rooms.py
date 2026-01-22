from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# class UserRooms(BaseModel):
#     id : str
#     user_id : str
#     room_id : str
#     is_admin : bool


class CreateRooms(BaseModel):
    room_name : str

class JoinRoom(BaseModel):
    room_id : str

class LeaveRoom(BaseModel):
    room_id : str

class RoomResponse(BaseModel):
    room_id : str
    room_name : str
    admin_id : str
    # is_admin : bool