# test_imports.py

from database import init_db_recomai

def test_init_db_recomai():
    try:
        init_db_recomai()
        print("init_db_recomai importado y ejecutado correctamente.")
    except Exception as e:
        print(f"Error al importar o ejecutar init_db_recomai: {e}")

if __name__ == "__main__":
    test_init_db_recomai()
