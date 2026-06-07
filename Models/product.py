from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    weight: float
    image_url: Optional[str] = None
    category: Optional[str] = None