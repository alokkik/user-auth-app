# app/schemas.py

from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    email: EmailStr
    id: str

class UserAuth(BaseModel):
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str