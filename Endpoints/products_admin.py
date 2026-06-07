#управление товарами (создание, редактирование, удаление)


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from auth import require_admin
from DB.DBconnect import get_db
from DB.tabels import ProductDB, OrderItemDB, CartDB
from Models.product import Product

router = APIRouter(prefix="/admin/products", tags=["Управление товарами"])


#добавиьь новый товар(админ)
@router.post("", status_code=201)
def create_product(product: Product,admin=Depends(require_admin),db: Session = Depends(get_db)):
    #нет ли товара с таким айди
    existing = db.query(ProductDB).filter(ProductDB.id_product == product.id).first()
    if existing:
        raise HTTPException(400, "Товар с таким ID уже существует")

    #создаём товар в БД
    new_product = ProductDB(
        id_product=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        weight=product.weight,
        image_url=product.image_url,
        category=product.category
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "Товар добавлен", "product": product}



#редактировать товар(админ)
@router.patch("/{product_id}")
def update_product(product_id: int, update_data: dict, admin=Depends(require_admin), db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id_product == product_id).first()
    if not product:
        raise HTTPException(404, "Товар не найден")

    # обновляем поля
    if "name" in update_data:
        product.name = update_data["name"]
    if "description" in update_data:
        product.description = update_data["description"]
    if "price" in update_data:
        product.price = update_data["price"]
    if "weight" in update_data:
        product.weight = update_data["weight"]
    if "image_url" in update_data:
        product.image_url = update_data["image_url"]
    if "category" in update_data:
        product.category = update_data["category"]

    db.commit()
    db.refresh(product)

    # Возвращаем словарь
    return {
        "message": "Товар обновлен",
        "product": {
            "id": product.id_product,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "weight": product.weight,
            "image_url": product.image_url,
            "category": product.category
        }
    }


#удалить товар(админ)
@router.delete("/{product_id}")
def delete_product(product_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id_product == product_id).first()
    if not product:
        raise HTTPException(404, "Товар не найден")

    order_items = db.query(OrderItemDB).filter(OrderItemDB.id_product == product_id).first()
    if order_items:
        raise HTTPException(400, "Нельзя удалить товар, который уже есть в заказах")

    cart_items = db.query(CartDB).filter(CartDB.id_product == product_id).first()
    if cart_items:
        raise HTTPException(400, "Нельзя удалить товар, который находится в чьей-то корзине")

    db.delete(product)
    db.commit()

    return {"message": f"Товар {product_id} удален"}