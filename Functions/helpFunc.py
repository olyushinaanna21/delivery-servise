from sqlalchemy.orm import Session
from DB.tabels import OrderDB
from datetime import datetime


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
def calculate_courier_earnings(courier_id: int, courier_type: str, db: Session) -> int:
    coeffs = {"foot": 2, "bike": 5, "car": 9}
    coefficient = coeffs.get(courier_type, 2)

    #считаем завершённые заказы курьера в бд
    completed_count = db.query(OrderDB).filter(OrderDB.id_courier == courier_id,OrderDB.status == "completed").count()

    return completed_count * 500 * coefficient




#функция расчета времени доставки (в сек)
def calculate_delivery_time(assign_time, complete_time) -> int:
    from datetime import datetime

    if isinstance(assign_time, str):
        assign_dt = datetime.fromisoformat(assign_time)
    else:
        assign_dt = assign_time

    if isinstance(complete_time, str):
        complete_dt = datetime.fromisoformat(complete_time)
    else:
        complete_dt = complete_time

    #расчет разницы
    delta = complete_dt - assign_dt
    return int(delta.total_seconds())




#функция расчета рейтинга курьера ((3600 - min(t, 3600)) / 3600 * 5)
#t -мин сред время доставки по районам (в сек)
def calculate_courier_rating(courier_id: int, db: Session) -> float:
    # получаем завершённые заказы из бд (все заказы курьера с пометкой комлитед)
    completed_orders = db.query(OrderDB).filter(
        OrderDB.id_courier == courier_id,
        OrderDB.status == "completed",
        OrderDB.assign_time.isnot(None),
        OrderDB.complete_time.isnot(None)
    ).order_by(OrderDB.assign_time).all()

    if not completed_orders:
        return 0.0

    # группировка времени доставки по районам
    region_times = {}
    previous_complete_time = None#время завершения предыдущего заказа

    for order in completed_orders:
        region = order.region
        assign_time = order.assign_time
        complete_time = order.complete_time

        if previous_complete_time is None:
            # время доставки первого заказа
            delivery_time = calculate_delivery_time(assign_time, complete_time)
        else:
            # время между завершением предыдущего и текущего
            delivery_time = calculate_delivery_time(previous_complete_time, complete_time)

        if region not in region_times:
            region_times[region] = []
        region_times[region].append(delivery_time)

        previous_complete_time = complete_time

    # вычисление среднего времени по каждому району
    region_averages = []
    for times in region_times.values():
        if times:
            region_averages.append(sum(times) / len(times))

    if not region_averages:
        return 0.0

    t = min(region_averages)

    # рассчитываем рейтинг
    rating = (3600 - min(t, 3600)) / 3600 * 5
    rating = round(rating, 2)

    return rating


#округление веса до 2 знаков
def round_weight(weight: float) -> float:
    return round(weight, 2)


#фунцкция получает текущее время
def get_current_time_iso() -> str:
    from datetime import datetime
    return datetime.now().isoformat()