#корзина покупателя


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from auth import require_customer
from DB.DBconnect import get_db
from DB.tabels import CartDB, ProductDB
from datetime import datetime



router = APIRouter(prefix="/cart", tags=["Корзина"])


#получить корзину
@router.get("")
def get_cart(current_user=Depends(require_customer),db: Session = Depends(get_db)):
    user_id = current_user["user_id"]

    #получаем все товары в корзине из бд
    cart_items = db.query(CartDB).filter(CartDB.id_user == user_id).all()

    items = []
    total_price = 0
    total_weight = 0

    for item in cart_items:
        product = db.query(ProductDB).filter(ProductDB.id_product == item.id_product).first()
        if product:
            items.append({
                "product_id": item.id_product,
                "name": product.name,
                "price": product.price,
                "weight": product.weight,
                "quantity": item.quantity
            })
            total_price += product.price * item.quantity
            total_weight += product.weight * item.quantity

    return {
        "user_id": user_id,
        "items": items,
        "total_price": total_price,
        "total_weight": total_weight
    }


#добавить товар в корзину
@router.post("/add")
def add_to_cart(product_id: int,quantity: int = 1,current_user=Depends(require_customer), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]

    # проверка существования товара
    product = db.query(ProductDB).filter(ProductDB.id_product == product_id).first()
    if not product:
        raise HTTPException(404, "Товар не найден")

    # проверяем, есть ли уже такой товар в корзине
    existing_item = db.query(CartDB).filter(
        CartDB.id_user == user_id,
        CartDB.id_product == product_id
    ).first()

    if existing_item:
        #если естьувеличиваем количество
        existing_item.quantity += quantity
    else:
        #если нет создаём новую запись
        new_item = CartDB(
            id_user=user_id,
            id_product=product_id,
            quantity=quantity,
            added_at=datetime.now()
        )
        db.add(new_item)

    db.commit()

    return {"message": "Товар добавлен в корзину"}


#изменение кол-ва товара
@router.patch("/update")
def update_quantity(product_id: int,quantity: int,current_user=Depends(require_customer),db: Session = Depends(get_db)):
    user_id = current_user["user_id"]

    #ищем товар в корзине
    cart_item = db.query(CartDB).filter(CartDB.id_user == user_id,CartDB.id_product == product_id).first()

    if not cart_item:
        raise HTTPException(404, "Товар не найден в корзине")

    if quantity <= 0:
        #удаляем товар из корзины
        db.delete(cart_item)
    else:
        #обновляем количество
        cart_item.quantity = quantity

    db.commit()

    return {"message": "Количество обновлено"}


#удалить товар из корзины
@router.delete("/remove/{product_id}")
def remove_from_cart(product_id: int,current_user=Depends(require_customer),db: Session = Depends(get_db)):
    user_id = current_user["user_id"]

    #ищем товар в корзине
    cart_item = db.query(CartDB).filter(  CartDB.id_user == user_id,CartDB.id_product == product_id).first()

    if not cart_item:
        raise HTTPException(404, "Товар не найден в корзине")

    db.delete(cart_item)
    db.commit()

    return {"message": "Товар удален из корзины"}


#очистить всю корзину
@router.delete("/clear")
def clear_cart(current_user=Depends(require_customer),db: Session = Depends(get_db)):
    user_id = current_user["user_id"]

    #удаляем все товары пользователя из корзины
    db.query(CartDB).filter(CartDB.id_user == user_id).delete()
    db.commit()

    return {"message": "Корзина очищена"}