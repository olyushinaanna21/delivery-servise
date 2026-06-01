#управление пользователями (просмотр всех+заказы, смена роли)


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from auth import require_admin
from DB.DBconnect import get_db
from DB.tabels import UserDB, OrderDB


router = APIRouter(prefix="/admin/users", tags=["Управление пользователями"])


#получить всех пользователей(админ)
@router.get("")
def get_all_users(admin=Depends(require_admin),db: Session = Depends(get_db)):
    users = db.query(UserDB).all()

    result = []
    for user in users:
        result.append({
            "id": user.id_user,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "address": user.address,
            "region": user.region,
            "created_at": user.created_at
        })
    return {"users": result, "total": len(result)}


#получить любого пользователя по айди(админ)
@router.get("/{user_id}")
def get_user_by_id(user_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
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


#изменить роль пользователя(админ)
@router.patch("/{user_id}/role")
def change_role(user_id: int, role: str, admin=Depends(require_admin), db: Session = Depends(get_db)):
    if role not in ["customer", "admin", "courier"]:
        raise HTTPException(400, "Неверная роль")

    user = db.query(UserDB).filter(UserDB.id_user == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    user.role = role
    db.commit()

    return {"message": f"Роль изменена на {role}"}



#получить заказы пользователя(админ)
@router.get("/{user_id}/orders")
def get_user_orders_by_admin(user_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id_user == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

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