from fastapi import APIRouter , Depends , HTTPException 
from schemas.user import LoginSchema , TokenResponse 
from core.database import get_db
from core.security import create_access_token, hash_password ,verify_password
from datetime import datetime   , UTC


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginSchema, db=Depends(get_db)):

    user = await db.users.find_one(
        {"username": data.username, "deleted_at": None}
    )

    # USER DOES NOT EXIST → CREATE
    if not user:
        hashed_password = hash_password(data.password)

        result = await db.users.insert_one({
            "username": data.username,
            "password": hashed_password,
            "created_at": datetime.now(UTC),
            "deleted_at": None
        })

        user_id = result.inserted_id

    # USER EXISTS → VERIFY PASSWORD
    else:
        if not verify_password(data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = user["_id"]

    # AUTO LOGIN (COMMON FOR BOTH)
    token = create_access_token({"sub": str(user_id)})

    return {
        "access_token": token,
    }
