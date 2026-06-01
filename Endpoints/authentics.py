#отвечает за регистрацию, вход, выход для всех пользователей

from fastapi import APIRouter, HTTPException, Depends
from auth import generate_api_key, API_KEYS, verify_api_key
from Models.user import User
from datetime import datetime
from sqlalchemy.orm import Session
from DB.DBconnect import get_db
from DB.tabels import UserDB
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Аутентификация"])





#вход (для всех ПОКУПАТЕЛЯ, АДМИНА, КУРЬЕРА)
@router.post("/login")
def login(username: str, password: str,db: Session = Depends(get_db)):
    #ищем пользователя в бд
    user = db.query(UserDB).filter(UserDB.username == username).first()


    if not user:
        raise HTTPException(400, "Неверный логин или пароль")

    #проверка пароля
    if user.password != password:
        raise HTTPException(400, "Неверный логин или пароль")

    #если у пользователя есть ключ берем его, иначе создаем новый
    if user.api_key:
        api_key = user.api_key
    else:
        api_key = generate_api_key()
        user.api_key = api_key
        db.commit() #сохраням ключ в бд

    #активация для сессий
    API_KEYS[api_key] = {
        "role": user.role,
        "user_id": user.id_user,
        "username": user.username
    }

    return {
        "api_key": api_key,
        "role": user.role,
        "user_id": user.id_user,
        "username": user.username
    }




#регистрация (только для ПОКУПАТЕЛЯ)
@router.post("/register", status_code=201)
def register(username: str, email: str, password: str, address: str = None, region: int = None, db: Session = Depends(get_db)):
    #проверка уникальности почты и логина
    existing_user = db.query(UserDB).filter((UserDB.username == username) | (UserDB.email == email)).first()

    if existing_user:
        if existing_user.username == username:
            raise HTTPException(400, "Username уже занят")
        if existing_user.email == email:
            raise HTTPException(400, "Email уже зарегистрирован")

    #генерация апи ключа
    api_key = generate_api_key()

    #создание пользователя(покупателя)
    new_user = UserDB(
        username=username,
        email=email,
        password=password,
        address=address,
        region=region,
        role="customer",
        api_key=api_key,
        created_at=datetime.now()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user) #получаем сгенерированный айди юзера

    # активация ключа
    API_KEYS[api_key] = {
        "role": "customer",
        "user_id": new_user.id_user,
        "username": username
    }

    return {
        "message": "Регистрация успешна",
        "user_id": new_user.id_user,
        "username": username,
        "api_key": api_key
    }




#выход (для всех ПОКУПАТЕЛЯ, АДМИНА, КУРЬЕРА)
@router.post("/logout")
def logout(current_user = Depends(verify_api_key)):
    api_key = current_user["api_key"]
    del API_KEYS[api_key]
    return {"message": "Выход выполнен"}