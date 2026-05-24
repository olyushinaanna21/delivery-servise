from pydantic import BaseModel, field_validator
from typing import List, Optional


#функция проверки формата времени по длине
def check_time_format(time_str: str) -> bool:
    if len(time_str) != 11:
        return False

    #позиции разделителей "09:00-18:00"
    if time_str[2] != ":" or time_str[5] != "-" or time_str[8] != ":":
        return False

    #символы - цифры + нужные места
    if not (time_str[0:2].isdigit() and time_str[3:5].isdigit() and
            time_str[6:8].isdigit() and time_str[9:11].isdigit()):
        return False

    #проверка часов и минут
    start_hour = int(time_str[0:2])
    start_min = int(time_str[3:5])
    end_hour = int(time_str[6:8])
    end_min = int(time_str[9:11])

    if start_hour > 23 or end_hour > 23:
        return False
    if start_min > 59 or end_min > 59:
        return False

    return True



#создание модели курьера
class CourierItem(BaseModel):
    courier_id: int
    courier_type: str
    regions: List[int]
    working_hours: List[str]

    #проверка айди курьера больше 0
    @field_validator("courier_id")
    @classmethod
    def check_id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("courier_id должен быть положительным числом")
        return v

    #проверка типа курьера пеший, велик или машина
    @field_validator("courier_type")
    @classmethod
    def check_courier_type(cls, v: str) -> str:
        if v not in ["foot", "bike", "car"]:
            raise ValueError("courier_type должен быть foot, bike или car")
        return v

    #проверка регион больше 0
    @field_validator("regions")
    @classmethod
    def check_regions(cls, v: List[int]) -> List[int]:
        for region in v:
            if region <= 0:
                raise ValueError("ID региона должен быть положительным числом")
        return v

    #проверка формата времени работы
    @field_validator("working_hours")
    @classmethod
    def check_working_hours(cls, v: List[str]) -> List[str]:
        for hours in v:
            if not check_time_format(hours):
                raise ValueError(f"Неверный формат времени: {hours}")
        return v

    #проверка грузоподьемности, вычисляемое поле
    @property
    def max_load(self) -> int:
        loads = {"foot": 10, "bike": 15, "car": 50}
        return loads[self.courier_type]




class CouriersPostRequest(BaseModel):
    data: List[CourierItem]



#обновление курьера
class CourierUpdateRequest(BaseModel):
    courier_type: Optional[str] = None
    regions: Optional[List[int]] = None
    working_hours: Optional[List[str]] = None

    #тип курьера
    @field_validator("courier_type")
    @classmethod
    def check_courier_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["foot", "bike", "car"]:
            raise ValueError("courier_type должен быть foot, bike или car")
        return v

    #регион
    @field_validator("regions")
    @classmethod
    def check_regions(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None:
            for region in v:
                if region <= 0:
                    raise ValueError("ID региона должен быть положительным числом")
        return v

    #время работы
    @field_validator("working_hours")
    @classmethod
    def check_working_hours(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            for hours in v:
                if not check_time_format(hours):
                    raise ValueError(f"Неверный формат времени: {hours}")
        return v



#модель ответа
class CourierResponse(BaseModel):
    courier_id: int
    courier_type: str
    regions: List[int]
    working_hours: List[str]
    rating: Optional[float] = None
    earnings: int = 0