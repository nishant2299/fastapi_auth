
from sqlalchemy.orm import Session

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import Dict

from config import settings
import random as r

import models, schema


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session):
    return db.query(models.User).all()


def create_user1(db: Session, user: schema.User_create):
    db_user = models.User(email=user.email, name=user.name, phone=user.phone, hashed_password=user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db:Session, user_id:int,user: schema.User_create):

    user_item=db.query(models.User).filter(models.User.id == user_id).first()
    user_item.email = user.email
    user_item.name = user.name
    user_item.phone = user.phone
    db.commit()
    return user_item


def otp_generator():
    otp=""
    for i in range(4):
        otp+=str(r.randint(1,9))
    return otp

conf = ConnectionConfig(
        MAIL_USERNAME = settings.MAIL_USERNAME,
        MAIL_PASSWORD = settings.MAIL_PASSWORD,
        MAIL_FROM= settings.MAIL_FROM,
        MAIL_PORT = settings.MAIL_PORT,
        MAIL_SERVER = settings.MAIL_SERVER,
        MAIL_TLS = settings.MAIL_TLS,
        MAIL_SSL = settings.MAIL_SSL
    )

async def forget_password_mail(db:Session, email):
    email= email[0]
    user_exists = db.query(models.User).filter(models.User.email == email).first()
    if user_exists:
        otp = otp_generator()
        message = MessageSchema(
            subject="Forget password link",
            recipients=[email], 
            body=f'Your forget password confirmation OTP is :- {otp}',
            )
        fm = FastMail(conf)
        await fm.send_message(message)
        save_otp = models.ForgetPasswordOTP(user_email = email[0], otp = otp)
        db.add(save_otp)
        db.commit()
        db.refresh(save_otp)
        return True, "OTP sent successfully"
    else:
        return False, 'user does not exist'


def verify_otp(otp, db):
    check_otp = db.query(models.ForgetPasswordOTP).filter(models.ForgetPasswordOTP.otp == otp).first()
    if check_otp:
        return True, check_otp.user_email
    else:
        return False, 'Invalid OTP'


def validate_password(request_data):
    if request_data.password == request_data.confirm_password and request_data.confirm_password!= 'string':
        return True
    else:
        False


def update_password(payload: Dict, model, email, db: Session,):
    try:
        db.query(model).filter_by(email=email).update(payload)
        db.commit()
        return True, 'Password updated successfully'
    except Exception as msg:
        db.rollback()
        return False, str(msg)
