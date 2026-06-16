import requests
import time

BASE_URL = "http://localhost:8080"

from helpTest import (
    get_customer_key,
    get_admin_key,
    get_courier_key,
    headers,
    create_test_user, create_test_customer, create_test_order_for_user
)



#пользователь получает свой профиль
def test_get_own_profile_success():
    customer_key = get_customer_key()

    login_response = requests.post(f"{BASE_URL}/auth/login",json={"username": "testcustomer", "password": "123456"})
    assert login_response.status_code == 200
    user_id = login_response.json()["user_id"]

    response = requests.get(f"{BASE_URL}/users/{user_id}",headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "testcustomer"
    assert "email" in data
    assert "role" in data



#пользователь не может получить и просмотреть чужой профиль
def test_get_other_user_profile_forbidden():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/users/1",headers=headers(customer_key))
    assert response.status_code == 403
    assert "Нельзя смотреть чужой профиль" in response.text


#нельзя смотреть без авторизации
def test_get_profile_unauthorized():
    response = requests.get(f"{BASE_URL}/users/1")
    assert response.status_code == 401


#нельзя смотреть с неверным ключом
def test_get_profile_wrong_key():
    response = requests.get(f"{BASE_URL}/users/1", headers=headers("wrong_key"))
    assert response.status_code == 403


#просмотр несуществующего пользователя
def test_get_nonexistent_user():
    customer_key = get_customer_key()

    login_response = requests.post(f"{BASE_URL}/auth/login",json={"username": "testcustomer", "password": "123456"})
    assert login_response.status_code == 200
    current_user_id = login_response.json()["user_id"]

    nonexistent_id = 99999
    if nonexistent_id == current_user_id:
        nonexistent_id = 99998

    response = requests.get(f"{BASE_URL}/users/{nonexistent_id}",headers=headers(customer_key))
    assert response.status_code in [403, 404]



#админ может получить свой профиль
def test_get_own_profile_as_admin():
    admin_key = get_admin_key()

    login_response = requests.post(f"{BASE_URL}/auth/login",json={"username": "admin", "password": "admin123"})
    assert login_response.status_code == 200
    user_id = login_response.json()["user_id"]

    response = requests.get(f"{BASE_URL}/users/{user_id}",headers=headers(admin_key))

    assert response.status_code == 200
    assert response.json()["role"] == "admin"



#курьер может получить свой профиль
def test_get_own_profile_as_courier():
    courier_key = get_courier_key()
    if courier_key:
        login_response = requests.post(f"{BASE_URL}/auth/login",json={"username": "courier1", "password": "12345678"})
        assert login_response.status_code == 200
        user_id = login_response.json()["user_id"]

        response = requests.get(f"{BASE_URL}/users/{user_id}",headers=headers(courier_key))

        assert response.status_code == 200
        assert response.json()["role"] == "courier"








#пользователь может обновить свой профиль
def test_update_own_profile_success():
    user_id, username, user_key = create_test_customer()

    update_data = {
        "address": "Новый адрес, ул. Тестовая, 100",
        "region": 10,
        "email": f"new_{username}@test.com"
    }

    response = requests.patch(f"{BASE_URL}/users/{user_id}",json=update_data,headers=headers(user_key))

    assert response.status_code == 200
    assert response.json()["message"] == "Профиль обновлен"


    get_response = requests.get(f"{BASE_URL}/users/{user_id}",headers=headers(user_key))
    assert get_response.status_code == 200
    assert get_response.json()["address"] == "Новый адрес, ул. Тестовая, 100"
    assert get_response.json()["region"] == 10


#нельзя редактировать чужой профиль
def test_update_other_user_forbidden():
    customer_key = get_customer_key()

    #обновление профиля админа
    update_data = {"address": "Попытка взлома"}
    response = requests.patch(f"{BASE_URL}/users/1",json=update_data,headers=headers(customer_key))

    assert response.status_code == 403
    assert "Нельзя редактировать чужой профиль" in response.text


#обновление без авторизации
def test_update_profile_unauthorized():
    update_data = {"address": "Новый адрес"}
    response = requests.patch(f"{BASE_URL}/users/1", json=update_data)
    assert response.status_code == 401


#обновление несуществующего пользователя
def test_update_nonexistent_user():
    user_id, username, user_key = create_test_customer()

    nonexistent_id = 99999
    if nonexistent_id == user_id:
        nonexistent_id = 99998

    update_data = {"address": "Новый адрес"}
    response = requests.patch(f"{BASE_URL}/users/{nonexistent_id}",json=update_data,headers=headers(user_key))

    assert response.status_code in [403, 404]



#частичное обновление профиля
def test_update_profile_partial():
    user_id, username, user_key = create_test_customer()

    get_response = requests.get(f"{BASE_URL}/users/{user_id}",headers=headers(user_key))
    original_region = get_response.json()["region"]

    update_data = {"address": "Только адрес обновлён"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}",json=update_data,headers=headers(user_key))

    assert response.status_code == 200

    get_response2 = requests.get(f"{BASE_URL}/users/{user_id}",headers=headers(user_key))
    assert get_response2.json()["address"] == "Только адрес обновлён"
    assert get_response2.json()["region"] == original_region



#обновление пароля пользователя
def test_update_profile_password():

    user_id, username, user_key = create_test_customer()

    update_data = {"password": "newpassword123"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}",json=update_data,headers=headers(user_key))

    assert response.status_code == 200

    login_response = requests.post(f"{BASE_URL}/auth/login",json={"username": username, "password": "newpassword123"})
    assert login_response.status_code == 200




#админ не может редактировать чужой профиль
def test_update_profile_as_admin():
    admin_key = get_admin_key()

    user_id, username, user_key = create_test_customer()

    update_data = {"address": "Админ пытается изменить"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}",json=update_data,headers=headers(admin_key))

    assert response.status_code == 403






#пользователь получает свои заказы
def test_get_own_orders_success():
    user_id, username, user_key = create_test_customer()

    order_id = create_test_order_for_user(user_key)

    response = requests.get(f"{BASE_URL}/users/{user_id}/orders",headers=headers(user_key))

    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert "total" in data
    assert isinstance(data["orders"], list)




#пользователь не может смотреть чужие заказы
def test_get_other_user_orders_forbidden():
    customer_key = get_customer_key()

    response = requests.get(f"{BASE_URL}/users/1/orders",headers=headers(customer_key))

    assert response.status_code == 403
    assert "Нельзя смотреть чужие заказы" in response.text


#просмотр заказов без авторизации
def test_get_orders_unauthorized():
    response = requests.get(f"{BASE_URL}/users/1/orders")
    assert response.status_code == 401


#просмотр заказов несуществующего пользователя
def test_get_orders_user_not_found():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/users/99999/orders",headers=headers(customer_key))

    assert response.status_code in [403, 404]



#пользователь без заказов получает пустой список
def test_get_orders_empty():
    user_id, username, user_key = create_test_customer()

    response = requests.get(f"{BASE_URL}/users/{user_id}/orders",headers=headers(user_key))

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["orders"]) == 0






#ользователь не может получить заказы другого пользователя
def test_cannot_access_another_user_data():

    user1_id, user1_name, user1_key = create_test_customer()
    user2_id, user2_name, user2_key = create_test_customer()


    response_profile = requests.get(f"{BASE_URL}/users/{user2_id}",headers=headers(user1_key))
    assert response_profile.status_code == 403

    response_orders = requests.get(f"{BASE_URL}/users/{user2_id}/orders",headers=headers(user1_key))
    assert response_orders.status_code == 403



#каждый пользователь видит только свои заказы
def test_each_user_sees_only_their_orders():
    user1_id, user1_name, user1_key = create_test_customer()
    user2_id, user2_name, user2_key = create_test_customer()

    create_test_order_for_user(user1_key)
    create_test_order_for_user(user2_key)

    response1 = requests.get(f"{BASE_URL}/users/{user1_id}/orders",headers=headers(user1_key))
    assert response1.status_code == 200

    response2 = requests.get(f"{BASE_URL}/users/{user2_id}/orders",headers=headers(user2_key))
    assert response2.status_code == 200



#проверка уникальности почты без учета регистра
def test_register_duplicate_email_case_insensitive():
    unique = int(time.time())
    email = f"DuplicateEmail_{unique}@test.com"

    user1_data = {
        "username": f"user1_{unique}",
        "email": email,
        "password": "123456",
        "address": "ул. Тестовая, 10",
        "region": 1
    }

    response1 = requests.post(f"{BASE_URL}/auth/register", json=user1_data)
    assert response1.status_code == 201

    user2_data = {
        "username": f"user2_{unique}",
        "email": email.lower(),
        "password": "123456",
        "address": "ул. Тестовая, 10",
        "region": 1
    }

    response2 = requests.post(f"{BASE_URL}/auth/register", json=user2_data)
    assert response2.status_code == 400
    assert "Email уже зарегистрирован" in response2.text