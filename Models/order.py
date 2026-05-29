from pydantic import BaseModel, field_validator
from typing import List, Optional
from Fuctions.helpFunc import check_time_format, round_weight

#модель заказа
class OrderItem(BaseModel):
    order_id: int
    weight: float
    region: int
    delivery_hours: List[str]

    #айди положительный
    @field_validator("order_id")
    @classmethod
    def check_order_id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("order_id должен быть положительным числом")
        return v


    #вес от 0,01 до 50
    @field_validator("weight")
    @classmethod
    def check_weight(cls, v: float) -> float:
        v = round_weight(v)

        if v < 0.01:
            raise ValueError("Вес заказа не может быть меньше 0.01 кг")
        if v > 50:
            raise ValueError("Вес заказа не может быть больше 50 кг")
        return v


    #регион больше 0
    @field_validator("region")
    @classmethod
    def check_region_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Регион должен быть положительным числом")
        return v


    #формат времени
    @field_validator("delivery_hours")
    @classmethod
    def check_delivery_hours(cls, v: List[str]) -> List[str]:
        for hours in v:
            if not check_time_format(hours):
                raise ValueError(f"Неверный формат времени: {hours}")
        return v


#одель запроса на создание заказа
class OrdersPostRequest(BaseModel):
    data: List[OrderItem]

#модель ответа при успешном создании
class OrdersPostResponse(BaseModel):
    orders: List[dict]


#назначение заказа
class AssignOrdersRequest(BaseModel):
    courier_id: int

#завершение заказа
class CompleteOrderRequest(BaseModel):
    courier_id: int
    order_id: int
    complete_time: str  # ISO формат: "2021-01-10T10:33:01.42Z"

