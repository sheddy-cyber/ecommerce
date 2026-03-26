from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import Base, engine
import models.user, models.product, models.order
from routers import auth, products, orders, websockets

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(websockets.router)

@app.get("/")
def root():
    return {"message": "Ecommerce API is running"}