#управление курьерами для администратора

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from auth import require_admin, generate_api_key, API_KEYS
from DB.DBconnect import get_db
from DB.tabels import UserDB, CourierDB, OrderDB
from Models.courier_admin import CourierUpdateRequest, CourierResponse, CreateCourierRequest
from Functions.helpFunc import get_capacity, is_order_compatible, calculate_courier_earnings, calculate_courier_rating, check_time_format
from datetime import datetime


router = APIRouter(prefix="/couriers", tags=["Курьеры"])


#создание курьера (пользователь(юзер с ролью курьер)+профиль курьера)
@router.post("", status_code=201)
def create_courier(request: CreateCourierRequest,admin=Depends(require_admin),db: Session = Depends(get_db)):
    #проверка уникальности пользователя
    existing_user = db.query(UserDB).filter((UserDB.username == request.username) | (UserDB.email == request.email)).first()

    if existing_user:
        if existing_user.username == request.username:
            raise HTTPException(400, "Username уже занят")
        if existing_user.email == request.email:
            raise HTTPException(400, "Email уже зарегистрирован")

    #генерация апи ключа
    api_key = generate_api_key()

    #создание пользователя
    new_user = UserDB(
        username=request.username,
        email=request.email,
        password=request.password,
        address=None,
        region=None,
        role="courier",
        api_key=api_key,
        created_at=datetime.now()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    #создание профиля курьера
    new_courier = CourierDB(
        id_user=new_user.id_user,
        courier_type=request.courier_type,
        regions=request.regions,
        working_hours=request.working_hours,
        max_load=request.max_load
    )
    db.add(new_courier)
    db.commit()

    #активация ключа
    API_KEYS[api_key] = {
        "role": "courier",
        "user_id": new_user.id_user,
        "username": request.username
    }

    return {
        "message": "Курьер успешно создан",
        "user_id": new_user.id_user,
        "username": request.username,
        "password": request.password,
        "api_key": api_key
    }



#список всех курьеров(админ)
@router.get("")
def get_all_couriers(admin=Depends(require_admin), db: Session = Depends(get_db)):
    couriers = db.query(CourierDB).all()

    result = []
    for courier in couriers:
        result.append({
            "courier_id": courier.id_courier,
            "courier_type": courier.courier_type,
            "regions": courier.regions,
            "working_hours": courier.working_hours,
            "max_load": courier.max_load
        })
    return {"couriers": result, "total": len(result)}




#обновление курьера(админ)(при изменении снимает неподходящие заказы)
@router.patch("/{courier_id}")
def update_courier(courier_id: int,update_data: CourierUpdateRequest,admin=Depends(require_admin),db: Session = Depends(get_db)):
    #ищем курьера
    courier = db.query(CourierDB).filter(CourierDB.id_courier == courier_id).first()
    if not courier:
        raise HTTPException(404, "Курьер не найден")

    #создаём копию для проверки совместимости
    courier_copy = {
        "courier_id": courier.id_courier,
        "courier_type": courier.courier_type,
        "regions": courier.regions,
        "working_hours": courier.working_hours,
        "max_load": courier.max_load
    }

    #применяем обновления к копии
    if update_data.courier_type is not None:
        courier_copy["courier_type"] = update_data.courier_type
    if update_data.regions is not None:
        courier_copy["regions"] = update_data.regions
    if update_data.working_hours is not None:
        courier_copy["working_hours"] = update_data.working_hours

    #снимаем неподходящие заказы (исправлено: id_courier вместо assigned_courier_id)
    orders = db.query(OrderDB).filter(OrderDB.id_courier == courier_id,OrderDB.status == "assigned").all()

    for order in orders:
        if not is_order_compatible(order.__dict__, courier_copy):
            order.status = "available"
            order.id_courier = None
            order.assign_time = None

    #обновляем курьера
    if update_data.courier_type is not None:
        courier.courier_type = update_data.courier_type
        courier.max_load = get_capacity(update_data.courier_type)
    if update_data.regions is not None:
        courier.regions = update_data.regions
    if update_data.working_hours is not None:
        courier.working_hours = update_data.working_hours

    db.commit()

    return {
        "courier_id": courier.id_courier,
        "courier_type": courier.courier_type,
        "regions": courier.regions,
        "working_hours": courier.working_hours
    }


#информация о курьере рейтинг и заработок(для всех админ, курьер, покупатель)
@router.get("/{courier_id}", response_model=CourierResponse)
def get_courier(courier_id: int, db: Session = Depends(get_db)):
    courier = db.query(CourierDB).filter(CourierDB.id_courier == courier_id).first()
    if not courier:
        raise HTTPException(404, "Курьер не найден")


    earnings = calculate_courier_earnings(courier_id, courier.courier_type, db)
    rating = calculate_courier_rating(courier_id, db)

    return {
        "courier_id": courier.id_courier,
        "courier_type": courier.courier_type,
        "regions": courier.regions,
        "working_hours": courier.working_hours,
        "rating": rating,
        "earnings": earnings
    }


#удаление курьера(админ)
@router.delete("/{courier_id}")
def delete_courier(courier_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    courier = db.query(CourierDB).filter(CourierDB.id_courier == courier_id).first()
    if not courier:
        raise HTTPException(404, "Курьер не найден")

    #снимаем все заказы с этого курьера
    orders = db.query(OrderDB).filter(OrderDB.id_courier == courier_id).all()
    for order in orders:
        order.id_courier = None
        order.status = "available"
        order.assign_time = None

    #удаляем профиль курьера
    db.delete(courier)
    db.commit()

    return {"message": f"Курьер {courier_id} удален"}