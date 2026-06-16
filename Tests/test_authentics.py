import requests
import pytest

BASE_URL = "http://localhost:8080"



#успешная регистрация пользователя
def test_register_success():
    unique_username = f"test_user_{__import__('time').time()}"

    user_data = {
        "username": unique_username,
        "email": f"{unique_username}@test.com",
        "password": "test123",
        "address": "ул. Тестовая, 10",
        "region": 1
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Регистрация успешна"
    assert data["username"] == unique_username
    assert "user_id" in data
    assert "api_key" in data

    login_data = {
        "username": unique_username,
        "password": "test123"
    }

    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert login_response.status_code == 200
    assert login_response.json()["username"] == unique_username
    assert login_response.json()["role"] == "customer"




#регистрация с существующим юзернейм(повторение)
def test_register_duplicate_username():
    username = "test_duplicate_user"
    email = f"{username}@test.com"

    user_data = {
        "username": username,
        "email": email,
        "password": "test123",
        "address": "ул. Тестовая, 10",
        "region": 1
    }

    response1 = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    assert response1.status_code == 201

    response2 = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    assert response2.status_code == 400
    assert "Username уже занят" in response2.text


#регистрация с существующим емейл(повторение)
def test_register_duplicate_email():
    email = "test_duplicate_email@test.com"

    user1_data = {
        "username": "test_user_1",
        "email": email,
        "password": "test123",
        "address": "ул. Тестовая, 10",
        "region": 1
    }

    response1 = requests.post(f"{BASE_URL}/auth/register", json=user1_data)
    assert response1.status_code == 201

    user2_data = {
        "username": "test_user_2",
        "email": email,
        "password": "test123",
        "address": "ул. Тестовая, 10",
        "region": 1
    }

    response2 = requests.post(f"{BASE_URL}/auth/register", json=user2_data)
    assert response2.status_code == 400
    assert "Email уже зарегистрирован" in response2.text


#регистрация не со всеми полями
def test_register_missing_fields():
    user_data = {
        "username": "test_user",
        "email": "test@test.com",
        "address": "ул. Тестовая",
        "region": 1
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    assert response.status_code == 422







#успешный вход
def test_login_success():
    username = f"test_login_{__import__('time').time()}"
    email = f"{username}@test.com"
    password = "login123"

    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "address": "ул. Тестовая, 10",
        "region": 1
    }

    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    assert register_response.status_code == 201

    login_data = {
        "username": username,
        "password": password
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "api_key" in data
    assert data["username"] == username
    assert data["role"] == "customer"
    assert "user_id" in data


#вход с неверным паролем
def test_login_wrong_password():
    username = f"test_wrong_pwd_{__import__('time').time()}"

    register_data = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "correct123",
        "address": "ул. Тестовая, 10",
        "region": 1
    }

    requests.post(f"{BASE_URL}/auth/register", json=register_data)

    login_data = {
        "username": username,
        "password": "wrong_password"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert response.status_code == 400
    assert "Неверный логин или пароль" in response.text




#вход несуществующего пользователя
def test_login_nonexistent_user():
    login_data = {
        "username": "nonexistent_user_12345",
        "password": "somepass"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert response.status_code == 400
    assert "Неверный логин или пароль" in response.text


#вход успешного регистратора
def test_login_existing_admin():
    login_data = {
        "username": "admin",
        "password": "admin123"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "api_key" in data
    assert data["username"] == "admin"
    assert data["role"] == "admin"


#вход успешного покупателя
def test_login_existing_customer():
    login_data = {
        "username": "testcustomer",
        "password": "123456"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "api_key" in data
    assert data["username"] == "testcustomer"
    assert data["role"] == "customer"



#вход успешного курьера
def test_login_existing_courier():
    login_data = {
        "username": "courier1",
        "password": "12345678"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "api_key" in data
    assert data["username"] == "courier1"
    assert data["role"] == "courier"







#успешный выход
def test_logout_success():
    username = f"test_logout_{__import__('time').time()}"

    register_data = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "logout123",
        "address": "ул. Тестовая, 10",
        "region": 1
    }

    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    assert register_response.status_code == 201
    api_key = register_response.json()["api_key"]



    headers = {"API-Token": api_key}
    response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Выход выполнен"



    response2 = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    assert response2.status_code == 403


#выход без апи ключа неавторизованный
def test_logout_without_key():
    response = requests.post(f"{BASE_URL}/auth/logout")
    assert response.status_code == 401

#выход с неверным апи ключом
def test_logout_with_wrong_key():
    headers = {"API-Token": "wrong_key_12345"}
    response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    assert response.status_code == 403

