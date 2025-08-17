from pydantic import BaseModel, Field, validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=6, pattern="^[a-zA-Z0-9]+$")
    password: str = Field(min_length=8)

    @validator("password")
    def validate_password(cls, val_passw: str) -> str:
        if not (
            any((c.isupper() for c in val_passw))
            and any((c.islower() for c in val_passw))
            and any((not c.isalnum() for c in val_passw))
        ):
            raise ValueError("Пароль не соответствует критериям")
        return val_passw


class LoginResponse(BaseModel):
    token: str
