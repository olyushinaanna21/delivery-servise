from fastapi import APIRouter, HTTPException
from Models.courier import CouriersPostRequest, CourierUpdateRequest, CourierResponse


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



#-----
#функция проверки грузоподьемности курьера
def get_capacity(courier_type: str) -> int:
    loads = {"foot": 10, "bike": 15, "car": 50}
    return loads.get(courier_type, 10)

#функция преобразования времени в минуты
def time_to_minutes(time_str: str) -> int:
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

#функция пересечения времени (для времени работы)
def has_time_overlap(time1: str, time2: str) -> bool:
    start1, end1 = time1.split('-')
    start2, end2 = time2.split('-')

    s1 = time_to_minutes(start1)
    e1 = time_to_minutes(end1)
    s2 = time_to_minutes(start2)
    e2 = time_to_minutes(end2)

    return not (e1 <= s2 or e2 <= s1)



#функция проверки подходит ли заказ курьеру вес, район, время
def is_order_compatible(order: dict, courier: dict) -> bool:
    capacity = get_capacity(courier["courier_type"])
    if order["weight"] > capacity:
        return False

    if order["region"] not in courier["regions"]:
        return False

    for courier_hour in courier["working_hours"]:
        for order_hour in order["delivery_hours"]:
            if has_time_overlap(courier_hour, order_hour):
                return True
    return False



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





#------
#функция расчета заработка курьера(сумма*(500 * C))(foot=2, bike=5, car=9)
def calculate_courier_earnings(courier_id: int, courier_type: str, orders_db: dict) -> int:
    coeffs = {"foot": 2, "bike": 5, "car": 9}
    coefficient = coeffs.get(courier_type, 2) #по умолч пеший

    earnings = 0

    for order in orders_db.values():
        #только завершенные заказы
        if (order.get("status") == "completed" and
                order.get("assigned_courier_id") == courier_id):
            earnings += 500 * coefficient

    return earnings


#функция расчета времени доставки (в сек)
def calculate_delivery_time(assign_time: str, complete_time: str) -> int:
    from datetime import datetime

    assign_dt = datetime.fromisoformat(assign_time)
    complete_dt = datetime.fromisoformat(complete_time)

    #расчет разницы
    delta = complete_dt - assign_dt
    return int(delta.total_seconds())



#функция расчета рейтинга курьера ((3600 - min(t, 3600)) / 3600 * 5)
#t -мин сред время доставки по районам (в сек)
def calculate_courier_rating(courier_id: int, orders_db: dict) -> float | None:
    #список завершенных курьером заказов
    completed_orders = []
    for order in orders_db.values():
        if (order.get("status") == "completed" and
                order.get("assigned_courier_id") == courier_id and
                order.get("assign_time") and
                order.get("complete_time")):
            completed_orders.append(order)


    if not completed_orders:
        return None

    #сортировка по времени назначения
    completed_orders.sort(key=lambda x: x.get("assign_time", ""))

    #групирровка времени доставки по районам
    region_times = {}
    previous_complete_time = None

    for order in completed_orders:
        region = order["region"]
        assign_time = order["assign_time"]
        complete_time = order["complete_time"]

        #время доставки первого заказа от назнач до заверш
        if previous_complete_time is None:
            delivery_time = calculate_delivery_time(assign_time, complete_time)
        else:
            #время между предыдущим заверешнием и начало следующего
            delivery_time = calculate_delivery_time(previous_complete_time, complete_time)


        if region not in region_times:
            region_times[region] = []
        region_times[region].append(delivery_time)

        previous_complete_time = complete_time

    #вычисление среднего времени по каждому району
    region_averages = []
    for times in region_times.values():
        if times:
            avg = sum(times) / len(times)
            region_averages.append(avg)

    if not region_averages:
        return None

    t = min(region_averages)

    #рассчитываем рейтинг
    rating = (3600 - min(t, 3600)) / 3600 * 5
    rating = round(rating, 2)

    return rating



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