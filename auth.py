import secrets
import datetime
from fastapi import HTTPException, Request
from database import db
from plans import limite_solicitudes

def generar_api_key():
    """Genera una API key única."""
    return secrets.token_hex(32)  # 64 caracteres hexadecimales

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

    # Incrementar el contador de solicitudes
    incrementar_solicitudes(api_key)

    return usuario