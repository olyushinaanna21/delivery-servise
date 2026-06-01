#работа курьера (профиль, заказы, статистика)

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from auth import require_courier
from DB.DBconnect import get_db
from DB.tabels import CourierDB, OrderDB
from Fuctions.helpFunc import calculate_courier_earnings, calculate_courier_rating
from datetime import datetime

router = APIRouter(prefix="/courier", tags=["Курьер"])


#профиль курьера
@router.get("/me")
def get_my_profile(current_user = Depends(require_courier), db: Session = Depends(get_db)):
    courier_id = current_user["user_id"]

    #ищем профиль курьера
    courier = db.query(CourierDB).filter(CourierDB.id_courier == courier_id).first()
    if not courier:
        raise HTTPException(404, "Курьер не найден")

    earnings = calculate_courier_earnings(courier_id, courier.courier_type, {})  # временно
    rating = calculate_courier_rating(courier_id, {})

    return {
        "courier_id": courier.id_courier,
        "courier_type": courier.courier_type,
        "regions": courier.regions,
        "working_hours": courier.working_hours,
        "max_load": courier.max_load,
        "earnings": earnings,
        "rating": rating
    }


#получить доступные заказы
@router.get("/orders/available")
def get_available_orders(current_user = Depends(require_courier),db: Session = Depends(get_db)):
    orders = db.query(OrderDB).filter(OrderDB.status == "available").all()

    available_orders = []
    for order in orders:
        available_orders.append({
            "order_id": order.id_order,
            "weight": order.weight,
            "region": order.region,
            "delivery_hours": order.delivery_hours
        })

    return {"orders": available_orders, "total": len(available_orders)}



#взять себе заказ с проверкой грузоподьемности
@router.post("/orders/take/{order_id}")
def take_order(order_id: int, current_user=Depends(require_courier), db: Session = Depends(get_db)):
    courier_id = current_user["user_id"]

    #существование заказа
    order = db.query(OrderDB).filter(OrderDB.id_order == order_id).first()
    if not order:
        raise HTTPException(404, "Заказ не найден")

    #доступность заказа
    if order.status != "available":
        raise HTTPException(400, "Заказ уже назначен или выполнен")

    #существование курьера
    courier = db.query(CourierDB).filter(CourierDB.id_courier == courier_id).first()
    if not courier:
        raise HTTPException(404, "Курьер не найден")

    max_load = courier.max_load

    #вес отдельного заказа
    if order.weight > max_load:
        raise HTTPException(400, f"Вес заказа ({order.weight} кг) превышает грузоподъемность ({max_load} кг)")

    #суммарный вес уже взятых заказов
    my_orders = db.query(OrderDB).filter( OrderDB.assigned_courier_id == courier_id,OrderDB.status == "assigned").all()

    current_total_weight = sum(o.weight for o in my_orders)

    #проверка грузоподъёмности
    if current_total_weight + order.weight > max_load:
        raise HTTPException(400,f"Нельзя взять заказ: суммарный вес ({current_total_weight} + {order.weight} = {current_total_weight + order.weight} кг) превысит грузоподъемность ({max_load} кг)")

    #назначаем заказ
    order.status = "assigned"
    order.assigned_courier_id = courier_id
    order.assign_time = datetime.now()

    db.commit()

    return {"message": f"Заказ {order_id} взят", "order_id": order_id}



#просмотр активных заказов(которые взял)
@router.get("/orders/my")
def get_my_orders(current_user = Depends(require_courier),db: Session = Depends(get_db)):
    courier_id = current_user["user_id"]

    orders = db.query(OrderDB).filter( OrderDB.assigned_courier_id == courier_id,OrderDB.status == "assigned").all()

    my_orders = []
    for order in orders:
        my_orders.append({
            "order_id": order.id_order,
            "weight": order.weight,
            "region": order.region,
            "delivery_hours": order.delivery_hours,
            "assign_time": order.assign_time
        })

    return {"orders": my_orders, "total": len(my_orders)}



#выполнение заказа комплит + время
@router.post("/orders/complete/{order_id}")
def complete_order(order_id: int, current_user = Depends(require_courier), db: Session = Depends(get_db)):
    courier_id = current_user["user_id"]

    order = db.query(OrderDB).filter(OrderDB.id_order == order_id).first()
    if not order:
        raise HTTPException(404, "Заказ не найден")

    if order.assigned_courier_id != courier_id:
        raise HTTPException(403, "Это не ваш заказ")

    if order.status != "assigned":
        raise HTTPException(400, "Заказ нельзя выполнить")

    order.status = "completed"
    order.complete_time = datetime.now()

    db.commit()

    return {"message": f"Заказ {order_id} выполнен", "order_id": order_id}


#заработок и рейтинг
@router.get("/earnings")
def get_my_earnings(current_user = Depends(require_courier),db: Session = Depends(get_db)):
    courier_id = current_user["user_id"]

    courier = db.query(CourierDB).filter(CourierDB.id_courier == courier_id).first()
    if not courier:
        raise HTTPException(404, "Курьер не найден")

    earnings = calculate_courier_earnings(courier_id, courier.courier_type, {})  # временно

    return {"earnings": earnings}


@router.get("/rating")
def get_my_rating(current_user = Depends(require_courier),db: Session = Depends(get_db)):
    courier_id = current_user["user_id"]

    courier = db.query(CourierDB).filter(CourierDB.id_courier == courier_id).first()
    if not courier:
        raise HTTPException(404, "Курьер не найден")

    rating = calculate_courier_rating(courier_id, {})  # временно

    return {"rating": rating}