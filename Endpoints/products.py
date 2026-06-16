#просмотр товаров (каталог)


from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from auth import verify_api_key
from DB.DBconnect import get_db
from DB.tabels import ProductDB

router = APIRouter(prefix="/products", tags=["Товары"])

#получить все товары с фильтром по товару и по категории
@router.get("")
def get_products(search: Optional[str] = None,category: Optional[str] = None,api_key=Depends(verify_api_key),db: Session = Depends(get_db)):
    query = db.query(ProductDB)

    #фильтр по категории
    if category:
        query = query.filter(ProductDB.category == category)

    #получаем товары
    products = query.all()

    #фильтр по названию
    if search:
        result = []
        for product in products:
            if search.lower() in product.name.lower():
                result.append(product)
        products = result

    return {
        "products": [
            {
                "id": p.id_product,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "weight": p.weight,
                "image_url": p.image_url,
                "category": p.category
            }
            for p in products
        ],
        "total": len(products)
    }


#получить товар по айди
@router.get("/{product_id}")
def get_product(product_id: int, api_key=Depends(verify_api_key), db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id_product == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    return {
        "id": product.id_product,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "weight": product.weight,
        "image_url": product.image_url,
        "category": product.category
    }


#получить список категорий
@router.get("/categories/all")
def get_categories(api_key=Depends(verify_api_key),db: Session = Depends(get_db)):
    #уникальные категории из бд
    categories = db.query(ProductDB.category).distinct().all()


    categories_list = []
    for category in categories:
        if category[0]:
            categories_list.append(category[0])
    return {"categories": categories_list}