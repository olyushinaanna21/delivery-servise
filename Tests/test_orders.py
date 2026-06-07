import requests
import time

BASE_URL = "http://localhost:8080"

from helpTest import (
    get_customer_key,
    get_admin_key,
    get_courier_key,
    headers,
    create_test_product,
    clear_cart, add_to_cart, create_test_order, create_test_user,
    create_test_product_with_custom_price_weight
)






#успешное оформление заказа
def test_checkout_success():
    customer_key = get_customer_key()
    product_id = create_test_product()

    clear_cart(customer_key)

    add_to_cart(customer_key, product_id, 2)

    checkout_data = {
        "delivery_hours": ["09:00-12:00"],
        "address": "ул. Тестовая, 10",
        "region": 5
    }
    response = requests.post(f"{BASE_URL}/orders/checkout",json=checkout_data,headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Заказ оформлен"
    assert "order_id" in data
    assert "total_price" in data
    assert data["total_price"] == 200



#оформление заказа с пустой корзиной
def test_checkout_empty_cart():
    customer_key = get_customer_key()

    clear_cart(customer_key)

    checkout_data = {
        "delivery_hours": ["09:00-12:00"],
        "address": "ул. Тестовая, 10",
        "region": 5
    }
    response = requests.post(f"{BASE_URL}/orders/checkout",json=checkout_data,headers=headers(customer_key))

    assert response.status_code == 400
    assert "Корзина пуста" in response.text




#оформление заказа без авторизации
def test_checkout_unauthorized():
    checkout_data = {
        "delivery_hours": ["09:00-12:00"],
        "address": "ул. Тестовая, 10",
        "region": 5
    }
    response = requests.post(f"{BASE_URL}/orders/checkout", json=checkout_data)
    assert response.status_code == 401



#админ не оформляет заказ
def test_checkout_as_admin():
    admin_key = get_admin_key()
    checkout_data = {
        "delivery_hours": ["09:00-12:00"],
        "address": "ул. Тестовая, 10",
        "region": 5
    }
    response = requests.post(f"{BASE_URL}/orders/checkout",json=checkout_data,headers=headers(admin_key))
    assert response.status_code == 403


#курьер не оформляет заказ
def test_checkout_as_courier():
    courier_key = get_courier_key()
    if courier_key:
        checkout_data = {
            "delivery_hours": ["09:00-12:00"],
            "address": "ул. Тестовая, 10",
            "region": 5
        }
        response = requests.post(f"{BASE_URL}/orders/checkout",json=checkout_data,headers=headers(courier_key))
        assert response.status_code == 403


#оформленеие заказа без всех нужных полей
def test_checkout_missing_fields():
    customer_key = get_customer_key()
    product_id = create_test_product()

    clear_cart(customer_key)
    add_to_cart(customer_key, product_id, 1)

    checkout_data = {"delivery_hours": ["09:00-12:00"],"region": 5}
    response = requests.post(f"{BASE_URL}/orders/checkout",json=checkout_data,headers=headers(customer_key))
    assert response.status_code == 422







#покупатель получает список своих заказов
def test_get_my_orders_success():
    customer_key = get_customer_key()

    order_id = create_test_order()

    response = requests.get(f"{BASE_URL}/orders/my", headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert "total" in data
    assert isinstance(data["orders"], list)


    #проверяем что заказ в списке
    if order_id:
        found = False
        for order in data["orders"]:
            if order["order_id"] == order_id:
                found = True
                assert "status" in order
                assert "total_price" in order
                break
        if found:
            print(f"Заказ {order_id} найден в списке")




#покупатель получает пустой список заказов
def test_get_my_orders_empty():

    user_id, username = create_test_user()

    login_response = requests.post(f"{BASE_URL}/auth/login",json={"username": username, "password": "test123"})

    assert login_response.status_code == 200
    new_customer_key = login_response.json()["api_key"]

    response = requests.get(f"{BASE_URL}/orders/my", headers=headers(new_customer_key))

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert isinstance(data["orders"], list)
    assert len(data["orders"]) == 0


#просмотр заказов без авторизации
def test_get_my_orders_unauthorized():
    response = requests.get(f"{BASE_URL}/orders/my")
    assert response.status_code == 401



#админ не может посмотреть свои заказы(у него их не может быть)
def test_get_my_orders_as_admin():
    admin_key = get_admin_key()
    response = requests.get(f"{BASE_URL}/orders/my", headers=headers(admin_key))
    assert response.status_code in [200, 403]







#покупатель смотрит детали заказа
def test_get_my_order_detail_success():
    customer_key = get_customer_key()

    order_id = create_test_order()
    assert order_id is not None, "Не удалось создать заказ"

    response = requests.get(f"{BASE_URL}/orders/my/{order_id}",headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert "user_id" in data
    assert "weight" in data
    assert "region" in data
    assert "address" in data
    assert "delivery_hours" in data
    assert "status" in data
    assert "total_price" in data
    assert "created_at" in data
    assert "items" in data
    assert isinstance(data["items"], list)




#покупатель смотрит несуществующий заказ
def test_get_my_order_detail_not_found():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/orders/my/99999",headers=headers(customer_key))
    assert response.status_code == 404
    assert "Заказ не найден" in response.text


#покупатель смотрит чужой заказ
def test_get_my_order_detail_not_mine():
    customer_key = get_customer_key()

    order_id = create_test_order()

    user_id, username = create_test_user()


    login_response = requests.post(f"{BASE_URL}/auth/login",json={"username": username, "password": "test123"})
    assert login_response.status_code == 200
    other_customer_key = login_response.json()["api_key"]

    response = requests.get(f"{BASE_URL}/orders/my/{order_id}",headers=headers(other_customer_key))

    assert response.status_code == 403
    assert "Это не ваш заказ" in response.text




#просмотр деталей заказа без авторизации
def test_get_my_order_detail_unauthorized():
    response = requests.get(f"{BASE_URL}/orders/my/1")
    assert response.status_code == 401









#проверка что товары в заказе такие же как товары в корзине
def test_order_items_correct():
    customer_key = get_customer_key()
    product_id = create_test_product()

    clear_cart(customer_key)

    add_to_cart(customer_key, product_id, 3)

    checkout_data = {
        "delivery_hours": ["09:00-12:00"],
        "address": "ул. Тестовая, 1",
        "region": 5
    }
    checkout_response = requests.post(f"{BASE_URL}/orders/checkout",json=checkout_data,headers=headers(customer_key))

    assert checkout_response.status_code == 200
    order_id = checkout_response.json()["order_id"]

    detail_response = requests.get(f"{BASE_URL}/orders/my/{order_id}",headers=headers(customer_key))

    assert detail_response.status_code == 200
    data = detail_response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 3
    assert data["items"][0]["price_at_time"] == 100
    assert data["total_price"] == 300
    assert data["weight"] == 1.5






#проверка расчета общего веса заказа
def test_checkout_calculates_weight_correctly():
    customer_key = get_customer_key()

    product1 = create_test_product_with_custom_price_weight(price=100, weight=1.5)
    product2 = create_test_product_with_custom_price_weight(price=200, weight=2.3)

    clear_cart(customer_key)
    add_to_cart(customer_key, product1, 2)  # 3
    add_to_cart(customer_key, product2, 3)  # 6.9

    checkout_data = {
        "delivery_hours": ["09:00-12:00"],
        "address": "ул. Тестовая, 1",
        "region": 5
    }

    response = requests.post(f"{BASE_URL}/orders/checkout", json=checkout_data, headers=headers(customer_key))
    assert response.status_code == 200

    order_id = response.json()["order_id"]
    detail = requests.get(f"{BASE_URL}/orders/my/{order_id}", headers=headers(customer_key))
    assert detail.json()["weight"] == 9.9