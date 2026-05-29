from fastapi import FastAPI
from Endpoints.couriers import router as couriers_router
from Endpoints.orders import router as orders_router


app = FastAPI()

app.include_router(couriers_router)
app.include_router(orders_router)


@app.get("/")
def root():
    return {"message": "Доставка посылок"}