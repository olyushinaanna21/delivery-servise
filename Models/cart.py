from pydantic import BaseModel
from typing import List

#один товар
class CartItem(BaseModel):
    product_id: int #айди товара
    name: str #название
    price: float #цена
    weight: float #вес
    quantity: int #количество штук


#корзина покупателя
class Cart(BaseModel):
    user_id: int #айди пользоваткеля
    items: List[CartItem] # список товаров в корзине
    total_price: float #итоговая цена
    total_weight: float #итоговый вес