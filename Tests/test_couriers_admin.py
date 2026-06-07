import requests
import time

BASE_URL = "http://localhost:8080"

from helpTest import (
    get_customer_key,
    get_admin_key,
    get_courier_key,
    headers, create_test_courier
)




#админ успешно создает курьера
def test_create_courier_success():
    admin_key = get_admin_key()
    unique_username = f"new_courier_{int(time.time())}"

    response = requests.post(f"{BASE_URL}/couriers",
        json={
            "username": unique_username,
            "password": "courier123",
            "email": f"{unique_username}@test.com",
            "courier_type": "bike",
            "regions": [1, 2, 3, 4, 5],
            "working_hours": ["09:00-18:00"]
        },
        headers=headers(admin_key)
    )

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Курьер успешно создан"
    assert "api_key" in data
    assert "user_id" in data




#создание курьера с существующим юзернейм(повторение)
def test_create_courier_duplicate_username():
    admin_key = get_admin_key()
    unique_username = f"dup_courier_{int(time.time())}"

    response1 = requests.post(
        f"{BASE_URL}/couriers",
        json={
            "username": unique_username,
            "password": "courier123",
            "email": f"{unique_username}@test.com",
            "courier_type": "foot",
            "regions": [1, 2, 3],
            "working_hours": ["09:00-18:00"]
        },
        headers=headers(admin_key)
    )
    assert response1.status_code == 201

    response2 = requests.post(
        f"{BASE_URL}/couriers",
        json={
            "username": unique_username,
            "password": "courier456",
            "email": f"another_{unique_username}@test.com",
            "courier_type": "bike",
            "regions": [1, 2, 3],
            "working_hours": ["09:00-18:00"]
        },
        headers=headers(admin_key)
    )

    assert response2.status_code == 400
    assert "Username уже занят" in response2.text


#создание курьера с существующим емейл(повторение)
def test_create_courier_duplicate_email():
    admin_key = get_admin_key()
    unique_email = f"dup_email_{int(time.time())}@test.com"

    response1 = requests.post(
        f"{BASE_URL}/couriers",
        json={
            "username": f"user1_{int(time.time())}",
            "password": "courier123",
            "email": unique_email,
            "courier_type": "foot",
            "regions": [1, 2, 3],
            "working_hours": ["09:00-18:00"]
        },
        headers=headers(admin_key)
    )
    assert response1.status_code == 201

    response2 = requests.post(
        f"{BASE_URL}/couriers",
        json={
            "username": f"user2_{int(time.time())}",
            "password": "courier456",
            "email": unique_email,
            "courier_type": "bike",
            "regions": [1, 2, 3],
            "working_hours": ["09:00-18:00"]
        },
        headers=headers(admin_key)
    )

    assert response2.status_code == 400
    assert "Email уже зарегистрирован" in response2.text


#создание курьера без авторизации
def test_create_courier_unauthorized():
    response = requests.post(
        f"{BASE_URL}/couriers",
        json={
            "username": "test_courier",
            "password": "123456",
            "email": "test@test.com",
            "courier_type": "foot",
            "regions": [1, 2, 3],
            "working_hours": ["09:00-18:00"]
        }
    )
    assert response.status_code == 401


#покупатель не может создавать курьеров(только админ)
def test_create_courier_as_customer():
    customer_key = get_customer_key()
    response = requests.post(
        f"{BASE_URL}/couriers",
        json={
            "username": "test_courier",
            "password": "123456",
            "email": "test@test.com",
            "courier_type": "foot",
            "regions": [1, 2, 3],
            "working_hours": ["09:00-18:00"]
        },
        headers=headers(customer_key)
    )
    assert response.status_code == 403







#админ получает список всех курьеров
def test_get_all_couriers_success():
    admin_key = get_admin_key()
    response = requests.get(f"{BASE_URL}/couriers", headers=headers(admin_key))

    assert response.status_code == 200
    data = response.json()
    assert "couriers" in data
    assert "total" in data


#получение без авторизации
def test_get_all_couriers_unauthorized():
    response = requests.get(f"{BASE_URL}/couriers")
    assert response.status_code == 401


#другая роль не может получить список курьеров
def test_get_all_couriers_as_customer():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/couriers", headers=headers(customer_key))
    assert response.status_code == 403








#получение информации о курьере по его айди
def test_get_courier_by_id_success():
    response = requests.get(f"{BASE_URL}/couriers/1")


    if response.status_code == 200:
        data = response.json()
        assert "courier_id" in data
        assert "courier_type" in data
        assert "regions" in data
        assert "working_hours" in data
    else:
        print("Нет курьера с таким айди")



#получение информаиции о несуществующем курьере
def test_get_courier_by_id_not_found():
    response = requests.get(f"{BASE_URL}/couriers/99999")
    assert response.status_code == 404









#успешное обновление курьера(админ)
def test_update_courier_success():
    admin_key = get_admin_key()

    courier_id, user_id, username = create_test_courier()

    if courier_id:
        update_data = {
            "courier_type": "car",
            "regions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "working_hours": ["10:00-20:00"]
        }
        response = requests.patch(f"{BASE_URL}/couriers/{courier_id}",json=update_data,headers=headers(admin_key))
        assert response.status_code == 200
        data = response.json()
        assert data["courier_type"] == "car"



#обновление без авторизации
def test_update_courier_unauthorized():
    response = requests.patch(f"{BASE_URL}/couriers/1", json={"courier_type": "bike"})
    assert response.status_code == 401


#другая роль не может обновлять курьера
def test_update_courier_as_customer():
    customer_key = get_customer_key()
    response = requests.patch(f"{BASE_URL}/couriers/1",json={"courier_type": "bike"},headers=headers(customer_key))
    assert response.status_code == 403









#удаление несуществующего курьера
def test_delete_courier_not_found():
    admin_key = get_admin_key()
    response = requests.delete(f"{BASE_URL}/couriers/99999",headers=headers(admin_key))
    assert response.status_code == 404

#удаление курьера без авторизации
def test_delete_courier_unauthorized():
    response = requests.delete(f"{BASE_URL}/couriers/1")
    assert response.status_code == 401


#другая роль не может удалять курьера
def test_delete_courier_as_customer():
    customer_key = get_customer_key()
    response = requests.delete(f"{BASE_URL}/couriers/1",headers=headers(customer_key))
    assert response.status_code == 403


#админ успешно удаляет курьера
def test_delete_courier_success():
    admin_key = get_admin_key()

    courier_id, user_id, username = create_test_courier()

    if courier_id:
        response = requests.delete(f"{BASE_URL}/couriers/{courier_id}",headers=headers(admin_key))
        assert response.status_code == 200
        assert f"Курьер {courier_id} удален" in response.json()["message"]
