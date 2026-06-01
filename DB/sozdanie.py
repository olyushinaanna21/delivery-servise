from DBconnect import engine, Base
from DB.tabels import UserDB, CourierDB, ProductDB, OrderDB, OrderItemDB, CartDB
from sqlalchemy import text


#добавление таблиц в бд
def create_tables():
    Base.metadata.create_all(bind=engine)


#добавляем админа статически
def add_admin():
    from DBconnect import SessionLocal
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT * FROM users WHERE role = 'admin'")).fetchone()
        if not result:
            db.execute(text("""
                INSERT INTO users (username, email, password, role, api_key, created_at)
                VALUES ('admin', 'admin@shop.com', 'admin123', 'admin', 'admin_key_123', NOW())
            """))
            db.commit()
            print("админ создан, логин: admin, пароль: admin123")
        else:
            print("админ уже существует")
    except Exception as e:
        print(f"ошибка при добавлении админа")
        db.rollback()
    finally:
        db.close()



if __name__ == "__main__":
    create_tables()
    add_admin()
    print("бд создана")