from app.model import User, UserType
from app.lib import cardano, environment

from jose import jwt
import datetime


ALGORITHM = environment.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = environment.get("ACCESS_TOKEN_EXPIRE_MINUTES", int)
SECRET_KEY = environment.get("SECRET_KEY")


async def authenticate_user(stake_address: str, signature: str) -> User | None:
    if not cardano.verify_signature(signature, stake_address):
        return None

    user = await User.filter(stake_address=stake_address).first()
    if not user:
        return None

    return user


def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def has_review_privileges(user: User):
    return user.type in [
        UserType.TEACHER.value,
        UserType.ORGANIZER.value,
        UserType.SUPERVISOR.value,
    ]
