import requests
import time

BASE_URL = "http://localhost:8080"

from helpTest import (
    get_customer_key,
    get_admin_key,
    get_courier_key,
    headers,create_test_product_admin
)





#админ создает товар успешно
def test_create_product_success():
    admin_key = get_admin_key()
    unique_id = int(time.time()) % 10000

    product_data = {
        "id": unique_id,
        "name": "Новый тестовый товар",
        "description": "Описание нового товара",
        "price": 250,
        "weight": 1.2,
        "image_url": "https://example.com/new.jpg",
        "category": "electronics"
    }

    response = requests.post(f"{BASE_URL}/admin/products",json=product_data,headers=headers(admin_key))

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Товар добавлен"
    assert "product" in data
    assert data["product"]["id"] == unique_id
    assert data["product"]["name"] == "Новый тестовый товар"



#создание товара уже с существующим айди
def test_create_prduct_duplicate_id():

    admin_key = get_admin_key()

    product_id = create_test_product_admin()
    assert product_id is not None

    product_data = {
        "id": product_id,
        "name": "Дубликат",
        "description": "Дубликат товара",
        "price": 100,
        "weight": 0.5,
        "image_url": "https://example.com/dup.jpg",
        "category": "test"
    }

    response = requests.post(f"{BASE_URL}/admin/products",json=product_data,headers=headers(admin_key))

    assert response.status_code == 400
    assert "Товар с таким ID уже существует" in response.text


#создание товара без авторизации
def test_create_product_unauthorized():
    product_data = {
        "id": 1000,
        "name": "Неавторизованный товар",
        "description": "Должен быть отклонён",
        "price": 100,
        "weight": 0.5,
        "image_url": "https://example.com/test.jpg",
        "category": "test"
    }
    response = requests.post(f"{BASE_URL}/admin/products", json=product_data)
    assert response.status_code == 401

#создание товара с неверным ключом
def test_create_product_wrong_key():
    product_data = {
        "id": 1001,
        "name": "Неверный ключ",
        "description": "Должен быть отклонён",
        "price": 100,
        "weight": 0.5,
        "image_url": "https://example.com/test.jpg",
        "category": "test"
    }
    response = requests.post(
        f"{BASE_URL}/admin/products",json=product_data,headers=headers("wrong_key"))
    assert response.status_code == 403



#покупатель не может создавать товар
def test_create_product_as_customer():
    customer_key = get_customer_key()
    product_data = {
        "id": 1002,
        "name": "Покупательский товар",
        "description": "Должен быть отклонён",
        "price": 100,
        "weight": 0.5,
        "image_url": "https://example.com/test.jpg",
        "category": "test"
    }
    response = requests.post(f"{BASE_URL}/admin/products",json=product_data,headers=headers(customer_key))
    assert response.status_code == 403


#создание товара с отсутствующими полями
def test_create_product_missing_fields():
    admin_key = get_admin_key()

    product_data = {
        "id": 1003,
        "price": 100,
        "weight": 0.5
    }
    response = requests.post(f"{BASE_URL}/admin/products",json=product_data,headers=headers(admin_key))
    assert response.status_code == 422







#успешное обновление товара
def test_update_product_success():
    admin_key = get_admin_key()

    product_id = create_test_product_admin()
    assert product_id is not None


    update_data = {
        "name": "Обновлённое название",
        "price": 500,
        "category": "updated"
    }
    response = requests.patch(f"{BASE_URL}/admin/products/{product_id}",json=update_data,headers=headers(admin_key))

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Товар обновлен"
    assert data["product"]["name"] == "Обновлённое название"
    assert data["product"]["price"] == 500
    assert data["product"]["category"] == "updated"

#обновление несуществующего товара
def test_update_product_not_found():
    admin_key = get_admin_key()
    update_data = {"name": "Новое название"}
    response = requests.patch(f"{BASE_URL}/admin/products/99999",json=update_data,headers=headers(admin_key))
    assert response.status_code == 404
    assert "Товар не найден" in response.text


#обновление товара без авторизации
def test_update_product_unauthorized():
    update_data = {"name": "Новое название"}
    response = requests.patch(f"{BASE_URL}/admin/products/1", json=update_data)
    assert response.status_code == 401


#покупатель не имеет права обновлять товар
def test_update_product_as_customer():
    customer_key = get_customer_key()
    update_data = {"name": "Новое название"}
    response = requests.patch(f"{BASE_URL}/admin/products/1",json=update_data,headers=headers(customer_key))
    assert response.status_code == 403




#частичное обновление товара
def test_update_product_partial():
    admin_key = get_admin_key()

    product_id = create_test_product_admin()
    assert product_id is not None

    update_data = {"price": 999}
    response = requests.patch(f"{BASE_URL}/admin/products/{product_id}",json=update_data,headers=headers(admin_key))

    assert response.status_code == 200
    data = response.json()
    assert data["product"]["price"] == 999







#успешное удаление товара
def test_delete_product_success():
    admin_key = get_admin_key()

    product_id = create_test_product_admin()
    assert product_id is not None

    response = requests.delete(f"{BASE_URL}/admin/products/{product_id}",headers=headers(admin_key))

    assert response.status_code == 200
    assert f"Товар {product_id} удален" in response.json()["message"]

    customer_key = get_customer_key()
    get_response = requests.get(f"{BASE_URL}/products/{product_id}", headers=headers(customer_key))
    assert get_response.status_code == 404



#удаление несуществующего товара
def test_delete_product_not_found():
    admin_key = get_admin_key()
    response = requests.delete(f"{BASE_URL}/admin/products/99999",headers=headers(admin_key))
    assert response.status_code == 404
    assert "Товар не найден" in response.text


#удаление товара без авторизации
def test_delete_product_unauthorized():
    response = requests.delete(f"{BASE_URL}/admin/products/1")
    assert response.status_code == 401


#покупатель не может удалить товар
def test_delete_product_as_customer():
    customer_key = get_customer_key()
    response = requests.delete(f"{BASE_URL}/admin/products/1",headers=headers(customer_key))
    assert response.status_code == 403


#курьер не может удалить товар
def test_delete_product_as_courier():
    courier_key = get_courier_key()
    if courier_key:
        response = requests.delete(f"{BASE_URL}/admin/products/1",headers=headers(courier_key))
        assert response.status_code == 403

