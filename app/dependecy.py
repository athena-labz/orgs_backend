from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError

from lib import environment
from model import User
import specs


ALGORITHM = environment.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = environment.get("ACCESS_TOKEN_EXPIRE_MINUTES", int)
SECRET_KEY = environment.get("SECRET_KEY")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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

        token_data = specs.TokenDataSpec(username=username)
    except JWTError:
        raise credentials_exception

    user = await User.filter(stake_address=token_data.username).first()
    if user is None:
        raise credentials_exception

    pydantic_user = await specs.UserSpec.from_tortoise_orm(user)

    return pydantic_user


async def get_current_active_user(
    current_user: Annotated[specs.UserSpec, Depends(get_current_user)]
):
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
