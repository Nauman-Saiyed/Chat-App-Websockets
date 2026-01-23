from fastapi import Depends , HTTPException , status
from fastapi.security import HTTPBearer , HTTPAuthorizationCredentials
from jose import jwt , JWTError
from core.config import settings

security = HTTPBearer()

def get_current_user(
    credentials : HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    
    try :
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=settings.JWT_ALGORITHM
        ) 
        
        userId : str = payload.get("sub")
        if not userId:
            raise HTTPException(status_code=401 , detail="Invalid Token")
        return userId
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired Token"
        )


async def get_user_from_token(token: str, db):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await db.users.find_one(
            {"_id": ObjectId(user_id)},
            {"username": 1}
        )

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return {
            "_id": user_id,
            "username": user["username"]
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
