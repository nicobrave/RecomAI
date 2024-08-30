import secrets
import datetime
from fastapi import HTTPException, Request
from database import db
from plans import limite_solicitudes

def generar_api_key():
    """Genera una API key única."""
<<<<<<< HEAD
    return secrets.token_hex(32)  # 64 caracteres hexadecimales
=======
    return secrets.token_hex(32)

def crear_usuario(nombre: str, email: str, plan: str):
    """Crea un nuevo usuario con una API key y lo almacena en MongoDB."""
    api_key = generar_api_key()
    nuevo_usuario = {
        "nombre": nombre,
        "email": email,
        "api_key": api_key,
        "plan": plan,
        "solicitudes_realizadas": 0,
        "fecha_creacion": datetime.datetime.utcnow()
    }
    db.usuarios.insert_one(nuevo_usuario)
    return api_key
>>>>>>> 9ce8628c109b7d6b84123870c8e60c04925f3405

def obtener_usuario_por_api_key(api_key: str):
    """Obtiene un usuario desde MongoDB usando su API key."""
    return db.usuarios.find_one({"api_key": api_key})

def incrementar_solicitudes(api_key: str):
    """Incrementa el contador de solicitudes realizadas por un usuario."""
    usuario = obtener_usuario_por_api_key(api_key)
    if usuario:
        db.usuarios.update_one(
            {"api_key": api_key},
            {"$inc": {"solicitudes_realizadas": 1}}
        )

async def validar_api_key(request: Request):
    """Middleware para validar la API key en cada solicitud."""
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        raise HTTPException(status_code=400, detail="API key requerida")
    
    usuario = obtener_usuario_por_api_key(api_key)
    if not usuario:
        raise HTTPException(status_code=403, detail="API key inválida")

<<<<<<< HEAD
    # Incrementar el contador de solicitudes
    incrementar_solicitudes(api_key)

    return usuario
=======
    # Verificar los límites de uso del plan de suscripción
    if usuario["solicitudes_realizadas"] >= limite_solicitudes(usuario["plan"]):
        raise HTTPException(status_code=429, detail="Límite de solicitudes alcanzado para este plan")

    # Incrementar el contador de solicitudes
    incrementar_solicitudes(api_key)

    return usuario
>>>>>>> 9ce8628c109b7d6b84123870c8e60c04925f3405
