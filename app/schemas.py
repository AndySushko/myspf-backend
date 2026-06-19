from datetime import date
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str | None = None
    birth_date: date


class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str | None = None
    birth_date: date
    phototype: str | None = None
    gender: str | None = None
    region: str | None = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PhototypeUpdate(BaseModel):
    phototype: str