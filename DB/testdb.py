from DBconnect import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("подключение к бд есть")
except Exception as e:
    print("подключения к бд нет")