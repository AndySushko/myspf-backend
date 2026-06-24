from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import hash_password, verify_password
from app.database import Base, engine, get_db
from fastapi import File, UploadFile
from app.ml import predict_phototype
from app.recommendations import get_recommendations
from app.schemas import RecommendationsOut
import requests

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MySPF API"
)


@app.get("/")
def root():
    return {"message": "MySPF API работает"}


@app.post("/auth/register", response_model=schemas.UserOut)
def register_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с такой почтой уже существует"
        )

    new_user = models.User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        birth_date=user_data.birth_date
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/auth/login", response_model=schemas.UserOut)
def login_user(
    login_data: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == login_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )

    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )

    return user


@app.patch("/users/{user_id}/phototype", response_model=schemas.UserOut)
def update_user_phototype(
    user_id: int,
    phototype_data: schemas.PhototypeUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    user.phototype = phototype_data.phototype

    db.commit()
    db.refresh(user)

    return user


@app.post("/ml/predict-phototype")
async def predict_phototype_endpoint(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()
    result = predict_phototype(image_bytes)

    return result

@app.get("/uv", response_model=schemas.UvOut)
def get_uv(
    latitude: float,
    longitude: float,
    phototype: str = "I-II"
):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "uv_index",
        "hourly": "uv_index",
        "daily": "uv_index_max",
        "timezone": "auto",
        "forecast_days": 7
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail="Не удалось получить данные UV-индекса"
        )

    data = response.json()

    hourly_times = data["hourly"]["time"]
    hourly_values = data["hourly"]["uv_index"]

    daily_values = data["daily"]["uv_index_max"]

    needed_hours = ["06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
    day_names = ["Сегодня", "Завтра", "Ср", "Чт", "Пт", "Сб", "Вс"]

    daily = []

    for day_index in range(7):
        day_hourly = []

        date_prefix = data["daily"]["time"][day_index]

        for target_hour in needed_hours:
            found_value = 0.0
            target_time = f"{date_prefix}T{target_hour}"

            for time_value, uv_value in zip(hourly_times, hourly_values):
                if time_value == target_time:
                    found_value = round(float(uv_value), 1)
                    break

            day_hourly.append(
                schemas.UvHourlyItem(
                    hour=target_hour[:2],
                    value=found_value
                )
            )

        daily.append(
            schemas.UvDayForecast(
                day=day_names[day_index],
                max_uv=round(float(daily_values[day_index]), 1),
                hourly=day_hourly
            )
        )

    today_hourly = daily[0].hourly

    current_uv = round(
        float(data.get("current", {}).get("uv_index", 0.0)),
        1
    )

    if current_uv < 3:
        risk_level = "низкий"
    elif current_uv < 6:
        risk_level = "умеренный"
    elif current_uv < 8:
        risk_level = "высокий"
    elif current_uv < 11:
        risk_level = "очень высокий"
    else:
        risk_level = "экстремальный"

    base_minutes = {
        "I-II": 180,
        "III": 260,
        "IV": 380,
        "V": 540,
        "VI": 760
    }.get(phototype, 180)

    safe_minutes = int(base_minutes / max(current_uv, 1))

    hours = safe_minutes // 60
    minutes = safe_minutes % 60

    if hours > 0:
        max_sun_time = f"{hours} ч {minutes} мин"
    else:
        max_sun_time = f"{minutes} мин"

    return schemas.UvOut(
        current_uv=current_uv,
        risk_level=risk_level,
        skin_type=f"{phototype} тип",
        max_sun_time=max_sun_time,
        hourly=today_hourly,
        daily=daily
    )

@app.get("/recommendations", response_model=schemas.RecommendationsOut)
def recommendations(
    latitude: float,
    longitude: float,
    phototype: str = "I-II"
):
    uv_response = get_uv(
        latitude=latitude,
        longitude=longitude,
        phototype=phototype
    )

    recommendations_list = get_recommendations(
        uv=uv_response.current_uv,
        phototype=phototype
    )

    return schemas.RecommendationsOut(
        recommendations=recommendations_list
    )