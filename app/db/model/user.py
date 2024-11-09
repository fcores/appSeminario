from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str | None = None
    username:str
    disabled: bool | None = None
    respuesta1:str | None = None
    respuesta2:str | None = None
    respuesta3:str | None = None
    respuesta4:str | None = None
    
class User_db(User):
    password:str