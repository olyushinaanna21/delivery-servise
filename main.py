from fastapi import FastAPI
from Endpoints.couriers import router as couriers_router


app = FastAPI()

app.include_router(couriers_router)


@app.get("/")
def root():
    return {"message": "Доставка посылок"}