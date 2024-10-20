from optparse import *
from fastapi import APIRouter, HTTPException,Depends,status,Header
from pydantic import BaseModel
import signal,sys,json,requests
from openai import OpenAI
from typing import List, Dict

router= APIRouter(prefix="/chat",tags=["chat"])

client = OpenAI()

#CONTEXTO DE GPT
context = {"role":"system","content":"Eres un asistente especialista en Seguridad informatica asesoras a empresas medianas o chicas"}
messages = [context]


# Modelo para manejar los mensajes
class Message(BaseModel):
    role: str  # "user" o "assistant"
    content: str

# Endpoint para enviar un mensaje y recibir respuesta
@router.post("/")
def chat(user_message: Message):
    
    # Agregar el mensaje del usuario al historial
    messages.append(user_message)

    # Llamar a la API de OpenAI con el historial completo del chat
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        # Obtener la respuesta del sistema
        response_content = response.choices[0].message.content

        # Agregar la respuesta del sistema al historial
        messages.append({"role":"assistant","content":response_content})

        return {"response": response_content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

