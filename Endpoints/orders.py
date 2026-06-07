#заказы для покупателя (оформление, просмотр)



from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from Models.order import CheckoutRequest
from auth import require_customer
from DB.DBconnect import get_db
from DB.tabels import OrderDB, OrderItemDB, CartDB, ProductDB
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["Заказы"])



#оформление заказа(покупатель)
@router.post("/checkout")
def checkout(request: CheckoutRequest, current_user = Depends(require_customer),db: Session = Depends(get_db)):
    user_id = current_user["user_id"]

    #получаем корзину из бд
    cart_items = db.query(CartDB).filter(CartDB.id_user == user_id).all()

    if not cart_items:
        raise HTTPException(400, "Корзина пуста")

    #считаем общий вес и сумму
    total_weight = 0
    total_price = 0

    for item in cart_items:
        product = db.query(ProductDB).filter(ProductDB.id_product == item.id_product).first()
        if product:
            total_weight += product.weight * item.quantity
            total_price += product.price * item.quantity

    total_weight = round(total_weight, 2)
    total_price = round(total_price, 2)

    #создаём заказ в бд
    order_number = db.query(OrderDB).count() + 1

    new_order = OrderDB(
        order_number=order_number,
        id_user=user_id,
        weight=total_weight,
        region=request.region,
        address=request.address,
        delivery_hours=request.delivery_hours,
        status="available",
        total_price=total_price,
        created_at=datetime.now()
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    #добавляем товары
    for item in cart_items:
        product = db.query(ProductDB).filter(ProductDB.id_product == item.id_product).first()
        if product:
            order_item = OrderItemDB(
                id_order=new_order.id_order,
                id_product=item.id_product,
                product_name=product.name,
                quantity=item.quantity,
                price_at_time=product.price,
                weight_at_time=product.weight
            )
            db.add(order_item)

    db.commit()

    #очищаем корзину
    db.query(CartDB).filter(CartDB.id_user == user_id).delete()
    db.commit()

    return {
        "message": "Заказ оформлен",
        "order_id": new_order.id_order,
        "total_price": total_price
    }


#просмотр заказов(мои заказы) покупатель
@router.get("/my")
def get_my_orders(current_user = Depends(require_customer), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]

    orders = db.query(OrderDB).filter(OrderDB.id_user == user_id).all()

    my_orders = []
    for order in orders:
        my_orders.append({
            "order_id": order.id_order,
            "weight": order.weight,
            "region": order.region,
            "address": order.address,
            "delivery_hours": order.delivery_hours,
            "status": order.status,
            "total_price": order.total_price,
            "created_at": order.created_at
        })

    return {"orders": my_orders, "total": len(my_orders)}


#детали заказа(покупатель)
@router.get("/my/{order_id}")
def get_my_order_detail(order_id: int, current_user = Depends(require_customer), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]

    #ищем заказ
    order = db.query(OrderDB).filter(OrderDB.id_order == order_id).first()
    if not order:
        raise HTTPException(404, "Заказ не найден")

    #проверяем, что заказ принадлежит пользователю
    if order.id_user != user_id:
        raise HTTPException(403, "Это не ваш заказ")

    #получаем товары в заказе
    items = db.query(OrderItemDB).filter(OrderItemDB.id_order == order_id).all()

    items_list = []
    for item in items:
        items_list.append({
            "product_id": item.id_product,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "price_at_time": item.price_at_time,
            "weight_at_time": item.weight_at_time
        })

    return {
        "order_id": order.id_order,
        "user_id": order.id_user,
        "weight": order.weight,
        "region": order.region,
        "address": order.address,
        "delivery_hours": order.delivery_hours,
        "status": order.status,
        "total_price": order.total_price,
        "created_at": order.created_at,
        "items": items_list
    }