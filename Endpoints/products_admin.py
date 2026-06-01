#управление товарами (создание, редактирование, удаление)


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from auth import require_admin
from DB.DBconnect import get_db
from DB.tabels import ProductDB
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
def update_product(product_id: int, update_data: dict, admin=Depends(require_admin),  db: Session = Depends(get_db)):
    #ищем товар в бд
    product = db.query(ProductDB).filter(ProductDB.id_product == product_id).first()
    if not product:
        raise HTTPException(404, "Товар не найден")

    #обновляем только переданные поля
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

    return {"message": "Товар обновлен", "product": product}


#удалить товар(админ)
@router.delete("/{product_id}")
def delete_product(product_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id_product == product_id).first()
    if not product:
        raise HTTPException(404, "Товар не найден")

    db.delete(product)
    db.commit()

    return {"message": f"Товар {product_id} удален"}