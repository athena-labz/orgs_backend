from pydantic import BaseModel
from enum import Enum
from model import UserSpec


# Token
class TokenSpec(BaseModel):
    access_token: str
    token_type: str

class TokenDataSpec(BaseModel):
    username: str | None = None

# Register
class UserTypeSpec(Enum):
    STUDENT = 0
    TEACHER = 1
    ORGANIZER = 2

class RegisterBodySpec(BaseModel):
    user_type: UserTypeSpec
    email: str
    stake_address: str
    signature: str