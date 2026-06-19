from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import hash_password, verify_password
from app.database import Base, engine, get_db
from fastapi import File, UploadFile
from app.ml import predict_phototype

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