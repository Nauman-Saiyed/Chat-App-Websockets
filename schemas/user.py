from pydantic import BaseModel , EmailStr
from typing import Optional
from datetime import datetime

class LoginSchema(BaseModel):
    username : str
    password : str


class TokenResponse(BaseModel):
    access_token : str
    token_type :  str = "bearer"

class CreateUser(BaseModel):
    username : str
    # email : EmailStr
    password : str


class UpdateUser(BaseModel):
    username : Optional[str] = None
    # email : Optional[str] = None


class UserResponse(BaseModel):
    user_id : str
    username : str
    # email : EmailStr
    created_at : datetime
