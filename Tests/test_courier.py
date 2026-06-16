import requests
import time

BASE_URL = "http://localhost:8080"

from helpTest import (
    get_customer_key,
    get_admin_key,
    get_courier_key,
    headers,create_test_order, create_test_order_with_weight
)



#курьер получает свой профиль
def test_get_courier_profile_success():
    courier_key = get_courier_key()
    response = requests.get(f"{BASE_URL}/courier/me", headers=headers(courier_key))

    assert response.status_code == 200
    data = response.json()
    assert "courier_id" in data
    assert "courier_type" in data
    assert "regions" in data
    assert "working_hours" in data
    assert "max_load" in data
    assert "earnings" in data
    assert "rating" in data

#попытка получение профиля без ключа
def test_get_courier_profile_unauthorized():
    response = requests.get(f"{BASE_URL}/courier/me")
    assert response.status_code == 401


#попытка получения профилья с неверным ключом
def test_get_courier_profile_wrong_key():
    response = requests.get(f"{BASE_URL}/courier/me", headers=headers("wrong_key"))
    assert response.status_code == 403


#покупатель не может получить профиль курьера
def test_get_courier_profile_as_customer():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/courier/me", headers=headers(customer_key))
    assert response.status_code == 403

#админ не может получать профиль курьера
def test_get_courier_profile_as_admin():
    admin_key = get_admin_key()
    response = requests.get(f"{BASE_URL}/courier/me", headers=headers(admin_key))
    assert response.status_code == 403








#курьер получает список доступных заказов
def test_get_available_orders_success():
    courier_key = get_courier_key()

    order_id = create_test_order()
    print(f"\nСоздан заказ {order_id}")

    response = requests.get(f"{BASE_URL}/courier/orders/available", headers=headers(courier_key))

    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert "total" in data
    assert isinstance(data["orders"], list)


#получение доступных заказов без ключа
def test_get_available_orders_unauthorized():
    response = requests.get(f"{BASE_URL}/courier/orders/available")
    assert response.status_code == 401

#другая роль не может получить доступные заказы
def test_get_available_orders_as_customer():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/courier/orders/available", headers=headers(customer_key))
    assert response.status_code == 403







#успешное взятие заказа себе
def test_take_order_success():
    courier_key = get_courier_key()
    order_id = create_test_order()

    response = requests.post(f"{BASE_URL}/courier/orders/take/{order_id}",headers=headers(courier_key))

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Заказ {order_id} взят"
    assert data["order_id"] == order_id


#взятие несуществующего заказа
def test_take_order_not_found():
    courier_key = get_courier_key()
    response = requests.post(f"{BASE_URL}/courier/orders/take/99999",headers=headers(courier_key))

    assert response.status_code == 404
    assert "Заказ не найден" in response.text


#взятие уже взятого заказа
def test_take_order_already_taken():
    courier_key = get_courier_key()
    order_id = create_test_order()

    requests.post(f"{BASE_URL}/courier/orders/take/{order_id}", headers=headers(courier_key))

    response = requests.post(f"{BASE_URL}/courier/orders/take/{order_id}",headers=headers(courier_key))

    assert response.status_code == 400
    assert "Заказ уже назначен или выполнен" in response.text


#взятие заказа без ключа
def test_take_order_unauthorized():
    response = requests.post(f"{BASE_URL}/courier/orders/take/1")
    assert response.status_code == 401


#другая роль не может брать заказ
def test_take_order_as_customer():
    customer_key = get_customer_key()
    response = requests.post(f"{BASE_URL}/courier/orders/take/1",headers=headers(customer_key))
    assert response.status_code == 403








#курьер просматривает список своих активных заказов
def test_get_my_orders_success():
    courier_key = get_courier_key()

    order_id = create_test_order()
    requests.post(f"{BASE_URL}/courier/orders/take/{order_id}", headers=headers(courier_key))

    response = requests.get(f"{BASE_URL}/courier/orders/my", headers=headers(courier_key))

    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert "total" in data
    assert isinstance(data["orders"], list)

    if data["total"] > 0:
        found = False
        for order in data["orders"]:
            if order["order_id"] == order_id:
                found = True
                break

        if found:
            print(f"Заказ {order_id} найден в списке")
        else:
            print(f"Заказ {order_id} не найден в списке")



#получение заказов без ключа
def test_get_my_orders_unauthorized():
    response = requests.get(f"{BASE_URL}/courier/orders/my")
    assert response.status_code == 401

#другая роль не может получить заказы курьера
def test_get_my_orders_as_customer():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/courier/orders/my", headers=headers(customer_key))
    assert response.status_code == 403








#успешное завершение зазказа
def test_complete_order_success():
    courier_key = get_courier_key()
    order_id = create_test_order()

    requests.post(f"{BASE_URL}/courier/orders/take/{order_id}", headers=headers(courier_key))

    response = requests.post(f"{BASE_URL}/courier/orders/complete/{order_id}",headers=headers(courier_key))

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Заказ {order_id} выполнен"
    assert data["order_id"] == order_id


#выполнение несуществующего заказа
def test_complete_order_not_found():
    courier_key = get_courier_key()
    response = requests.post(f"{BASE_URL}/courier/orders/complete/99999",headers=headers(courier_key))

    assert response.status_code == 404
    assert "Заказ не найден" in response.text



#выполнение не своего заказа
def test_complete_order_not_mine():
    courier_key = get_courier_key()
    order_id = create_test_order()


    response = requests.post(f"{BASE_URL}/courier/orders/complete/{order_id}",headers=headers(courier_key))

    assert response.status_code in [400, 403]



#выполнение заказа без авторизации ключа
def test_complete_order_unauthorized():
    response = requests.post(f"{BASE_URL}/courier/orders/complete/1")
    assert response.status_code == 401



#другая роль не может выполнять заказ
def test_complete_order_as_customer():
    customer_key = get_customer_key()
    response = requests.post(f"{BASE_URL}/courier/orders/complete/1",headers=headers(customer_key))
    assert response.status_code == 403








#получение заработка
def test_get_earnings_success():
    courier_key = get_courier_key()
    response = requests.get(f"{BASE_URL}/courier/earnings", headers=headers(courier_key))

    assert response.status_code == 200
    data = response.json()
    assert "earnings" in data
    assert isinstance(data["earnings"], (int, float))



#получение заработка без авторизации
def test_get_earnings_unauthorized():
    response = requests.get(f"{BASE_URL}/courier/earnings")
    assert response.status_code == 401


#другая роль не может получать заработок
def test_get_earnings_as_customer():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/courier/earnings", headers=headers(customer_key))
    assert response.status_code == 403

#увеличесние заработка после выполнения заказа
def test_earnings_increase_after_complete():

    courier_key = get_courier_key()

    before = requests.get(f"{BASE_URL}/courier/earnings", headers=headers(courier_key)).json()
    earnings_before = before["earnings"]

    order_id = create_test_order()
    requests.post(f"{BASE_URL}/courier/orders/take/{order_id}", headers=headers(courier_key))
    requests.post(f"{BASE_URL}/courier/orders/complete/{order_id}", headers=headers(courier_key))

    after = requests.get(f"{BASE_URL}/courier/earnings", headers=headers(courier_key)).json()
    earnings_after = after["earnings"]

    assert earnings_after > earnings_before





#получение рейтинга
def test_get_rating_success():
    courier_key = get_courier_key()
    response = requests.get(f"{BASE_URL}/courier/rating", headers=headers(courier_key))

    assert response.status_code == 200
    data = response.json()
    assert "rating" in data
    assert isinstance(data["rating"], (int, float))



#получение рейтинга без авторизации
def test_get_rating_unauthorized():
    response = requests.get(f"{BASE_URL}/courier/rating")
    assert response.status_code == 401


#другая роль не может получить рейтинг
def test_get_rating_as_customer():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/courier/rating", headers=headers(customer_key))
    assert response.status_code == 403



#рейтинг появляется/обновляется после выполнения заказа
def test_rating_appears_after_complete():
    courier_key = get_courier_key()

    # Получаем рейтинг до (может быть 0)
    before = requests.get(f"{BASE_URL}/courier/rating", headers=headers(courier_key)).json()
    rating_before = before["rating"]

    # Выполняем заказ
    order_id = create_test_order()
    requests.post(f"{BASE_URL}/courier/orders/take/{order_id}", headers=headers(courier_key))
    requests.post(f"{BASE_URL}/courier/orders/complete/{order_id}", headers=headers(courier_key))

    # Получаем рейтинг после
    after = requests.get(f"{BASE_URL}/courier/rating", headers=headers(courier_key)).json()
    rating_after = after["rating"]

    # Рейтинг должен быть >= 0
    assert rating_after >= 0
    print(f"Рейтинг: {rating_after}")








#курьер не модет взять заказ который тяжелее его грузоподьемности
def test_take_order_exceeds_max_load():
    courier_key = get_courier_key()

    profile = requests.get(f"{BASE_URL}/courier/me", headers=headers(courier_key)).json()
    max_load = profile["max_load"]

    overweight = max_load + 10
    order_id = create_test_order_with_weight(weight=overweight)

    response = requests.post(f"{BASE_URL}/courier/orders/take/{order_id}", headers=headers(courier_key))

    assert response.status_code == 400
    assert "превышает" in response.text.lower() or "грузоподъемность" in response.text.lower()



#нельзя взять второй заказ если суммарный вес превышает грузоподьемность
def test_take_order_exceeds_total_load():
    courier_key = get_courier_key()

    profile = requests.get(f"{BASE_URL}/courier/me", headers=headers(courier_key)).json()
    max_load = profile["max_load"]


    half_load = (max_load // 2) + 1
    if half_load <= 0:
        half_load = 1

    order1_id = create_test_order_with_weight(weight=half_load)
    order2_id = create_test_order_with_weight(weight=half_load + 1)

    response1 = requests.post(f"{BASE_URL}/courier/orders/take/{order1_id}", headers=headers(courier_key))
    assert response1.status_code == 200

    response2 = requests.post(f"{BASE_URL}/courier/orders/take/{order2_id}", headers=headers(courier_key))

    assert response2.status_code == 400
    assert "превысит" in response2.text.lower() or "грузоподъемность" in response2.text.lower()



#если грузоподьемность не превышена можно взять заказ
def test_take_order_within_max_load():
    courier_key = get_courier_key()

    profile = requests.get(f"{BASE_URL}/courier/me", headers=headers(courier_key)).json()
    max_load = profile["max_load"]

    normal_weight = max_load - 1 if max_load > 1 else 1
    order_id = create_test_order_with_weight(weight=normal_weight)

    response = requests.post(f"{BASE_URL}/courier/orders/take/{order_id}", headers=headers(courier_key))

    assert response.status_code == 200
    assert response.json()["message"] == f"Заказ {order_id} взят"



#освобождение грузоподьемности после выполнения товара
def test_take_order_after_complete_load():
    courier_key = get_courier_key()

    profile = requests.get(f"{BASE_URL}/courier/me", headers=headers(courier_key)).json()
    max_load = profile["max_load"]

    order1_id = create_test_order_with_weight(weight=max_load)
    order2_id = create_test_order_with_weight(weight=max_load)

    response1 = requests.post(f"{BASE_URL}/courier/orders/take/{order1_id}", headers=headers(courier_key))
    assert response1.status_code == 200

    requests.post(f"{BASE_URL}/courier/orders/complete/{order1_id}", headers=headers(courier_key))

    response2 = requests.post(f"{BASE_URL}/courier/orders/take/{order2_id}", headers=headers(courier_key))

    assert response2.status_code == 200



#курьер может взять заказ вес которого равен его грузоподьемности
def test_take_order_equal_max_load():
    courier_key = get_courier_key()
    profile = requests.get(f"{BASE_URL}/courier/me", headers=headers(courier_key)).json()
    max_load = profile["max_load"]


    order_id = create_test_order_with_weight(weight=max_load)

    response = requests.post(f"{BASE_URL}/courier/orders/take/{order_id}", headers=headers(courier_key))

    assert response.status_code == 200