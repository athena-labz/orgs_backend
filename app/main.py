from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from tortoise.contrib.fastapi import register_tortoise

from model import User
from lib import cardano, auth, environment

import dependecy
import specs

import pycardano as pyc
import datetime


ACCESS_TOKEN_EXPIRE_MINUTES = environment.get("ACCESS_TOKEN_EXPIRE_MINUTES", int)
DATABASE = environment.get("DATABASE")


# https://fastapi.tiangolo.com
# https://fastapi.tiangolo.com/tutorial/bigger-applications/
app = FastAPI()


@app.post("/token", response_model=specs.TokenSpec)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.stake_address}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=specs.UserSpec)
async def read_users_me(
    current_user: Annotated[specs.UserSpec, Depends(dependecy.get_current_active_user)]
):
    return current_user


@app.post("/register")
async def register(body: specs.RegisterBodySpec):
    if not cardano.verify_signature(body.signature, body.stake_address):
        raise HTTPException(status_code=400, detail="Invalid signature")

    user = await User.create(email=body.email, stake_address=body.stake_address)
    pydantic_user = await specs.UserSpec.from_tortoise_orm(user)

    return pydantic_user


# class CreateOrganizationBody(BaseModel):
#     email: str
#     password: str
#     signature: str
#     user_type: UserType


# @app.post("/organization/create")
# def create_organization(body: CreateOrganizationBody):
#     print("body", body)

#     return {"Hello": "World"}


register_tortoise(app, db_url=DATABASE, modules={"models": ["model"]})
