#отвечает за регистрацию, вход, выход для всех пользователей
from fastapi import APIRouter, HTTPException, Depends
from auth import generate_api_key, API_KEYS, verify_api_key
from Models.authent import LoginRequest, RegisterRequest
from datetime import datetime
from sqlalchemy.orm import Session
from DB.DBconnect import get_db
from DB.tabels import UserDB
from sqlalchemy import func

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


#вход
@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == request.username).first()

    if not user:
        raise HTTPException(400, "Неверный логин или пароль")

    if user.password != request.password:
        raise HTTPException(400, "Неверный логин или пароль")

    if user.api_key:
        api_key = user.api_key
    else:
        api_key = generate_api_key()
        user.api_key = api_key
        db.commit()

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


#регистрация (покупатель)
@router.post("/register", status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # проверка уникальности
    existing_user = db.query(UserDB).filter(
        (func.lower(UserDB.username) == request.username.lower()) |
        (func.lower(UserDB.email) == request.email.lower())).first()

    if existing_user:
        if existing_user.username.lower() == request.username.lower():
            raise HTTPException(400, "Username уже занят")
        if existing_user.email.lower() == request.email.lower():
            raise HTTPException(400, "Email уже зарегистрирован")

    api_key = generate_api_key()

    new_user = UserDB(
        username=request.username,
        email=request.email,
        password=request.password,
        address=request.address,
        region=request.region,
        role="customer",
        api_key=api_key,
        created_at=datetime.now()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    API_KEYS[api_key] = {
        "role": "customer",
        "user_id": new_user.id_user,
        "username": request.username
    }

    return {
        "message": "Регистрация успешна",
        "user_id": new_user.id_user,
        "username": request.username,
        "api_key": api_key
    }


#выход
@router.post("/logout")
def logout(current_user = Depends(verify_api_key)):
    api_key = current_user["api_key"]
    del API_KEYS[api_key]
    return {"message": "Выход выполнен"}