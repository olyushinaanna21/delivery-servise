from pydantic import BaseModel, field_validator
from typing import Optional


#модель пользователя
class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    address: Optional[str] = None #только для покупателя
    region: Optional[int] = None #только для покупателя
    role: str #"customer", "admin", "courier"
    api_key: Optional[str] = None
    created_at: Optional[str] = None
