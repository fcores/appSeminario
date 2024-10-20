from fastapi import APIRouter, HTTPException,Depends,status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from db.model.user import User, User_db
from db.userdb import users_db


router = APIRouter(prefix="/login")

oauth2 = OAuth2PasswordBearer(tokenUrl="login")
    

def search_user_db(username:str):
    if username in users_db:
        return User_db(**users_db[username])
    
def search_user(username:str):
    if username in users_db:
        return User(**users_db[username])
    

async def current_user(token:str =Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Credenciales de autenticacion invalidas",headers={"www-Authenticate":"Bearer"})
    
    if not user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Usuario Inactivo",headers={"www-Authenticate":"Bearer"})
    return user   

@router.post("/")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400,detail="El usuario no es correcto")
    
    user = search_user_db(form.username)
    
    print(user)
    if not form.password == user.password:
        raise HTTPException(status_code=400,detail="La contrasegna no es correcto")
    
    return {"access_token": user.username, "token_type": "bearer"}

@router.get("/users/me")
async def me(  user : User = Depends(current_user)):
    return user