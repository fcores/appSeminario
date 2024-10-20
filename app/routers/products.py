from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/products",
                   responses={404:{"message":"No encontrado"}},
                   tags=["products"])

class Product(BaseModel):
    id:int
    description: str
    price: int | None = None
    
productsLista = [Product(id=1,description="Computadora",price=29),Product(id=2,description="Paleta",price=5445)]

@router.get("/")
async def products():
    """CONSULTA GENERAL DE UNA LISTA"""
    return productsLista


@router.get("/{id}")
async def products(id:int):
    """CONSULTA GENERAL DE UNA LISTA"""
    try:    
        return productsLista[id]
    except:
        raise HTTPException(status_code=409,detail="El producto esta fuera de rango")