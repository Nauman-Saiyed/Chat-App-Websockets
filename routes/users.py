from fastapi import APIRouter , Depends , HTTPException , status
from datetime import datetime
from bson import ObjectId
from schemas.user import CreateUser , UpdateUser
from models.user import user_detail
from core.database import get_db
from middleware.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("" , status_code=status.HTTP_201_CREATED)
async def create_user(data : CreateUser , db = Depends(get_db)):
    existing_user = await db.users.find_one(
        {"username" : data.username}
    )
    
    if existing_user :
        raise HTTPException(status_code=400 , detail="User Already Registered")
    
    user = user_detail(data.dict())
    await db.users.insert_one(user)
    
    return {"message" : "User created Successfully"}


@router.get("")
async def get_users(
    db=Depends(get_db),
    user_id : str = Depends(get_current_user)
) :
    users = []
    async for user in db.users.find():
        users.append({
            "user_id": str(user["_id"]),
            "username": user["username"],
            # "email": user["email"],
            "created_at": user["created_at"],
        })
    return users

@router.get("/{user_id}")
async def get_one_user(
    user_id : str ,
    db = Depends(get_db),
    _: str = Depends(get_current_user) 
) :
    user = await db.users.find_one(
        {"_id" : ObjectId(user_id)}
    )
    
    if not user :
        raise HTTPException(status_code=404 , detail="User not Found")
    
    return {
        "user_id": str(user["_id"]),
        "username": user["username"],
        # "email": user["email"],
        "created_at": user["created_at"],
    }


@router.put("/{user_id}")
async def update_user(
    user_id : str,
    data : UpdateUser,
    db = Depends(get_db),
    _: str = Depends(get_current_user)
):
    update_data = {k : v for k , v in data.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    result = await db.users.update_one(
        {"_id" : ObjectId(user_id)} ,
        {"$set" : update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404 , detail="User Not Found")
    
    return {"message" : "User Updated Successfully"}

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db=Depends(get_db),
    _: str = Depends(get_current_user)
):
    result = await db.users.update_one(
        {"_id": ObjectId(user_id), "deleted_at": None},
        {"$set": {"deleted_at": datetime.utcnow()}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}
