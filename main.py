from curses.ascii import US
from typing import List
from datetime import datetime, timedelta
from urllib import request
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
import models
from models import User
import schema
from db import engine
from crud import get_user, get_users, create_user1, verify_otp,validate_password, update_password, forget_password_mail
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from depend import get_db, get_current_user, create_access_token, create_refresh_token
from config import settings


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Api's

@app.post("/users/")
async def create_user(user: schema.User_create, db: Session = Depends(get_db)):
    return create_user1(db=db, user=user)


@app.get("/users/")
async def read_users(db: Session = Depends(get_db)):
    users = get_users(db)
    return users


@app.get("/users/{user_id}", dependencies=[Depends(get_current_user)])
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/me/", tags=["current_user"])
async def read_users_me(db:Session=Depends(get_current_user)):
    return {"email": db.email,"username":db.name, "phone":db.phone}


@app.post("/token", tags=["authentication"])
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):

    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not form_data.password == user.hashed_password:
        return {"status": False, "access_token": "please enter valid password", "token_type": "bearer"}

    if form_data.password == user.hashed_password:
        refresh_token=create_refresh_token(data={"email":user.email})
        if refresh_token:
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"id": user.id}, expires_delta=access_token_expires)

    return {"access_token": access_token, "refresh_token":refresh_token, "token_type": "bearer"} 


@app.get("/get_new_access", tags=["authentication"])
async def get_new_access_token(refresh_token:str,db:Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if refresh_token:
        payload= jwt.decode(refresh_token, settings.SECRET_KEY, settings.ALGORITHM,)
        user= payload.get("email")
        if user is None:
            raise credentials_exception
    current_user = db.query(models.User).filter_by(email=user).first()
    if current_user is None:
        raise credentials_exception
    access_user = {"id":current_user.id, "exp": datetime.utcnow() + timedelta(minutes=30)}
    new_accesss_token = jwt.encode(access_user, settings.SECRET_KEY, settings.ALGORITHM)
    return {"status":True, "new_access_token":new_accesss_token}


@app.post("/forget_password/")
async def forget_password(request_data: schema.ForgetPassword, db: Session = Depends(get_db)):
    status_val, message = await forget_password_mail(db=db, email=request_data.email)
    if not status_val:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
        )
    return{"status":status.HTTP_200_OK, "message": message}


@app.post("/reset_password/")
async def reset_password(request_data:schema.ResetPswdSchema,db: Session = Depends(get_db)):
    status_val, email = verify_otp(request_data.otp, db = db)
    if status_val:
        status_val = validate_password(request_data)
        if status_val:
            payload ={
                'hashed_password': request_data.confirm_password
            }
            status_val, message = update_password(
                payload = payload,
                model = User,
                email = email,
                db = db
            ) 
            return {'status': status_val, 'message': message} 
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Password",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP",
        )
        


