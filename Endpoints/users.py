#просмотр и обновление профилей пользователей(каждый видит, редактирует только себя)

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from auth import get_current_user
from DB.DBconnect import get_db
from DB.tabels import UserDB, OrderDB


router = APIRouter(prefix="/users", tags=["Пользователи"])


#получить свой профиль
@router.get("/{user_id}")
def get_user(user_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    #только свой
    if current_user["user_id"] != user_id:
        raise HTTPException(403, "Нельзя смотреть чужой профиль")

    user = db.query(UserDB).filter(UserDB.id_user == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    return {
        "id": user.id_user,
        "username": user.username,
        "email": user.email,
        "address": user.address,
        "region": user.region,
        "role": user.role,
        "created_at": user.created_at
    }


#редактировать профиль только свой
@router.patch("/{user_id}")
def update_user(user_id: int, update_data: dict, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["user_id"] != user_id:
        raise HTTPException(403, "Нельзя редактировать чужой профиль")

    user = db.query(UserDB).filter(UserDB.id_user == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    # обновляем только переданные поля
    if "address" in update_data:
        user.address = update_data["address"]
    if "region" in update_data:
        user.region = update_data["region"]
    if "email" in update_data:
        user.email = update_data["email"]
    if "password" in update_data:
        user.password = update_data["password"]

    db.commit()

    return {"message": "Профиль обновлен"}


#получить заказы
@router.get("/{user_id}/orders")
def get_user_orders(user_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["user_id"] != user_id:
        raise HTTPException(403, "Нельзя смотреть чужие заказы")

    # проверяем существование ли пользователь
    user = db.query(UserDB).filter(UserDB.id_user == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    # получаем заказы пользователя из бд
    orders = db.query(OrderDB).filter(OrderDB.id_user == user_id).all()

    user_orders = []
    for order in orders:
        user_orders.append({
            "order_id": order.id_order,
            "weight": order.weight,
            "region": order.region,
            "status": order.status,
            "total_price": order.total_price,
            "created_at": order.created_at
        })

    return {"orders": user_orders, "total": len(user_orders)}