from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from db.userdb import users_db
from db.model.user import User
from db.model.user import User_db

router = APIRouter(prefix="/users",tags=["users"])


@router.get("/")
async def users():
    """CONSULTA GENERAL DE UNA LISTA"""
    return users_db

@router.get("/{username}")
async def get_user_by_id(username: str):
    """CONSULTA USUARIO POR USERNAME SOBRE EL PATH"""
    user = search_users(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.post("/", status_code=201)
async def create_user(user: User_db):
    """CREAR USUARIOS NUEVOS"""
    if search_users(user.username):
        raise HTTPException(status_code=409, detail="El usuario ya existe")

    # Agregar el nuevo usuario al diccionario users_db
    users_db[user.username] = user.dict()
    return {"detail": "Usuario creado"}

@router.put("/", status_code=200)
async def update_user(user: User):
    """FUNCION PARA ACTUALIZAR USUARIOS"""
    existing_user = search_users(user.username)
    if not existing_user:
        raise HTTPException(status_code=404, detail="El usuario no fue encontrado")

    # Actualizar el usuario existente en users_db
    users_db[user.username] = user.dict()
    return {"detail": "Usuario modificado"}

@router.delete("/{username}")
async def delete_user(username: str):
    """FUNCION PARA BORRAR USUARIOS"""
    username_to_delete = None

    # Buscar el usuario por USERNAME en users_db
    for username, user_data in users_db.items():
        if user_data["username"] == username:
            username_to_delete = username
            break

    if not username_to_delete:
        raise HTTPException(status_code=404, detail="El usuario no fue encontrado")

    # Eliminar el usuario de users_db
    del users_db[username_to_delete]
    return {"detail": "Usuario eliminado"}

def search_users(username: str):
    """CONSULTA DE USUARIOS POR USERNAME"""
    for user_data in users_db.values():
        if user_data["username"] == username:
            return user_data
    return None