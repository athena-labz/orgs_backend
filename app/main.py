from typing import Annotated, Optional
from pydantic import BaseModel
from enum import Enum

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import jwt, JWTError

from model import db, User
from lib import cardano_tools

import pycardano as pyc
import peewee as pw
import datetime


SECRET_KEY = "23a5caa2d8386c8c33ff2b62babc7d79582f44bce2803376a5a6561bd10a652f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


db.connect()
db.create_tables([User])
db.close()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserExposed(BaseModel):
    email: str
    stake_address: str
    active: bool


# We will use OAuth2 for authentication
# username will be the stake address
# password will be the signature
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# https://fastapi.tiangolo.com
# https://fastapi.tiangolo.com/tutorial/bigger-applications/
app = FastAPI()


def get_user(username: str) -> Optional[User]:
    return User.get(User.stake_address == username)


def authenticate_user(username: str, password: str):
    user = get_user(username)

    if not user:
        return None

    if not cardano_tools.verify_signature(
        password, pyc.Address.from_primitive(username)
    ):
        return None

    return user


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.stake_address}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=UserExposed)
async def read_users_me(
    current_user: Annotated[UserExposed, Depends(get_current_active_user)]
):
    return current_user


class UserType(Enum):
    STUDENT = 0
    TEACHER = 1
    ORGANIZER = 2


class RegisterBody(BaseModel):
    user_type: UserType
    email: str
    stake_address: str
    signature: str  # possibly use this in the password field


@app.post("/register")
def register(body: RegisterBody):
    if not cardano_tools.verify_signature(
        body.signature, pyc.Address.from_primitive(body.stake_address)
    ):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    db.connect()
    User.create(email=body.email, stake_address=body.stake_address)
    db.commit()
    db.close()

    return {"Hello": "World"}


# class CreateOrganizationBody(BaseModel):
#     email: str
#     password: str
#     signature: str
#     user_type: UserType


# @app.post("/organization/create")
# def create_organization(body: CreateOrganizationBody):
#     print("body", body)

#     return {"Hello": "World"}
