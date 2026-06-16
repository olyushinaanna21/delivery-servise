#общие вспомогательные методы для тестовых файлов

import requests
import time

BASE_URL = "http://localhost:8080"



#авторизация как админ и возврат его апи ключа
def get_admin_key():
    response = requests.post(f"{BASE_URL}/auth/login",json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["api_key"]



#авторизация как покупатель и возврат его апи ключа
def get_customer_key():
    response = requests.post(f"{BASE_URL}/auth/login",json={"username": "testcustomer", "password": "123456"})
    assert response.status_code == 200
    return response.json()["api_key"]



#авторизация как курьер и возврат его апи ключа(курьера может не быть)
def get_courier_key():
    response = requests.post(f"{BASE_URL}/auth/login",json={"username": "courier1", "password": "12345678"})
    if response.status_code == 200:
        return response.json()["api_key"]
    return None



#возвращает словарь по апи ключу, который нужно передать в headers= при отправке запроса
def headers(key):
    return {"API-Token": key}



#создание тестового товара и возврат его айди
def create_test_product():
    admin_key = get_admin_key() #только админ
    headers_admin = {"API-Token": admin_key}

    product_data = {
        "id": 998,
        "name": "Тестовый товар",
        "description": "Для тестирования",
        "price": 100,
        "weight": 0.5,
        "image_url": "https://example.com/test.jpg",
        "category": "test"
    }

    response = requests.post(f"{BASE_URL}/admin/products",json=product_data,headers=headers_admin)
    return 998



#создает тестовый заказ(через корзину) и возвращает его айди
def create_test_order():
    customer_key = get_customer_key() #только покупатель
    headers_customer = {"API-Token": customer_key}

    product_id = create_test_product()

    requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": 1},headers=headers_customer)

    checkout_data = {
        "delivery_hours": ["09:00-12:00"],
        "address": "ул. Тестовая, 1",
        "region": 5
    }

    response = requests.post(f"{BASE_URL}/orders/checkout",json=checkout_data,headers=headers_customer)
    assert response.status_code == 200
    return response.json()["order_id"]



#создание тестового пользователя, возврат айди и юзернейм
def create_test_user():
    unique_username = f"test_user_{int(time.time())}"
    user_data = {
        "username": unique_username,
        "email": f"{unique_username}@test.com",
        "password": "test123",
        "address": "ул. Тестовая, 10",
        "region": 1
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    assert response.status_code == 201
    return response.json()["user_id"], unique_username



#получение ключа покупателя по юзернейм и паролю
def get_customer_key_by_username(username, password):
    response = requests.post(f"{BASE_URL}/auth/login",json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["api_key"]



#очистка корзины пользователя
def clear_cart(customer_key):
    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(customer_key))

#добавление товара в корзину
def add_to_cart(customer_key, product_id, quantity=1):
    return requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": quantity},headers=headers(customer_key))



#создание тестового курьера(курьер айди, юзер айди, юзернейм)
def create_test_courier():
    admin_key = get_admin_key()
    unique_username = f"test_courier_{int(time.time())}"


    response = requests.post(
        f"{BASE_URL}/couriers",
        json={
            "username": unique_username,
            "password": "test123",
            "email": f"{unique_username}@test.com",
            "courier_type": "foot",
            "regions": [1, 2, 3],
            "working_hours": ["09:00-18:00"]
        },
        headers=headers(admin_key)
    )

    if response.status_code == 201:
        user_id = response.json()["user_id"]

        list_response = requests.get(f"{BASE_URL}/couriers", headers=headers(admin_key))
        if list_response.status_code == 200:
            couriers = list_response.json()["couriers"]
            if couriers:
                courier_id = couriers[-1]["courier_id"]
                return courier_id, user_id, unique_username

    return None, None, None



#создает тестовый товар и возвращает айди
def create_test_product_admin():
    admin_key = get_admin_key()
    unique_id = int(time.time()) % 10000

    product_data = {
        "id": unique_id,
        "name": f"Тестовый товар {unique_id}",
        "description": "Для тестирования управления товарами",
        "price": 100,
        "weight": 0.5,
        "image_url": "https://example.com/test.jpg",
        "category": "test"
    }

    response = requests.post(
        f"{BASE_URL}/admin/products",
        json=product_data,
        headers=headers(admin_key)
    )

    if response.status_code == 201:
        return unique_id
    return None




#создает тестового покупателя и возвращает юзер айди, юзер нейм, кей
def create_test_customer():
    user_id, username = create_test_user()

    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": "test123"}
    )
    assert login_response.status_code == 200
    api_key = login_response.json()["api_key"]

    return user_id, username, api_key




#создание тестового покупателя и возвращает айди
def create_test_user_id():
    unique_username = f"test_user_{int(time.time())}"
    user_data = {
        "username": unique_username,
        "email": f"{unique_username}@test.com",
        "password": "test123",
        "address": "ул. Тестовая, 10",
        "region": 1
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    assert response.status_code == 201
    return response.json()["user_id"]



#создает заказ для конкретного пользователя по его ключу
def create_test_order_for_user(user_key):
    product_id = create_test_product()
    clear_cart(user_key)
    add_to_cart(user_key, product_id, 1)

    checkout_data = {
        "delivery_hours": ["09:00-12:00"],
        "address": "ул. Тестовая, 1",
        "region": 5
    }
    response = requests.post(f"{BASE_URL}/orders/checkout", json=checkout_data, headers=headers(user_key))
    assert response.status_code == 200
    return response.json()["order_id"]



#создание заказа с указанным весом
def create_test_order_with_weight(weight=1.0):
    customer_key = get_customer_key()
    admin_key = get_admin_key()

    test_response = requests.get(f"{BASE_URL}/admin/users", headers=headers(admin_key))
    if test_response.status_code != 200:
        admin_key = get_admin_key()


    import time
    unique_id = int(time.time() * 1000) % 100000


    product_data = {
        "id": unique_id,
        "name": f"Товар весом {weight}кг",
        "description": "Для теста грузоподъёмности",
        "price": 100,
        "weight": weight,
        "image_url": "https://example.com/test.jpg",
        "category": "test"
    }

    response = requests.post(f"{BASE_URL}/admin/products", json=product_data, headers=headers(admin_key))
    assert response.status_code == 201, f"Ошибка создания товара: {response.text}"


    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(customer_key))

    response = requests.post(f"{BASE_URL}/cart/add", params={"product_id": unique_id, "quantity": 1}, headers=headers(customer_key))
    assert response.status_code == 200


    checkout_data = {
        "delivery_hours": ["09:00-12:00"],
        "address": "ул. Тестовая, 1",
        "region": 5
    }

    response = requests.post(f"{BASE_URL}/orders/checkout", json=checkout_data, headers=headers(customer_key))
    assert response.status_code == 200

    order_id = response.json()["order_id"]

    return order_id



#тестовый товар с заданным весом и ценой
def create_test_product_with_custom_price_weight(price=100, weight=0.5):
    admin_key = get_admin_key()
    import time
    unique_id = int(time.time() * 1000) % 100000

    product_data = {
        "id": unique_id,
        "name": f"Товар {price}р {weight}кг",
        "description": "Для тестирования",
        "price": price,
        "weight": weight,
        "image_url": "https://example.com/test.jpg",
        "category": "test"
    }

    response = requests.post(f"{BASE_URL}/admin/products", json=product_data, headers=headers(admin_key))
    assert response.status_code == 201, f"Ошибка создания товара: {response.text}"

    return unique_id



#очистка бд перед каждым тестом(иначе накладываются друг на друга и падают)
import psycopg2
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "delivery",
    "user": "postgres",
    "password": "postgres"
}


def cleanup_database():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()


        cur.execute("DELETE FROM order_items;")
        cur.execute("DELETE FROM orders;")
        cur.execute("DELETE FROM carts;")


        cur.execute("DELETE FROM products WHERE category = 'test' OR id_product > 100;")


        cur.execute("DELETE FROM couriers WHERE id_courier != 1;")


        cur.execute("DELETE FROM users WHERE id_user NOT IN (1, 2, 3);")


        cur.execute("ALTER SEQUENCE users_id_user_seq RESTART WITH 4;")
        cur.execute("ALTER SEQUENCE couriers_id_courier_seq RESTART WITH 2;")
        cur.execute("ALTER SEQUENCE products_id_product_seq RESTART WITH 100;")
        cur.execute("ALTER SEQUENCE orders_id_order_seq RESTART WITH 1;")

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка очистки бд: {e}")

