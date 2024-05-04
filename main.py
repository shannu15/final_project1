from fastapi import FastAPI, Depends
from init_db import get_db_conn 
from routers.customer_router import router as customer_router
from routers.item_router import router as item_router
from routers.order_router import router as order_router
app = FastAPI()
app.include_router(customer_router)
app.include_router(item_router)
app.include_router(order_router)