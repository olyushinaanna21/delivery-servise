from DB.DBconnect import engine, Base
import DB.tabels  # ← добавь этот импорт (он регистрирует модели)
from sqlalchemy import text

def create_tables():
    print("Создаём таблицы...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы")

def add_admin():
    from DB.DBconnect import SessionLocal
    db = SessionLocal()
    try:
        # Проверяем существование таблицы и наличие админа
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
        print(f"ошибка при добавлении админа: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    add_admin()
    print("бд создана")