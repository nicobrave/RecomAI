from fastapi import Depends, HTTPException
from database import obtener_usuario_por_api_key

def validar_api_key(api_key: str = Depends()):
    usuario = obtener_usuario_por_api_key(api_key)
    if not usuario:
        raise HTTPException(status_code=403, detail="API Key no válida")
    return api_key
