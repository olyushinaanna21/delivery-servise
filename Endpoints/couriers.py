from fastapi import APIRouter, HTTPException
from Models.courier import CouriersPostRequest, CourierUpdateRequest, CourierResponse
from Fuctions.helpFunc import get_capacity, is_order_compatible, calculate_courier_earnings, calculate_courier_rating

router = APIRouter(prefix="/couriers", tags=["Курьеры"])
couriers_db = {}
orders_db = {}


#добавление курьера
@router.post("", status_code=201)
def create_couriers(request: CouriersPostRequest):
    successful = [] #успешные курьеры
    failed = [] #ошибочные курьеры
    seen_ids = set() #уникальность айди

    #проход по всем курьерам из запроса
    for courier in request.data:


        #1 - дубликат внутри запроса
        if courier.courier_id in seen_ids:
            failed.append({"id": courier.courier_id})
            continue

        #2 - курьер с таким id уже есть в бд
        if courier.courier_id in couriers_db:
            failed.append({"id": courier.courier_id})
            continue

        #сохранение курьера
        seen_ids.add(courier.courier_id)
        couriers_db[courier.courier_id] = {
            "courier_id": courier.courier_id,
            "courier_type": courier.courier_type,
            "regions": courier.regions,
            "working_hours": courier.working_hours,
            "max_load": courier.max_load
        }
        successful.append({"id": courier.courier_id})

    #при ошибках 400 + фейлд список
    if failed:
        raise HTTPException(
            status_code=400,
            detail={
                "validation_error": {
                    "couriers": failed
                }
            }
        )

    # успешно 201 и список успешных курьеров
    return {"couriers": successful}




#обновление информации о курьере, при изменении снимаем неподходящие заказы
@router.patch("/{courier_id}")
def update_courier(courier_id: int, update_data: CourierUpdateRequest):
    #1 - существование курьера
    if courier_id not in couriers_db:
        raise HTTPException(status_code=404, detail="Курьер не найден")

    #2 - текущий курьер, копия чтобы не изменять раньше времени бд
    courier = couriers_db[courier_id].copy()

    #3 - применение обновлений, к копии
    if update_data.courier_type is not None:
        courier["courier_type"] = update_data.courier_type

    if update_data.regions is not None:
        courier["regions"] = update_data.regions

    if update_data.working_hours is not None:
        courier["working_hours"] = update_data.working_hours


    #проверка неподходящих заказов курьеру
    freed_orders = []

    for order_id, order in orders_db.items():
        if order.get("assigned_courier_id") == courier_id and order.get("status") == "assigned":
            if not is_order_compatible(order, courier):
                order["status"] = "available"
                order["assigned_courier_id"] = None
                order["assign_time"] = None
                freed_orders.append(order_id)

    #5- записываем созранения в бд в оригинал
    if update_data.courier_type is not None:
        couriers_db[courier_id]["courier_type"] = update_data.courier_type
        couriers_db[courier_id]["max_load"] = get_capacity(update_data.courier_type)

    if update_data.regions is not None:
        couriers_db[courier_id]["regions"] = update_data.regions

    if update_data.working_hours is not None:
        couriers_db[courier_id]["working_hours"] = update_data.working_hours

    #6 - ответ измененная информация
    return {
        "courier_id": courier_id,
        "courier_type": couriers_db[courier_id]["courier_type"],
        "regions": couriers_db[courier_id]["regions"],
        "working_hours": couriers_db[courier_id]["working_hours"]
    }


#получение информации о курьере
@router.get("/{courier_id}", response_model=CourierResponse)
def get_courier(courier_id: int):
    if courier_id not in couriers_db:
        raise HTTPException(status_code=404, detail="Курьер не найден")

    courier = couriers_db[courier_id]

    #расчет заработка
    earnings = calculate_courier_earnings(
        courier_id,
        courier["courier_type"],
        orders_db
    )

    #расчет рейтинга
    rating = calculate_courier_rating(courier_id, orders_db)

    return {
        "courier_id": courier_id,
        "courier_type": courier["courier_type"],
        "regions": courier["regions"],
        "working_hours": courier["working_hours"],
        "rating": rating,
        "earnings": earnings
    }