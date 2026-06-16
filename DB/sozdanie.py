from DB.DBconnect import engine, Base
import DB.tabels
from sqlalchemy import text

def create_tables():
    print("Создаём таблицы")
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы")


def add_admin():
    from DB.DBconnect import SessionLocal
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
        print(f"ошибка при добавлении админа: {e}")
        db.rollback()
    finally:
        db.close()


def add_test_user():
    from DB.DBconnect import SessionLocal
    db = SessionLocal()
    try:
        #проверяем, существует ли пользователь customer1
        result = db.execute(text("SELECT * FROM users WHERE username = 'customer1'")).fetchone()
        if not result:
            db.execute(text("""
                INSERT INTO users (username, email, password, role, api_key, address, created_at)
                VALUES ('customer1', 'customer1@test.com', 'customer1', 'customer', 'customer_key_123', 'г. Москва, ул. Тестовая, д.1', NOW())
            """))
            db.commit()
            print("покупатель создан, логин: customer1, пароль: customer1")
        else:
            print("покупатель customer1 уже существует")
    except Exception as e:
        print(f"ошибка при добавлении покупателя: {e}")
        db.rollback()
    finally:
        db.close()


def add_test_courier():
    from DB.DBconnect import SessionLocal
    db = SessionLocal()
    try:
        #проверяем, существует ли курьер
        result = db.execute(text("""
            SELECT u.username FROM users u 
            JOIN couriers c ON u.id_user = c.id_user 
            WHERE u.username = 'courier1'
        """)).fetchone()

        if not result:
            #создаём пользователя-курьера
            db.execute(text("""
                INSERT INTO users (username, email, password, role, api_key, created_at)
                VALUES ('courier1', 'courier1@test.com', 'courier1', 'courier', 'courier_key_123', NOW())
                RETURNING id_user
            """))
            db.commit()

            #получаем id
            user_result = db.execute(text("SELECT id_user FROM users WHERE username = 'courier1'")).fetchone()
            user_id = user_result[0]

            #создаём запись курьера
            db.execute(text("""
                INSERT INTO couriers (id_user, courier_type, regions, working_hours, max_load)
                VALUES (:user_id, 'foot', :regions, :working_hours, 10)
            """), {
                'user_id': user_id,
                'regions': '[1, 2, 3, 4, 5]',
                'working_hours': '["9:00-21:00"]'
            })
            db.commit()
            print("курьер создан, логин: courier1, пароль: courier1")
            print("тип: пеший, регионы: [1,2,3,4,5], часы работы: 9:00-21:00")
        else:
            print("курьер courier1 уже существует")
    except Exception as e:
        print(f"ошибка при добавлении курьера: {e}")
        db.rollback()
    finally:
        db.close()


def add_test_products():
    from DB.DBconnect import SessionLocal
    db = SessionLocal()
    try:
        #тестовые товары
        products = [
            {"id": 998, "name": "Тестовый товар 1", "price": 100.00, "weight": 0.5, "category": "тестовый товар"},
            {"id": 999, "name": "Тестовый товар 2", "price": 200.00, "weight": 1.0, "category": "тестовый товар"},
            {"id": 1000, "name": "Тестовый товар 3", "price": 300.00, "weight": 2.0, "category": "тестовый товар"},
        ]

        for product in products:
            #проверяем, существует ли товар
            result = db.execute(
                text("SELECT * FROM products WHERE id_product = :id"),
                {"id": product["id"]}
            ).fetchone()

            if not result:
                db.execute(text("""
                    INSERT INTO products (id_product, name, description, price, weight, category)
                    VALUES (:id, :name, :description, :price, :weight, :category)
                """), {
                    "id": product["id"],
                    "name": product["name"],
                    "description": f"Описание для {product['name']}",
                    "price": product["price"],
                    "weight": product["weight"],
                    "category": product["category"]
                })
                print(f"товар создан: {product['name']} (id={product['id']}, вес={product['weight']}кг)")
            else:
                print(f"товар уже существует: {product['name']}")

        db.commit()
        print("все тестовые товары добавлены")
    except Exception as e:
        print(f"ошибка при добавлении товаров: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    add_admin()
    add_test_user()
    add_test_courier()
    add_test_products()
    print("база данных полностью готова к работе!")
    print("Админ:admin / admin123")
    print("Покупатель:customer1 / customer1")
    print("Курьер:courier1 / courier1")

    print("id=998: Тестовый товар 1 (0.5 кг, 100 руб)")
    print("id=999: Тестовый товар 2 (1.0 кг, 200 руб)")
    print("id=1000: Тестовый товар 3 (2.0 кг, 300 руб)")
