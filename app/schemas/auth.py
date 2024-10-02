from pydantic import Field
from schemas.base import OrjsonBaseModel


class Credentials(OrjsonBaseModel):
    username: str = Field(title="Email")
    password: str = Field(title="Password")


class Token(OrjsonBaseModel):
    token: str


class RefreshToken(OrjsonBaseModel):
    refresh_token: str


class TwoTokens(RefreshToken):
    access_token: str
