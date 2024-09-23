from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde .env
load_dotenv()

# Configura la URI de conexión a MongoDB Atlas para RecomAI
MONGO_URI_RECOMAI = os.getenv("MONGO_URI_RECOMAI")
client_recomai = MongoClient(MONGO_URI_RECOMAI)
db_recomai = client_recomai.recomAI  # Conecta a la base de datos 'recomAI'

def init_db_recomai():
    global client_recomai, db_recomai
    client_recomai = MongoClient(MONGO_URI_RECOMAI)
    db_recomai = client_recomai.recomAI  # Conecta a la base de datos 'recomAI'

def obtener_usuario_por_api_key(api_key: str):
    return db_recomai.usuarios.find_one({"api_key": api_key})

def incrementar_solicitudes(api_key: str):
    usuario = obtener_usuario_por_api_key(api_key)
    if usuario:
        db_recomai.usuarios.update_one({"api_key": api_key}, {"$inc": {"solicitudes_realizadas": 1}})

# --------------------------------------------------------
# Configura la URI de conexión a MongoDB Atlas para Factura
MONGO_URI_FACTURA = os.getenv("MONGO_URI_FACTURA")
client_factura = MongoClient(MONGO_URI_FACTURA)
db_factura = client_factura.factura  # Conecta a la base de datos 'factura'

def init_db_factura():
    global client_factura, db_factura
    client_factura = MongoClient(MONGO_URI_FACTURA)
    db_factura = client_factura.factura  # Conecta a la base de datos 'factura'

def obtener_contrato_por_numero(numero_contrato: str):
    return db_factura.contracts.find_one({"number": numero_contrato})

def insertar_contrato(contrato_data):
    return db_factura.contracts.insert_one(contrato_data)

def obtener_ito_por_numero_contrato(numero_contrato: str):
    return db_factura.itos.find_one({"contract_number": numero_contrato})

def insertar_ito(itos_data: list):
    return db_factura.itos.insert_many(itos_data)

def insertar_factura(facturas_data: list):
    return db_factura.invoices.insert_many(facturas_data)

def obtener_facturas_pendientes():
    return db_factura.invoices.find({"status": "Pendiente"})
