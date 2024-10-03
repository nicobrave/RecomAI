import secrets
from flask import request, abort
from database import usuarios_collection, obtener_usuario_por_api_key, incrementar_solicitudes
from plans import limite_solicitudes

def generar_api_key():
    """Genera una API key única."""
    return secrets.token_hex(32)  # 64 caracteres hexadecimales

def obtener_usuario_por_api_key(api_key: str):
    """Obtiene un usuario desde MongoDB usando su API key."""
    return usuarios_collection.find_one({"api_key": api_key})

def incrementar_solicitudes(api_key: str):
    """Incrementa el contador de solicitudes realizadas por un usuario."""
    usuario = obtener_usuario_por_api_key(api_key)
    if usuario:
        usuarios_collection.update_one(
            {"api_key": api_key},
            {"$inc": {"solicitudes_realizadas": 1}}
        )

def validar_api_key():
    """Middleware to validate the API key on each request."""

    # Get the API key from the request headers
    api_key = request.headers.get('X-API-KEY')
    
    # Check if the API key was provided
    if not api_key:
        abort(400, description="API key requerida")
    
    # Check if the user associated with the API key exists
    usuario = obtener_usuario_por_api_key(api_key)
    if not usuario:
        abort(403, description="API key inválida")
    
    # Increment the number of requests made by this API key
    incrementar_solicitudes(api_key)
    
    # Get the user's plan and check if they have reached their request limit
    plan = usuario.get('plan')
    if usuario['solicitudes_realizadas'] >= limite_solicitudes(plan):
        abort(429, description="Límite de solicitudes alcanzado para el plan actual")
    
    # If everything is valid, return the user data (this can be used in other routes)
    return usuario
