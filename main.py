from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from Endpoints.authentics import router as auth_router
from Endpoints.users import router as users_router
from Endpoints.courier import router as courier_router
from Endpoints.couriers_admin import router as couriers_admin_router
from Endpoints.orders import router as orders_router
from Endpoints.carts import router as carts_router
from Endpoints.products import router as products_router
from Endpoints.products_admin import router as products_admin_router
from Endpoints.admins_orders import router as admins_orders_router
from Endpoints.users_admin import router as admin_users_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#подключаем все роутеры
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(courier_router)
app.include_router(couriers_admin_router)
app.include_router(orders_router)
app.include_router(carts_router)
app.include_router(products_router)
app.include_router(products_admin_router)
app.include_router(admins_orders_router)
app.include_router(admin_users_router)

@app.get("/")
def root():
    return {"message": "Доставка посылок"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )