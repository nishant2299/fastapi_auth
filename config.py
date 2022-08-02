import os
from pydantic import BaseSettings
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY = os.environ["SECRET_KEY"]
    ALGORITHM = os.environ["ALGORITHM"]
    ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]
    SQLALCHEMY_DATABASE_URL = os.environ["SQLALCHEMY_DATABASE_URL"]
    MAIL_USERNAME = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    MAIL_FROM = os.environ["MAIL_FROM"]
    MAIL_PORT = os.environ["MAIL_PORT"]
    MAIL_SERVER = os.environ["MAIL_SERVER"]
    MAIL_TLS = os.environ["MAIL_TLS"]
    MAIL_SSL = os.environ["MAIL_SSL"]

    

settings = Settings()




