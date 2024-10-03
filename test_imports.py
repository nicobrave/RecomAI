from database import db_recomai  # Asegúrate de importar correctamente tu base de datos

# Realiza la consulta a la colección de usuarios con la API Key que quieres validar
usuario = db_recomai.usuarios.find_one({"api_key": "14af42625ea1a749250734a53742f8558cbcfb875ad2ce9d3e930bfcb0321926"})

# Verifica si encontró el usuario
if usuario:
    print("Usuario encontrado:", usuario)
else:
    print("API Key no encontrada o inválida")
