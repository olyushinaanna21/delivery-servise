import requests
from helpTest import (
    get_customer_key,
    get_admin_key,
    get_courier_key,
    headers,
    create_test_product,
    create_test_user,
    get_customer_key_by_username, clear_cart
)


BASE_URL = "http://localhost:8080"



#получение пустой корзины
def test_get_cart_empty():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/cart", headers=headers(customer_key))

    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "items" in data
    assert "total_price" in data
    assert "total_weight" in data
    assert isinstance(data["items"], list)
    assert data["total_price"] == 0
    assert data["total_weight"] == 0


#получение корзины без регистрации
def test_get_cart_unauthorized():
    response = requests.get(f"{BASE_URL}/cart")
    assert response.status_code == 401


#получение корзины с неверным ключом
def test_get_cart_wrong_key():
    response = requests.get(f"{BASE_URL}/cart", headers=headers("wrong_key"))
    assert response.status_code == 403




#другая роль не может получить корзину
def test_get_cart_as_admin():
    admin_key = get_admin_key()
    response = requests.get(f"{BASE_URL}/cart", headers=headers(admin_key))
    assert response.status_code == 403

#курьер не может получить корзину
def test_get_cart_as_courier():
    courier_key = get_courier_key()
    if courier_key:
        response = requests.get(f"{BASE_URL}/cart", headers=headers(courier_key))
        assert response.status_code == 403








#успещное добавление в корзину
def test_add_to_cart_success():
    customer_key = get_customer_key()
    product_id = create_test_product()

    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(customer_key))

    response = requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": 1},headers=headers(customer_key))

    assert response.status_code == 200
    assert response.json()["message"] == "Товар добавлен в корзину"


    cart_response = requests.get(f"{BASE_URL}/cart", headers=headers(customer_key))
    assert cart_response.status_code == 200
    assert len(cart_response.json()["items"]) == 1
    assert cart_response.json()["total_price"] == 100


#добавление несуществующего товара
def test_add_to_cart_product_not_found():
    customer_key = get_customer_key()

    response = requests.post(f"{BASE_URL}/cart/add",params={"product_id": 99999, "quantity": 1},headers=headers(customer_key))

    assert response.status_code == 404
    assert "Товар не найден" in response.text


#добавление в корзину без авторизации
def test_add_to_cart_unauthorized():
    response = requests.post(f"{BASE_URL}/cart/add", params={"product_id": 1, "quantity": 1})
    assert response.status_code == 401

#добавление с количеством больше 1
def test_add_to_cart_multiple_quantity():
    customer_key = get_customer_key()
    product_id = create_test_product()

    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(customer_key))

    response = requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": 3},headers=headers(customer_key))

    assert response.status_code == 200

    cart_response = requests.get(f"{BASE_URL}/cart", headers=headers(customer_key))
    assert cart_response.status_code == 200
    assert cart_response.json()["items"][0]["quantity"] == 3
    assert cart_response.json()["total_price"] == 300



#добавление уже существующего товара(увеличение количества)
def test_add_to_cart_duplicate():
    customer_key = get_customer_key()
    product_id = create_test_product()

    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(customer_key))

    requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": 1},headers=headers(customer_key))

    requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": 2},headers=headers(customer_key))



    cart_response = requests.get(f"{BASE_URL}/cart", headers=headers(customer_key))
    assert cart_response.status_code == 200
    assert cart_response.json()["items"][0]["quantity"] == 3
    assert cart_response.json()["total_price"] == 300






#успешное обновление количества
def test_update_quantity_success():
    customer_key = get_customer_key()
    product_id = create_test_product()

    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(customer_key))
    requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": 1},headers=headers(customer_key))

    response = requests.patch(f"{BASE_URL}/cart/update",params={"product_id": product_id, "quantity": 5},headers=headers(customer_key))

    assert response.status_code == 200
    assert response.json()["message"] == "Количество обновлено"


    cart_response = requests.get(f"{BASE_URL}/cart", headers=headers(customer_key))
    assert cart_response.json()["items"][0]["quantity"] == 5
    assert cart_response.json()["total_price"] == 500


#обновление количества до 0(удаление товара)
def test_update_quantity_to_zero():
    customer_key = get_customer_key()
    product_id = create_test_product()

    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(customer_key))
    requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": 1},headers=headers(customer_key))


    response = requests.patch(f"{BASE_URL}/cart/update",params={"product_id": product_id, "quantity": 0},headers=headers(customer_key))

    assert response.status_code == 200

    cart_response = requests.get(f"{BASE_URL}/cart", headers=headers(customer_key))
    assert len(cart_response.json()["items"]) == 0
    assert cart_response.json()["total_price"] == 0




#обновление колва у несуществующего товара в корзине
def test_update_quantity_not_found():
    customer_key = get_customer_key()

    response = requests.patch(f"{BASE_URL}/cart/update",params={"product_id": 99999, "quantity": 5},headers=headers(customer_key))

    assert response.status_code == 404
    assert "Товар не найден в корзине" in response.text


#обновление без авторизации
def test_update_quantity_unauthorized():
    response = requests.patch(f"{BASE_URL}/cart/update", params={"product_id": 1, "quantity": 5})
    assert response.status_code == 401







#успешное удаление товара из корзины
def test_remove_from_cart_success():
    customer_key = get_customer_key()
    product_id = create_test_product()

    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(customer_key))
    requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": 1},headers=headers(customer_key))

    response = requests.delete(f"{BASE_URL}/cart/remove/{product_id}",headers=headers(customer_key))

    assert response.status_code == 200
    assert response.json()["message"] == "Товар удален из корзины"

    cart_response = requests.get(f"{BASE_URL}/cart", headers=headers(customer_key))
    assert len(cart_response.json()["items"]) == 0


#удаление несущетсвующего товара в корзине
def test_remove_from_cart_not_found():
    customer_key = get_customer_key()

    response = requests.delete(f"{BASE_URL}/cart/remove/99999",headers=headers(customer_key))

    assert response.status_code == 404
    assert "Товар не найден в корзине" in response.text

#удаление без авторизации
def test_remove_from_cart_unauthorized():
    response = requests.delete(f"{BASE_URL}/cart/remove/1")
    assert response.status_code == 401







#очистка всей корзины
def test_clear_cart_success():
    customer_key = get_customer_key()
    product_id = create_test_product()

    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(customer_key))
    requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": 2},headers=headers(customer_key))


    response = requests.delete(f"{BASE_URL}/cart/clear", headers=headers(customer_key))

    assert response.status_code == 200
    assert response.json()["message"] == "Корзина очищена"

    cart_response = requests.get(f"{BASE_URL}/cart", headers=headers(customer_key))
    assert len(cart_response.json()["items"]) == 0
    assert cart_response.json()["total_price"] == 0

#очистка корзины без авторизации
def test_clear_cart_unauthorized():
    response = requests.delete(f"{BASE_URL}/cart/clear")
    assert response.status_code == 401


#никто кроме покупателя не может очищать корзину
def test_clear_cart_as_admin():
    admin_key = get_admin_key()
    response = requests.delete(f"{BASE_URL}/cart/clear", headers=headers(admin_key))
    assert response.status_code == 403







#корзины разных пользователей не сливаются в одну
def test_cart_isolation():

    user1_id, user1_name = create_test_user()
    user2_id, user2_name = create_test_user()

    user1_key = get_customer_key_by_username(user1_name, "test123")
    user2_key = get_customer_key_by_username(user2_name, "test123")

    product_id = create_test_product()

    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(user1_key))
    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(user2_key))

    requests.post(f"{BASE_URL}/cart/add",params={"product_id": product_id, "quantity": 1},headers=headers(user1_key))


    cart1 = requests.get(f"{BASE_URL}/cart", headers=headers(user1_key))
    assert len(cart1.json()["items"]) == 1

    cart2 = requests.get(f"{BASE_URL}/cart", headers=headers(user2_key))
    assert len(cart2.json()["items"]) == 0







#добавление очень большого количества товара
def test_add_to_cart_large_quantity():
    customer_key = get_customer_key()
    product_id = create_test_product()

    clear_cart(customer_key)

    response = requests.post(f"{BASE_URL}/cart/add", params={"product_id": product_id, "quantity": 9999},headers=headers(customer_key))

    assert response.status_code == 200

    cart_response = requests.get(f"{BASE_URL}/cart", headers=headers(customer_key))
    assert cart_response.json()["items"][0]["quantity"] == 9999
    assert cart_response.json()["total_price"] == 100 * 9999