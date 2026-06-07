import requests
import time

BASE_URL = "http://localhost:8080"

from helpTest import (
    get_customer_key,
    get_admin_key,
    get_courier_key,
    headers, create_test_product
)



#получение списка всех товаров (авторизованный)
def test_get_all_products_success():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/products", headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total" in data
    assert isinstance(data["products"], list)


#получение товаров без авторизации
def test_get_all_products_unauthorized():
    response = requests.get(f"{BASE_URL}/products")
    assert response.status_code == 401

#получение с неверным ключом
def test_get_all_products_wrong_key():
    response = requests.get(f"{BASE_URL}/products", headers=headers("wrong_key"))
    assert response.status_code == 403

#админ получает список товаров
def test_get_all_products_as_admin():
    admin_key = get_admin_key()
    response = requests.get(f"{BASE_URL}/products", headers=headers(admin_key))
    assert response.status_code == 200


#курьер получает список товаров
def test_get_all_products_as_courier():
    courier_key = get_courier_key()
    if courier_key:
        response = requests.get(f"{BASE_URL}/products", headers=headers(courier_key))
        assert response.status_code == 200










#фильтрация товара по категории
def test_get_products_by_category():
    customer_key = get_customer_key()

    create_test_product()

    response = requests.get(f"{BASE_URL}/products?category=special",headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total" in data


    for product in data["products"]:
        assert product["category"] == "special"


#фильтрация по несуществующей категории
def test_get_products_by_nonexistent_category():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/products?category=nonexistent",headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["products"]) == 0








#поиск товаров по названию
def test_search_products_by_name():
    customer_key = get_customer_key()

    create_test_product()

    response = requests.get(f"{BASE_URL}/products?search=Уникальный",headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total" in data

    for product in data["products"]:
        assert "уникальный" in product["name"].lower()


#поиск несуществующего товара
def test_search_products_not_found():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/products?search=несуществующийтовар12345",headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["products"]) == 0


#поиск товара без учета регистра
def test_search_products_case_insensitive():
    customer_key = get_customer_key()
    create_test_product()

    response_lower = requests.get(f"{BASE_URL}/products?search=уникальный",headers=headers(customer_key))

    response_upper = requests.get(f"{BASE_URL}/products?search=УНИКАЛЬНЫЙ",headers=headers(customer_key))

    assert response_lower.status_code == 200
    assert response_upper.status_code == 200

    assert response_lower.json()["total"] == response_upper.json()["total"]







#фильтрация по категории и по поиску одновременно

def test_get_products_with_category_and_search():
    customer_key = get_customer_key()

    response = requests.get(f"{BASE_URL}/products?category=test&search=Тестовый",headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total" in data

    for product in data["products"]:
        assert product["category"] == "test"
        assert "тестовый" in product["name"].lower()







#получение товара по айди
def test_get_product_by_id_success():
    customer_key = get_customer_key()

    create_test_product()

    response = requests.get(f"{BASE_URL}/products/998", headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 998
    assert "name" in data
    assert "price" in data
    assert "weight" in data
    assert "category" in data



#получение несуществующего товара по айди
def test_get_product_by_id_not_found():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/products/99999", headers=headers(customer_key))

    assert response.status_code == 404
    assert "Товар не найден" in response.text

#получение товара по айди без авторизации
def test_get_product_by_id_unauthorized():
    response = requests.get(f"{BASE_URL}/products/1")
    assert response.status_code == 401

#получение товара по айди с неверным ключом
def test_get_product_by_id_wrong_key():
    response = requests.get(f"{BASE_URL}/products/1", headers=headers("wrong_key"))
    assert response.status_code == 403

#получение товара с отрицательным айди
def test_get_product_by_id_negative():
    customer_key = get_customer_key()

    response = requests.get(f"{BASE_URL}/products/-1", headers=headers(customer_key))

    assert response.status_code in [400, 404, 422]






#получение списка категорий
def test_get_categories_success():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/products/categories/all", headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert isinstance(data["categories"], list)


#получение категорий без авторизации
def test_get_categories_unauthorized():
    response = requests.get(f"{BASE_URL}/products/categories/all")
    assert response.status_code == 401

#получение категории с неверным ключом
def test_get_categories_wrong_key():
    response = requests.get(f"{BASE_URL}/products/categories/all", headers=headers("wrong_key"))
    assert response.status_code == 403



#админ получает список категорий
def test_get_categories_as_admin():
    admin_key = get_admin_key()
    response = requests.get(f"{BASE_URL}/products/categories/all", headers=headers(admin_key))
    assert response.status_code == 200



#проверка что категория есть в списке
def test_get_categories_contains_test_category():

    customer_key = get_customer_key()

    create_test_product()

    response = requests.get(f"{BASE_URL}/products/categories/all", headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert "test" in data["categories"] or "test" in str(data["categories"])
