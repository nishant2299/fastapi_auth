import string
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    phone = Column(Integer)
    hashed_password = Column(String)


class ForgetPasswordOTP(Base):
    __tablename__ = "user_otp"

    id = Column(Integer, primary_key=True, index=True)
    otp = Column(Integer)
    user_email = Column(String(255), ForeignKey("users.email"))
    email = relationship("User")


