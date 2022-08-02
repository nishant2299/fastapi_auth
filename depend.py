from jose import JWTError, jwt
from db import SessionLocal
from typing import Optional
from datetime import datetime, timedelta
from config import settings 
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPBasicCredentials
import models

security = HTTPBearer()


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        userid: int = payload.get("id")
        if userid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    current_user = db.query(models.User).filter_by(id=userid).first()
    if current_user is None:
        raise credentials_exception
    return current_user