from database import db_recomai

usuario = db_recomai.usuarios.find_one({"api_key": "14af42625ea1a749250734a53742f8558cbcfb875ad2ce9d3e930bfcb0321926"})
print(usuario)
