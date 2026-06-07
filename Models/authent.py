from pydantic import BaseModel, field_validator
from typing import Optional

#модель запроса на вход
class LoginRequest(BaseModel):
    username: str
    password: str

#модель запроса на регистрацию
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    address: str
    region: int

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Имя пользователя должно быть не менее 2 символов")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if len(v) < 4:
            raise ValueError("Email должен быть не менее 4 символов")
        if "@" not in v:
            raise ValueError("Email должен содержать символ @")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Пароль должен быть не менее 6 символов")
        return v


