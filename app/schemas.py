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

class UvHourlyItem(BaseModel):
    hour: str
    value: float


class UvDailyItem(BaseModel):
    day: str
    max_uv: float

class UvDayForecast(BaseModel):
    day: str
    max_uv: float
    hourly: list[UvHourlyItem]

class UvOut(BaseModel):
    current_uv: float
    risk_level: str
    skin_type: str
    max_sun_time: str
    hourly: list[UvHourlyItem]
    daily: list[UvDayForecast]

class RecommendationItem(BaseModel):
    type: str
    title: str
    icon: str


class RecommendationsOut(BaseModel):
    recommendations: list[RecommendationItem]
