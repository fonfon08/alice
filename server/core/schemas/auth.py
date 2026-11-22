from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    operator_key: str = ""
    user: str = ""
    pass_: str = Field(default="", alias="pass")
    secret: str = ""
