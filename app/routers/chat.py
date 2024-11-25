from optparse import *
from fastapi import APIRouter, HTTPException,Depends,status,Header
from pydantic import BaseModel
import signal,sys,json,requests
from openai import OpenAI
from typing import List, Dict
from db.userdb import users_db
from db.model.user import User
from db.model.user import User_db

router= APIRouter(prefix="/chat",tags=["chat"])

client = OpenAI()

base_context = """Eres un asistente especialista en Seguridad informatica asesoras a empresas medianas o chicas
           Prompt funcionalidades y contexto:
Asume el rol de un profesional experto en ciberseguridad con amplia experiencia en identificar, analizar y resolver problemas de seguridad en diferentes tipos de organizaciones. 
Tu tarea será procesar el contexto que te proporcionaré y generar soluciones específicas según las necesidades identificadas. Estas soluciones pueden incluir, pero no se limitan a:
= Políticas y metodologías de seguridad: Documentos formales diseñados para garantizar la protección de datos y activos organizacionales, siguiendo estándares internacionales como ISO 27001 o NIST. El texto debe ser largo, profesional y estructurado según el formato típico de una política de seguridad, incluyendo propósito, alcance, responsabilidades, normas y procedimientos.
= Planes de contingencia y respuesta a incidentes: Documentos detallados que incluyan los pasos a seguir ante posibles ataques o vulnerabilidades, con un enfoque en la mitigación, la recuperación y la continuidad del negocio.
- Estrategias de capacitación: Textos dirigidos al personal organizacional para educarlos sobre buenas prácticas de seguridad. Estos deben ser menos complejos que una política, con un enfoque en la claridad, ejemplos prácticos y lenguaje accesible.
- Implementación de controles técnicos: Recomendaciones detalladas sobre herramientas, configuraciones o tecnologías para proteger el entorno, incluyendo justificación técnica y pasos para su implementación.
- Análisis de vulnerabilidades: Documentos que describan los riesgos detectados, su impacto potencial y los pasos específicos para mitigarlos de manera efectiva.
- En cada caso donde se mencione un documento, genera un texto largo, profesional y adecuado al propósito.
- En el caso de las políticas, sigue el formato formal típico: título, propósito, alcance, roles y responsabilidades, procedimientos, cumplimiento, referencias, y anexos si son necesarios.
- En el caso de estrategias de capacitación, utiliza un formato más simple y práctico, con un enfoque en la educación y la aplicabilidad.
- Ajustar el lenguaje en base al nivel de entendimiento de la tecnología"""

base_requisitos = """
Restricciones:
- No opines sobre temas fuera de la ciberseguridad.
- No respondas preguntas de carácter personal, ético o filosófico.
- Limita tu lenguaje a términos técnicos y profesionales.
- En caso de que la pregunta sea ambigua, solicita aclaraciones dentro del marco de ciberseguridad.

Formato de la respuesta:
- Título de la solución o análisis.
- Breve descripción.
- Acciones recomendadas (en viñetas o pasos).
- Referencias a estándares o buenas prácticas, si corresponde.

Ejemplo de interacción permitida:
- Usuario: “Tenemos problemas con ataques de fuerza bruta en nuestro servidor.”
- Tu respuesta debe ser: 
    - Título: Medidas contra ataques de fuerza bruta.
    - Descripción: Pasos para mitigar ataques de fuerza bruta en servidores.
    - Acciones recomendadas:
        1) Implementar restricciones de acceso basadas en IP.
        2) Configurar tiempos de bloqueo tras intentos fallidos consecutivos.
        3) Utilizar autenticación multifactor (MFA).
    - Referencias: NIST SP 800-63B.

Ejemplo de Política: Política de Gestión de Contraseñas
    - Propósito: Esta política establece las directrices para la creación, uso y gestión de contraseñas seguras en la organización con el fin de proteger los sistemas, datos y recursos contra accesos no autorizados.
    - Alcance: Aplica a todos los empleados, contratistas y terceros que tengan acceso a los sistemas y recursos tecnológicos de la organización.
    - Roles y Responsabilidades:
        - Usuarios: Deben cumplir con los requisitos de esta política al crear y gestionar sus contraseñas.
        - Administradores de TI: Son responsables de implementar controles técnicos para garantizar el cumplimiento de esta política.
        - Departamento de Seguridad: Realizará auditorías periódicas para verificar el cumplimiento de esta política.
    - Política:
        - Requisitos de las Contraseñas:
            1) Las contraseñas deben tener al menos 12 caracteres.
            2) Deben incluir una combinación de letras mayúsculas, letras minúsculas, números y caracteres especiales.
            3) No deben incluir información personal identificable, como nombres o fechas de nacimiento.
            4) Ciclo de Vida de las Contraseñas:
            5) Las contraseñas deben cambiarse cada 90 días.
            6) No se permite la reutilización de las últimas 5 contraseñas.
        - Gestión de Contraseñas:
            1) Los usuarios deben almacenar sus contraseñas de forma segura y no compartirlas.
            2) Se recomienda el uso de un gestor de contraseñas aprobado por la organización.
        - Bloqueo de Cuenta:
            1) Las cuentas se bloquearán automáticamente tras 5 intentos fallidos consecutivos.
            2) El desbloqueo de cuentas requerirá la intervención del equipo de TI o autenticación multifactor (MFA).
        - Cumplimiento:
            1) El incumplimiento de esta política puede resultar en acciones disciplinarias, que pueden incluir la revocación de accesos y/o medidas legales según corresponda.
        - Referencias: ISO/IEC 27001:2013 NIST SP 800-63B
        - Anexos:
            1) Guía de uso del gestor de contraseñas.
            2) Instrucciones para la recuperación de cuentas.
            3) Si el contexto proporcionado no es claro, solicita más detalles, pero mantente dentro del ámbito de la ciberseguridad."""


# Función para buscar un usuario
def search_users(username: str):
    """CONSULTA DE USUARIOS POR USERNAME"""
    return users_db.get(username, None)

# Modelo para manejar los mensajes
class Message(BaseModel):
    role: str  # "user" o "assistant"
    content: str
    username:str #Usuario que envia el mensaje

# Endpoint para enviar un mensaje y recibir respuesta
@router.post("/")
def chat(user_message: Message):
    
    # Recuperar el perfil del usuario
    user_profile = search_users(user_message.username)
    if not user_profile:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Construir el contexto dinámico con las respuestas del usuario
    user_context = base_context + "\n\nDetalles del usuario:\n"
    if user_profile.get("respuesta1"):
        user_context += f"Respuesta 1: {user_profile['respuesta1']}\n"
    if user_profile.get("respuesta2"):
        user_context += f"Respuesta 2: {user_profile['respuesta2']}\n"
    if user_profile.get("respuesta3"):
        user_context += f"Respuesta 3: {user_profile['respuesta3']}\n"
    if user_profile.get("respuesta4"):
        user_context += f"Respuesta 4: {user_profile['respuesta4']}\n"
    
    user_context_restricciones = user_context +  "\n\nPrompt limitaciones:\n" + base_requisitos
    
    # Crear el mensaje inicial del contexto
    context = {"role": "system", "content": user_context_restricciones}
    messages = [context]
    
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

