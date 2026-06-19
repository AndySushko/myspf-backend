from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    birth_date = Column(Date, nullable=False)

    phototype = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    region = Column(String, nullable=True)