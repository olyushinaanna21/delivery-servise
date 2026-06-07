from pydantic import BaseModel, field_validator
from typing import List, Optional
from Functions.helpFunc import check_time_format, round_weight

#модель заказа
class OrderItem(BaseModel):
    order_id: int
    weight: float
    region: int
    delivery_hours: List[str]
    address: str
    user_id: int
    status: str
    assigned_courier_id: Optional[int] = None
    assign_time: Optional[str] = None
    complete_time: Optional[str] = None

    @field_validator("order_id")
    @classmethod
    def check_order_id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("order_id должен быть положительным числом")
        return v

    @field_validator("weight")
    @classmethod
    def check_weight(cls, v: float) -> float:
        v = round_weight(v)
        if v < 0.01:
            raise ValueError("Вес заказа не может быть меньше 0.01 кг")
        if v > 50:
            raise ValueError("Вес заказа не может быть больше 50 кг")
        return v

    @field_validator("region")
    @classmethod
    def check_region_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Регион должен быть положительным числом")
        return v

    @field_validator("delivery_hours")
    @classmethod
    def check_delivery_hours(cls, v: List[str]) -> List[str]:
        for hours in v:
            if not check_time_format(hours):
                raise ValueError(f"Неверный формат времени: {hours}")
        return v


#оформление заказа из корзины покупателем
class CheckoutRequest(BaseModel):
    delivery_hours: List[str]
    address: str
    region: int

    @field_validator("delivery_hours")
    def check_delivery_hours(cls, v):
        for hours in v:
            if not check_time_format(hours):
                raise ValueError("Неверный формат времени")
        return v

    @field_validator("region")
    def check_region(cls, v):
        if v <= 0:
            raise ValueError("Регион должен быть > 0")
        return v


#завершение заказа(для курьера)
class CompleteOrderRequest(BaseModel):
    courier_id: int
    order_id: int
    complete_time: str


#одель запроса на создание заказа
# class OrdersPostRequest(BaseModel):
#     data: List[OrderItem]

#модель ответа при успешном создании
# class OrdersPostResponse(BaseModel):
#     orders: List[dict]


#назначение заказа
# class AssignOrdersRequest(BaseModel):
#     courier_id: int
#
#завершение заказа
# class CompleteOrderRequest(BaseModel):
#     courier_id: int
#     order_id: int
#     complete_time: str






