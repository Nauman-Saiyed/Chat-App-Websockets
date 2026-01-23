from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime
from core.database import get_db
from middleware.auth import get_current_user
from schemas.messages import Message, MessageResponse

router = APIRouter(prefix="/rooms", tags=["Messages"])

@router.post("/{room_id}/messages", response_model=MessageResponse)
async def create_message(
    room_id: str,
    data: Message,
    db=Depends(get_db),
    user_id=Depends(get_current_user)
):
    room = await db.rooms.find_one({"_id": ObjectId(room_id)})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    doc = {
        "content": data.content,
        "room_id": room_id,
        "user_id": str(user_id),
        "created_at": datetime.utcnow(),
    }
    res = await db.messages.insert_one(doc)
    return {
        "id": str(res.inserted_id),
        "content": doc["content"],
        "room_id": doc["room_id"],
        "user_id": doc["user_id"],
    }

@router.get("/{room_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    room_id: str,
    db=Depends(get_db),
    user_id=Depends(get_current_user) 
):
    cursor = db.messages.find({"room_id": room_id}).sort("created_at", 1)
    docs = await cursor.to_list(length=200)

    return [
        {
            "id": str(d["_id"]),
            "content": d["content"],
            "room_id": d["room_id"],
            "user_id": d["user_id"],
        }
        for d in docs
    ]
