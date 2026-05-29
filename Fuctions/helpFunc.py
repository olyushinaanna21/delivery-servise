# функция проверки формата времени по длине
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




#округление веса до 2 знаков
def round_weight(weight: float) -> float:
    return round(weight, 2)




#функция получения списка всех доступных заказов (статсу авелибл)
def get_available_orders(orders_db: dict) -> list:
    result = []
    for order in orders_db.values():
        if order.get("status") == "available":
            result.append(order)
    return result



#функция получения назначенных, но не завершенных заказов курьера
def get_courier_assigned_orders(courier_id: int, orders_db: dict) -> list:
    result = []
    for order in orders_db.values():
        if order.get("assigned_courier_id") != courier_id:
            continue
        if order.get("status") != "assigned":
            continue
        result.append(order)
    return result




#фильтрация заказов по весу, району, времени
def filter_compatible_orders(orders: list, courier: dict) -> list:
    compatible = []
    for order in orders:
        if is_order_compatible(order, courier):
            compatible.append(order)
    return compatible





#фунцкция получает текущее время
def get_current_time_iso() -> str:
    from datetime import datetime
    return datetime.now().isoformat()