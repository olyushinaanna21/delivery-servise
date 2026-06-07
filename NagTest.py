from locust import HttpUser, task, between
import random


#покупатель
class CustomerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.username = f"load_user_{random.randint(1, 1000000)}"
        self.password = "test123"
        self.headers = None
        self.user_id = None
        self.last_order_id = None

        # Регистрация
        response = self.client.post("/auth/register", json={
            "username": self.username,
            "email": f"{self.username}@test.com",
            "password": self.password,
            "address": "ул. Тестовая, 1",
            "region": 5
        })

        if response.status_code == 201:
            self.api_key = response.json()["api_key"]
            self.user_id = response.json()["user_id"]
            self.headers = {"API-Token": self.api_key}
        else:
            login_response = self.client.post("/auth/login", json={
                "username": self.username,
                "password": self.password
            })
            if login_response.status_code == 200:
                self.api_key = login_response.json()["api_key"]
                self.user_id = login_response.json()["user_id"]
                self.headers = {"API-Token": self.api_key}
            else:
                print(f"Не удалось создать пользователя {self.username}")
                self.headers = None
                self.user_id = None
                self.last_order_id = None


    #задача + вес задачи(частота выполнения)
    #просмотр каталога товаров
    @task(5)
    def view_products(self):
        if self.headers:
            self.client.get("/products", headers=self.headers)
        else:
            print("Нет заголовка с апи ключом")


    #просмотр конкретного товара(странички товара)
    @task(3)
    def view_product_detail(self):
        if self.headers:
            product_id = 998
            self.client.get(f"/products/{product_id}", headers=self.headers)


    #добавление товара в козину
    @task(2)
    def add_to_cart(self):
        if self.headers:
            self.client.post("/cart/add", params={"product_id": 998,"quantity": random.randint(1, 3)}, headers=self.headers)


    #создание заказа
    @task(1)
    def checkout(self):
        if self.headers:
            #товар
            self.client.post("/cart/add", params={"product_id": 998,"quantity": 1}, headers=self.headers)

            #заказ
            response = self.client.post("/orders/checkout", json={
                "delivery_hours": ["09:00-12:00"],
                "address": "ул. Тестовая, 1",
                "region": 5
            }, headers=self.headers)

            #сохраняем айди заказа для получения деталей заказа
            if response.status_code == 200:
                self.last_order_id = response.json()["order_id"]


    #просмотр заказов
    @task(2)
    def view_my_orders(self):
        if self.headers:
            self.client.get("/orders/my", headers=self.headers)


    #просмотр корзины
    @task(1)
    def view_cart(self):
        if self.headers:
            self.client.get("/cart", headers=self.headers)


    #очистка корзины
    @task(1)
    def clear_cart(self):
        if self.headers:
            self.client.delete("/cart/clear", headers=self.headers)


    #получение своего профиля (из айди)
    @task(1)
    def get_my_profile(self):
        if self.headers and self.user_id:
            self.client.get(f"/users/{self.user_id}", headers=self.headers)


    #изменение количества товара в корзине
    @task(1)
    def update_cart_quantity(self):
        if self.headers:
            self.client.patch("/cart/update", params={"product_id": 998,"quantity": random.randint(1, 5)}, headers=self.headers)


    #удаление товара из корзины
    @task(1)
    def remove_from_cart(self):
        if self.headers:
            self.client.delete(f"/cart/remove/998", headers=self.headers)

    #получение деталей заказа
    @task(1)
    def get_order_detail(self):
        if self.headers and self.last_order_id:
            self.client.get(f"/orders/my/{self.last_order_id}", headers=self.headers)

    #выход из системы
    @task(1)
    def logout(self):
        if self.headers:
            self.client.post("/auth/logout", headers=self.headers)
            self.headers = None

    #получение списка категорий
    @task(1)
    def get_categories(self):
        if self.headers:
            self.client.get("/products/categories/all", headers=self.headers)




#администратор
class AdminUser(HttpUser):
    wait_time = between(2, 5)



    def on_start(self):
        response = self.client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code == 200:
            self.api_key = response.json()["api_key"]
            self.headers = {"API-Token": self.api_key}
        else:
            self.headers = None


    #получить всех пользователей
    @task(2)
    def get_all_users(self):
        if self.headers:
            self.client.get("/admin/users", headers=self.headers)


    #получить все заказы
    @task(2)
    def get_all_orders(self):
        if self.headers:
            self.client.get("/admin/orders", headers=self.headers)


    #получить всех курьеров
    @task(1)
    def get_all_couriers(self):
        if self.headers:
            self.client.get("/couriers", headers=self.headers)

    #получить заказы курьера
    @task(1)
    def get_user_orders(self):
        if self.headers:
            self.client.get("/admin/users/1/orders", headers=self.headers)


    #получить пользователя по айди
    @task(1)
    def get_user_by_id(self):
        if self.headers:
            self.client.get("/admin/users/1", headers=self.headers)


    #изменить роль пользователя
    @task(1)
    def change_user_role(self):
        if self.headers:
            self.client.patch("/admin/users/1/role?role=customer", headers=self.headers)


    #создать товар
    @task(1)
    def create_product(self):
        if self.headers:
            unique_id = random.randint(9000, 9999)
            self.client.post("/admin/products", json={
                "id": unique_id,
                "name": f"Нагрузочный товар {unique_id}",
                "description": "Создан во время нагрузочного теста",
                "price": 100,
                "weight": 0.5,
                "image_url": "https://example.com/test.jpg",
                "category": "load_test"
            }, headers=self.headers)


    #обновить товар
    @task(1)
    def update_product(self):
        if self.headers:self.client.patch("/admin/products/998", json={"price": 150}, headers=self.headers)






#курьер
class CourierLoadUser(HttpUser):
    wait_time = between(1, 4)

    def on_start(self):
        response = self.client.post("/auth/login", json={
            "username": "courier1",
            "password": "12345678"
        })
        if response.status_code == 200:
            self.api_key = response.json()["api_key"]
            self.headers = {"API-Token": self.api_key}
        else:
            self.headers = None


    #получить свободные заказы
    @task(3)
    def get_available_orders(self):
        if self.headers:
            self.client.get("/courier/orders/available", headers=self.headers)


    #посмотреть профиль
    @task(2)
    def get_my_profile(self):
        if self.headers:
            self.client.get("/courier/me", headers=self.headers)


    #посмотреть свои заказы
    @task(1)
    def get_my_orders(self):
        if self.headers:
            self.client.get("/courier/orders/my", headers=self.headers)


    #посмотреть заработок
    @task(1)
    def get_earnings(self):
        if self.headers:
            self.client.get("/courier/earnings", headers=self.headers)


    #посмотреть рейтинг
    @task(1)
    def get_rating(self):
        if self.headers:
            self.client.get("/courier/rating", headers=self.headers)


    #взять себе заказ
    @task(1)
    def take_order(self):
        if self.headers:
            response = self.client.get("/courier/orders/available", headers=self.headers)
            if response.status_code == 200 and response.json()["orders"]:
                order_id = response.json()["orders"][0]["order_id"]
                self.client.post(f"/courier/orders/take/{order_id}", headers=self.headers)


    #завершить(выполнить) заказ
    @task(1)
    def complete_order(self):
        if self.headers:
            response = self.client.get("/courier/orders/my", headers=self.headers)
            if response.status_code == 200 and response.json()["orders"]:
                order_id = response.json()["orders"][0]["order_id"]
                self.client.post(f"/courier/orders/complete/{order_id}", headers=self.headers)


    #получение информации о курьере по айди
    @task(1)
    def get_courier_info(self):
        if self.headers:
            self.client.get("/couriers/1", headers=self.headers)






class MixedLoadUser(HttpUser):

    wait_time = between(1, 3)

    def on_start(self):
        self.role = random.choice(['customer', 'admin', 'courier'])
        self.headers = None

        if self.role == 'customer':
            self.username = f"load_user_{random.randint(1, 1000000)}"
            response = self.client.post("/auth/register", json={
                "username": self.username,
                "email": f"{self.username}@test.com",
                "password": "test123",
                "address": "ул. Тестовая, 1",
                "region": 5
            })
            if response.status_code == 201:
                self.api_key = response.json()["api_key"]
                self.headers = {"API-Token": self.api_key}

        elif self.role == 'admin':
            response = self.client.post("/auth/login", json={
                "username": "admin",
                "password": "admin123"
            })
            if response.status_code == 200:
                self.api_key = response.json()["api_key"]
                self.headers = {"API-Token": self.api_key}

        else:  # courier
            response = self.client.post("/auth/login", json={
                "username": "courier1",
                "password": "12345678"
            })
            if response.status_code == 200:
                self.api_key = response.json()["api_key"]
                self.headers = {"API-Token": self.api_key}

    @task
    def do_task(self):
        if not self.headers:
            return

        if self.role == 'customer':
            actions = [
                lambda: self.client.get("/products", headers=self.headers),
                lambda: self.client.get("/products/998", headers=self.headers),  # ← добавить
                lambda: self.client.get("/cart", headers=self.headers),
                lambda: self.client.post("/cart/add", params={"product_id": 998, "quantity": 1}, headers=self.headers),
                lambda: self.client.patch("/cart/update", params={"product_id": 998, "quantity": 2},headers=self.headers),
                lambda: self.client.delete("/cart/remove/998", headers=self.headers),
                lambda: self.client.delete("/cart/clear", headers=self.headers),
                lambda: self.client.get("/orders/my", headers=self.headers),
                lambda: self.client.post("/orders/checkout", json={
                    "delivery_hours": ["09:00-12:00"],
                    "address": "ул. Тестовая, 1",
                    "region": 5
                }, headers=self.headers),
            ]
        elif self.role == 'admin':
            actions = [
                lambda: self.client.get("/admin/users", headers=self.headers),
                lambda: self.client.get("/admin/orders", headers=self.headers),
                lambda: self.client.get("/couriers", headers=self.headers),
                lambda: self.client.get("/admin/users/1", headers=self.headers),
                lambda: self.client.get("/admin/users/1/orders", headers=self.headers),
                lambda: self.client.get("/couriers/1", headers=self.headers),
                lambda: self.client.get("/products/categories/all", headers=self.headers),
                lambda: self.client.post("/admin/products", json={
                    "id": random.randint(9000, 9999),
                    "name": f"LoadTest_{random.randint(1, 1000)}",
                    "description": "Создан нагрузочным тестом",
                    "price": 100,
                    "weight": 0.5,
                    "image_url": "",
                    "category": "load_test"
                }, headers=self.headers),
            ]
        else:
            actions = [
                lambda: self.client.get("/courier/orders/available", headers=self.headers),
                lambda: self.client.get("/courier/me", headers=self.headers),
                lambda: self.client.get("/courier/orders/my", headers=self.headers),
                lambda: self.client.get("/courier/earnings", headers=self.headers),
                lambda: self.client.get("/courier/rating", headers=self.headers),
                lambda: self.client.get("/couriers/1", headers=self.headers),
            ]

        random.choice(actions)()