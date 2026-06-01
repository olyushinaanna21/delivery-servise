from pydantic import BaseModel


#моделька товара
class Product(BaseModel):
    id: int #айди
    name: str #название
    description: str #описание
    price: float #цена
    weight: float # вес в кг
    image_url: str #ссылка на кратинку
    category: str #категория товара
