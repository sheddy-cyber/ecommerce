from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True