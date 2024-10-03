import uuid
from database import usuarios_collection
from datetime import datetime

def crear_usuario(nombre, email, plan="basico"):
    api_key = str(uuid.uuid4())  # Genera una API key única
    nuevo_usuario = {
        "nombre": nombre,
        "email": email,
        "api_key": api_key,
        "plan": plan,
        "solicitudes_realizadas": 0,
        "fecha_creacion": datetime.utcnow()
    }
    usuarios_collection.insert_one(nuevo_usuario)
    return nuevo_usuario

if __name__ == "__main__":

    # Crear usuario con valores predefinidos
    nombre = "WorkID"
    email = "nico@recomai.cl"
    plan = "basico"
    usuario_creado = crear_usuario(nombre, email, plan)
    print(f"Usuario creado con ID: {usuario_creado['_id']}, API Key: {usuario_creado['api_key']}")
