from fastapi import APIRouter , Depends , HTTPException ,status
from schemas.rooms import  CreateRooms , JoinRoom, LeaveRoom 
from models.user import user_detail
from core.database import get_db
from middleware.auth import get_current_user
from bson import ObjectId
from core.connection_manager import room_manager


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)


@router.post("/")
async def create_room(
        data : CreateRooms ,
        db = Depends(get_db) , 
        user_id = Depends(get_current_user)
):
    existing_room = await db.rooms.find_one(
        {"room_name" : data.room_name}
    )
    
    if existing_room :
        raise HTTPException(status_code=400 , detail="Room Already Exists")
    
    # print(user_id)
    room_detail = {
            "_id" : ObjectId(),
            "room_name" : data.room_name,
            "admin_id" : ObjectId(user_id),
            "members" : [ObjectId(user_id)]
        }
    
    new_room = await db.rooms.insert_one(room_detail)
    # print(new_room.admin_id)
    return {"message" : "Room Created " ,
            "room_id" : str(new_room.inserted_id),
            "room_name" : data.room_name,
            "is_admin":  True
            }


@router.post("/join")
async def join_room(
    data : JoinRoom,
    db = Depends(get_db),
    user_id = Depends(get_current_user)
):
    
    existing_room = await db.rooms.find_one(
        {"_id" : ObjectId(data.room_id)}
    )
    print(existing_room)
    if not existing_room:
        raise HTTPException(status_code=400 , detail="Room does not Exist")
    
    # if user_id not in existing_room["members"]:
    await db.rooms.update_one(
        {"_id" : ObjectId(data.room_id)} ,
            {
                "$addToSet" : {
                    "members" : ObjectId(user_id)
                }
            }
    )
    
    return {
        "message": "Joined room",
        "room_id": str(existing_room["_id"]),
        "room_name": existing_room["room_name"],
        "is_admin":  existing_room["admin_id"] == ObjectId(user_id)
    }

@router.post("/leave")
async def leave_room(
    data : LeaveRoom,
    db=Depends(get_db),
    user_id =Depends(get_current_user)
):
    existing_room = await db.rooms.find_one(
        {"_id": ObjectId(data.room_id)}
    )
    
    if not existing_room:
        return {"message": "Room already removed"}
    
    admin_id = existing_room.get("admin_id")
    is_admin = (
            admin_id == ObjectId(user_id) or 
            str(admin_id) == str(user_id)
        )
    
    if is_admin:
        await db.rooms.delete_one(
            {"_id" : ObjectId(data.room_id)}
        )
        
        await db.messages.delete_many(
            {"room_id" : data.room_id}
        )
        # await room_manager.close_room(data.room_id)
        return {"message" : "Room Dismantled by Admin"}
    
    if ObjectId(user_id) in existing_room["members"]:
        await db.rooms.update_one(
            {"_id" : ObjectId(data.room_id)},
            {
                "$pull" : {
                    "members" : ObjectId(user_id)
                }
            }
        )
        return {"message" : "Left Room"}
    
    return {"message": "User not in room"}
