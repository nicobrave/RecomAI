from fastapi import HTTPException
from database import obtener_usuario_por_api_key

def validar_api_key(api_key: str):
    """
    Valida la API Key proporcionada por el cliente.
    
    Args:
    - api_key (str): La clave API que se va a validar.
    
    Returns:
    - str: La API Key si es válida.
    
    Raises:
    - HTTPException: Si la API Key no es válida.
    """
    usuario = obtener_usuario_por_api_key(api_key)
    if not usuario:
        raise HTTPException(status_code=403, detail="API Key no válida")
    return api_key
