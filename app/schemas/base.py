import orjson
from pydantic import BaseModel
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrjsonBaseModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class HTTPExceptionResponse(OrjsonBaseModel):
    detail: str

class ValidationError(BaseModel):
    loc: List[Union[str, int]] = Field(..., title='Location')
    msg: str = Field(..., title='Message')
    type: str = Field(..., title='Error Type')

class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = Field(None, title='Detail')