import requests
import time
from helpTest import (
    get_admin_key,
    get_customer_key,
    get_courier_key,
    create_test_order,
    headers,
    create_test_user, create_test_user_id
)
BASE_URL = "http://localhost:8080"



#администратор получает список всех пользователей
def test_get_all_users_success():
    admin_key = get_admin_key()
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers(admin_key))

    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert isinstance(data["users"], list)


#без ключа доступ запрещен
def test_get_all_users_unauthorized():
    response = requests.get(f"{BASE_URL}/admin/users")
    assert response.status_code == 401



#с неверным ключом доступ запрещен
def test_get_all_users_wrong_key():
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers("wrong_key"))
    assert response.status_code == 403


#покупатель не имеет доступ
def test_get_all_users_as_customer():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers(customer_key))
    assert response.status_code == 403

#курьер не имеет доступ
def test_get_all_users_as_courier():
    courier_key = get_courier_key()
    if courier_key:
        response = requests.get(f"{BASE_URL}/admin/users", headers=headers(courier_key))
        assert response.status_code == 403








#получение пользователя по айди админ
def test_get_user_by_id_success():
    admin_key = get_admin_key()

    #создаём тестового пользователя
    user_id = create_test_user_id()

    response = requests.get(f"{BASE_URL}/admin/users/{user_id}", headers=headers(admin_key))

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert "username" in data
    assert "email" in data
    assert "role" in data



#получение несуществующего пользователя
def test_get_user_by_id_not_found():
    admin_key = get_admin_key()
    response = requests.get(f"{BASE_URL}/admin/users/99999", headers=headers(admin_key))

    assert response.status_code == 404
    assert "Пользователь не найден" in response.text


#нет доступа без ключа
def test_get_user_by_id_unauthorized():
    response = requests.get(f"{BASE_URL}/admin/users/1")
    assert response.status_code == 401



#покупатель не может получить доступ
def test_get_user_by_id_as_customer():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/admin/users/1", headers=headers(customer_key))
    assert response.status_code == 403








#успешное изменение роли
def test_change_role_success():
    admin_key = get_admin_key()
    user_id = create_test_user_id()

    response = requests.patch(f"{BASE_URL}/admin/users/{user_id}/role?role=courier",headers=headers(admin_key))

    assert response.status_code == 200
    assert response.json()["message"] == "Роль изменена на courier"

    check_response = requests.get(f"{BASE_URL}/admin/users/{user_id}", headers=headers(admin_key))
    assert check_response.json()["role"] == "courier"



#назначение неверной роли(несуществующей)
def test_change_role_invalid():
    admin_key = get_admin_key()
    user_id = create_test_user_id()

    response = requests.patch(f"{BASE_URL}/admin/users/{user_id}/role?role=invalid_role",headers=headers(admin_key))

    assert response.status_code == 400
    assert "Неверная роль" in response.text



#изменение роли несуществующего пользователя
def test_change_role_user_not_found():
    admin_key = get_admin_key()

    response = requests.patch(f"{BASE_URL}/admin/users/99999/role?role=courier",headers=headers(admin_key))

    assert response.status_code == 404
    assert "Пользователь не найден" in response.text


#без ключа нельзя сменить роль
def test_change_role_unauthorized():
    response = requests.patch(f"{BASE_URL}/admin/users/1/role?role=admin")
    assert response.status_code == 401

#покупатель не может сменить роль он не админ
def test_change_role_as_customer():
    customer_key = get_customer_key()
    response = requests.patch(f"{BASE_URL}/admin/users/1/role?role=admin",headers=headers(customer_key))
    assert response.status_code == 403








#админ получает заказы пользователя
def test_get_user_orders_success():
    admin_key = get_admin_key()

    login_response = requests.post(f"{BASE_URL}/auth/login",json={"username": "testcustomer", "password": "123456"})
    assert login_response.status_code == 200
    real_user_id = login_response.json()["user_id"]


    #создание заказа
    order_id = create_test_order()
    print(f"Создан заказ {order_id}")

    #получаем заказ
    response = requests.get(f"{BASE_URL}/admin/users/{real_user_id}/orders",headers=headers(admin_key))

    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert "total" in data



#админ получает заказы несуществующего пользователя
def test_get_user_orders_user_not_found():
    admin_key = get_admin_key()

    response = requests.get(f"{BASE_URL}/admin/users/99999/orders", headers=headers(admin_key))

    assert response.status_code == 404
    assert "Пользователь не найден" in response.text


#без ключа нельзя получить заказы пользователя
def test_get_user_orders_unauthorized():
    response = requests.get(f"{BASE_URL}/admin/users/2/orders")
    assert response.status_code == 401


#покупатель не может получать заказы пользователя он не админ
def test_get_user_orders_as_customer():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/admin/users/2/orders", headers=headers(customer_key))
    assert response.status_code == 403




#курьер не может получать заказы пользователя он не админ
def test_get_user_orders_as_courier():
    courier_key = get_courier_key()
    if courier_key:
        response = requests.get(f"{BASE_URL}/admin/users/2/orders", headers=headers(courier_key))
        assert response.status_code == 403



#админ не может менять свою роль
def test_change_role_for_self():
    admin_key = get_admin_key()

    login_response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    admin_user_id = login_response.json()["user_id"]

    response = requests.patch(f"{BASE_URL}/admin/users/{admin_user_id}/role?role=customer", headers=headers(admin_key))

    assert response.status_code in [400, 403]
