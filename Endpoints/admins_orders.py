#администратор(управление заказами)

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session  # ← ДОБАВИТЬ
from auth import require_admin
from DB.DBconnect import get_db
from DB.tabels import OrderDB
from Fuctions.helpFunc import get_current_time_iso

router = APIRouter(prefix="/admin", tags=["Админ"])


# получить все заказы(админ)
@router.get("/orders")
def get_all_orders(admin=Depends(require_admin),db: Session = Depends(get_db)):
    orders = db.query(OrderDB).all()

    result = []
    for order in orders:
        result.append({
            "order_id": order.id_order,
            "weight": order.weight,
            "region": order.region,
            "delivery_hours": order.delivery_hours,
            "status": order.status,
            "assigned_courier_id": order.assigned_courier_id,
            "assign_time": order.assign_time,
            "complete_time": order.complete_time,
            "user_id": order.id_user,
            "address": order.address
        })

    return {"orders": result, "total": len(result)}



#отмениьь заказ(админ)
@router.patch("/orders/{order_id}/cancel")
def cancel_order(order_id: int, admin=Depends(require_admin),db: Session = Depends(get_db)):
    order = db.query(OrderDB).filter(OrderDB.id_order == order_id).first()
    if not order:
        raise HTTPException(404, "Заказ не найден")

    if order.status == "completed":
        raise HTTPException(400, "Нельзя отменить выполненный заказ")

    #отменяем заказ
    order.status = "cancelled"
    order.assigned_courier_id = None
    order.assign_time = None

    db.commit()

    return {"message": f"Заказ {order_id} отменен"}
