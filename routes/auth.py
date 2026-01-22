from fastapi import APIRouter , Depends , HTTPException 
from schemas.user import LoginSchema , TokenResponse 
from core.database import get_db
from core.security import create_access_token ,verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login" , response_model=TokenResponse)
async def login(data : LoginSchema , db =  Depends(get_db)):
    user = await db.users.find_one(
        {"email" : data.email , "deleted_at" : None}
    )
    
    if not user :
        raise HTTPException(status_code=401 , detail="Invalid Credentials")
    
    if not verify_password(data.password , user["password"]):
        raise HTTPException(status_code=401 , detail="Invalid Credentials")
    
    token = create_access_token({"sub" : str(user["_id"])})
    
    return {"access_token" : token}
