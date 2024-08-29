from pymongo import MongoClient

# Configura la URI de conexión a MongoDB Atlas
MONGO_URI = "mongodb+srv://nicobrave:7BJnxAPjSkV8DaCz@recomai.rhwff.mongodb.net/?retryWrites=true&w=majority&appName=RecomAI"  # Reemplaza con tu URI de MongoDB Atlas

client = MongoClient("mongodb+srv://nicobrave:7BJnxAPjSkV8DaCz@recomai.rhwff.mongodb.net/?retryWrites=true&w=majority&appName=RecomAI")
db = client.recomAI

def init_db():
    global client, db
    client = MongoClient(MONGO_URI)
    db = client.RecomAI  # Conecta a la base de datos RecomAI

def obtener_usuario_por_api_key(api_key: str):
    return db.usuarios.find_one({"api_key": api_key})

def incrementar_solicitudes(api_key: str):
    usuario = obtener_usuario_por_api_key(api_key)
    if usuario:
        db.usuarios.update_one({"api_key": api_key}, {"$inc": {"solicitudes_realizadas": 1}})
