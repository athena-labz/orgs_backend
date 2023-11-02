from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from tortoise.contrib.fastapi import register_tortoise
from tortoise.expressions import Q

from model import User, UserType, Organization, OrganizationType
from lib import cardano, auth, environment, utils

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
    pydantic_user = await specs.UserSpec.from_tortoise_orm(current_user)
    return pydantic_user


@app.post("/users/register", response_model=specs.UserSpec)
async def register(body: specs.RegisterBodySpec):
    if not cardano.verify_signature(body.signature, body.stake_address):
        raise HTTPException(status_code=400, detail="Invalid signature")

    user = await User.filter(
        Q(stake_address=body.stake_address) | Q(email=body.email)
    ).first()
    if user is not None:
        raise HTTPException(status_code=400, detail="Stake address or email taken")

    user = await User.create(
        type=body.user_type.value, email=body.email, stake_address=body.stake_address
    )
    pydantic_user = await specs.UserSpec.from_tortoise_orm(user)

    return pydantic_user


@app.post("/users/confirm/email")
async def confirm_email(
    email_validation_string: str,
    current_user: Annotated[User, Depends(dependecy.get_current_user)],
):
    if current_user.active:
        raise HTTPException(status_code=400, detail="Email already verified")

    if email_validation_string != current_user.email_validation_string:
        await current_user.update_from_dict(
            {"email_validation_string": utils.string_generator()}
        )
        await current_user.save()

        raise HTTPException(status_code=400, detail="Wrong email string")

    await current_user.update_from_dict({"active": True})
    await current_user.save()

    return {"message": "Successfully confirmed the email"}


@app.post("/organization/create", response_model=specs.OrganizationSpec)
async def organization_create(
    current_user: Annotated[User, Depends(dependecy.get_current_active_user)],
    body: specs.CreateOrganizationBodySpec,
):
    if not current_user.type == UserType.ORGANIZER.value:
        raise HTTPException(status_code=400, detail="User not of type organizer")

    existing_organization = await Organization.filter(
        identifier=body.identifier
    ).first()
    if existing_organization is not None:
        raise HTTPException(status_code=400, detail="Organization identifier taken")

    organization = await Organization.create(
        identifier=body.identifier,
        type=body.organization_type.value,
        name=body.name,
        description=body.description,
        students_password=body.students_password,
        teachers_password=body.teachers_password,
        areas=body.areas,
        admin=current_user,
    )
    pydantic_organization = await specs.OrganizationSpec.from_tortoise_orm(organization)

    return pydantic_organization


register_tortoise(app, db_url=DATABASE, modules={"models": ["model"]})
