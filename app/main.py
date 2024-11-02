from fastapi import FastAPI
from routers import products
from routers import users
from routers import basic_auth_users
from routers import chat
from fastapi.staticfiles import StaticFiles

app = FastAPI()

#Routers
app.include_router(users.router)
app.include_router(basic_auth_users.router)
app.mount("/static",StaticFiles(directory="static"),name="static")



@app.get("/")
async def root():
    return {"message": "Trabajo Practico Ciencia de Datos"}