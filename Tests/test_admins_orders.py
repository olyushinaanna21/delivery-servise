import requests

BASE_URL = "http://localhost:8080"

from helpTest import get_admin_key, get_customer_key, get_courier_key, create_test_order, headers



#получение списка всех заказов админом
def test_get_all_orders_success():
    admin_key = get_admin_key()
    response = requests.get(f"{BASE_URL}/admin/orders", headers=headers(admin_key))

    assert response.status_code == 200
    assert "orders" in response.json()
    assert "total" in response.json()



#без ключа доступа нет неавторизованно
def test_get_all_orders_unauthorized():
    response = requests.get(f"{BASE_URL}/admin/orders")
    assert response.status_code == 401


#с неверным ключом доступа нет
def test_get_all_orders_wrong_key():
    response = requests.get(f"{BASE_URL}/admin/orders", headers=headers("wrong_key"))
    assert response.status_code == 403

#другая роль не может получить список заказов
def test_get_all_orders_as_customer():
    customer_key = get_customer_key()
    response = requests.get(f"{BASE_URL}/admin/orders", headers=headers(customer_key))
    assert response.status_code == 403


#другая роль не может получить список заказов
def test_get_all_orders_as_courier():
    courier_key = get_courier_key()
    if courier_key:
        response = requests.get(f"{BASE_URL}/admin/orders", headers=headers(courier_key))
        assert response.status_code == 403








#успешная отмена заказа
def test_cancel_order_success():
    admin_key = get_admin_key()
    order_id = create_test_order()

    response = requests.patch(f"{BASE_URL}/admin/orders/{order_id}/cancel",headers=headers(admin_key))
    assert response.status_code == 200
    assert response.json()["message"] == f"Заказ {order_id} отменен"

#отмена несуществующего заказа
def test_cancel_order_not_found():
    admin_key = get_admin_key()
    response = requests.patch(f"{BASE_URL}/admin/orders/99999/cancel",headers=headers(admin_key))
    assert response.status_code == 404

#без авторизации нельзя отменить заказ
def test_cancel_order_unauthorized():
    response = requests.patch(f"{BASE_URL}/admin/orders/1/cancel")
    assert response.status_code == 401


#с неверным ключом нельзя отменить заказ
def test_cancel_order_wrong_key():
    response = requests.patch(f"{BASE_URL}/admin/orders/1/cancel",headers=headers("wrong_key"))
    assert response.status_code == 403


#другая роль не может отменять заказ
def test_cancel_order_as_customer():
    customer_key = get_customer_key()
    response = requests.patch(f"{BASE_URL}/admin/orders/1/cancel",headers=headers(customer_key))
    assert response.status_code == 403

#другая роль не может отменять заказ
def test_cancel_order_as_courier():
    courier_key = get_courier_key()
    if courier_key:
        response = requests.patch(f"{BASE_URL}/admin/orders/1/cancel",headers=headers(courier_key))
        assert response.status_code == 403
