from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from db.userdb import users_db
from db.model.user import User

router = APIRouter(prefix="/users",tags=["users"])


@router.get("/")
async def users():
    """CONSULTA GENERAL DE UNA LISTA"""
    return users_db

@router.get("/{id}")
async def get_user_by_id(id: int):
    """CONSULTA USUARIO POR ID SOBRE EL PATH"""
    user = search_users(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.post("/", status_code=201)
async def create_user(user: User):
    """CREAR USUARIOS NUEVOS"""
    if search_users(user.id):
        raise HTTPException(status_code=409, detail="El usuario ya existe")

    # Agregar el nuevo usuario al diccionario users_db
    users_db[user.username] = user.dict()
    return {"detail": "Usuario creado"}

@router.put("/", status_code=200)
async def update_user(user: User):
    """FUNCION PARA ACTUALIZAR USUARIOS"""
    existing_user = search_users(user.id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="El usuario no fue encontrado")

    # Actualizar el usuario existente en users_db
    users_db[user.username] = user.dict()
    return {"detail": "Usuario modificado"}

@router.delete("/{id}")
async def delete_user(id: int):
    """FUNCION PARA BORRAR USUARIOS"""
    username_to_delete = None

    # Buscar el usuario por ID en users_db
    for username, user_data in users_db.items():
        if user_data["id"] == id:
            username_to_delete = username
            break

    if not username_to_delete:
        raise HTTPException(status_code=404, detail="El usuario no fue encontrado")

    # Eliminar el usuario de users_db
    del users_db[username_to_delete]
    return {"detail": "Usuario eliminado"}

def search_users(id: int):
    """CONSULTA DE USUARIOS POR ID"""
    for user_data in users_db.values():
        if user_data["id"] == id:
            return user_data
    return None