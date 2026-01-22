from fastapi import APIRouter , Depends , HTTPException 
from schemas.user import LoginSchema , TokenResponse 
from core.database import get_db
from core.security import create_access_token, hash_password ,verify_password
from datetime import datetime   , UTC


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login" , response_model=TokenResponse)
async def login(data : LoginSchema , db =  Depends(get_db)):
    
    print(data)
    user = await db.users.find_one(
        {"username" : data.username , "deleted_at" : None}
    )
    
    if not user :
        hashed = hash_password(data.password)
        new_user = await db.users.insert_one(
            {"username" : data.username, "password" : hashed , "created_at" : datetime.now(UTC) , "updated_at" : datetime.now(UTC) | None , "deleted_at" : None}
        )
        print(new_user)
        # result = await db.users.insert_one(new_user)
        user_id = new_user.inserted_id
        # raise HTTPException(status_code=401 , detail="Invalid Credentials")
    else:
        if not verify_password(data.password , user["password"]):
            raise HTTPException(status_code=401 , detail="Invalid Credentials")
    
    user_id = user["_id"]
    token = create_access_token({"sub" : str(user_id)})
    
    return {"access_token" : token}
