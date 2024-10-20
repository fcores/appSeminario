from pydantic import BaseModel

class User(BaseModel):
    id:int
    name: str
    email: str | None = None
    age: int | None = None
    empresa:str | None = None
    username:str
    full_name: str
    disabled: bool | None = None
    
class User_db(User):
    password:str