from typing import List, Optional

from pydantic import BaseModel, EmailStr


class User_create(BaseModel):
    email: str
    name:str
    phone:int
    hashed_password: str

    class Config:
        orm_mode = True

class ForgetPassword(BaseModel):
    email: List[EmailStr]
    class Config:
        orm_mode = True

class ResetPswdSchema(BaseModel):
    otp : int
    password: str
    confirm_password : str