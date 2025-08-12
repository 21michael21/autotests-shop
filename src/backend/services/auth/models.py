from pydantic import BaseModel, Field, validator

class RegisterRequest(BaseModel):
    username: str = Field(min_length=6, pattern='^[a-zA-Z0-9]+$')
    password: str = Field(min_length=8)

    @validator('password')
    def validate_password(cls, v: str) -> str:
        if not (any((c.isupper() for c in v)) and any((c.islower() for c in v)) and any((not c.isalnum() for c in v))):
            raise ValueError('Password does not match criteria')
        return v

class LoginResponse(BaseModel):
    token: str
