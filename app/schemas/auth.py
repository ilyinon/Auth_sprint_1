from pydantic import Field
from schemas.base import OrjsonBaseModel


class Credentials(OrjsonBaseModel):
    username: str = Field(title="Email")
    password: str = Field(title="Password")


class RefreshToken(OrjsonBaseModel):
    refresh_token: str


class TwoTokens(RefreshToken):
    access_token: str


class UserLoginModel(OrjsonBaseModel):
    email: str = Field()
    password: str = Field()


class Payload(OrjsonBaseModel):
    user: str
    roles: list
    exp: int
    jti: str
    refresh: bool
