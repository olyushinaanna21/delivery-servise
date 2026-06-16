#система авторизации по api ключу

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import secrets
import string

API_KEYS = {"admin_key_123": {"role": "admin", "user_id": 1, "username": "admin"},
    "test_customer_key_456": {"role": "customer", "user_id": 2, "username": "testcustomer"},
    "courier_key_789": {"role": "courier", "user_id": 3, "username": "courier1"},} #в будущем бд


#ищет в http аголовок апи токен, если его нет ошибка 403 (доступ запрещён)
api_key_header = APIKeyHeader(name="API-Token", auto_error=True)

#функция проверки API ключа и возврат данных пользователя
def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in API_KEYS:
        raise HTTPException(403, "Неверный API ключ")

    data = API_KEYS[api_key].copy()
    data["api_key"] = api_key
    return data


#генерирует случайный апи ключ из 10 символов цифр и букв
def generate_api_key(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


#функции проверок ролей по ключам
def require_admin(api_key_data: dict = Security(verify_api_key)):
    if api_key_data["role"] != "admin":
        raise HTTPException(403, "Требуются права администратора")
    return api_key_data


def require_courier(api_key_data: dict = Security(verify_api_key)):
    if api_key_data["role"] != "courier":
        raise HTTPException(403, "Требуются права курьера")
    return api_key_data


def require_customer(api_key_data: dict = Security(verify_api_key)):
    if api_key_data["role"] != "customer":
        raise HTTPException(403, "Требуются права покупателя")
    return api_key_data


#возвращает данные текущего пользователя по апи ключу
def get_current_user(api_key_data: dict = Security(verify_api_key)):
    return api_key_data