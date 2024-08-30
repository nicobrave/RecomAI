from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import config
import requests
import uvicorn
import openai
import os
import pandas as pd
from auth import validar_api_key
from recommendations import obtener_mejor_candidato

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar los datos
# URL del archivo en Google Drive
url = "https://drive.google.com/uc?export=download&id=1ZaYiCQ7oJEEcNHPT0z_UAvQvNLN4AN9W"

# Realiza la solicitud GET para descargar el archivo
response = requests.get(url)

# Guarda el contenido en un archivo local
with open('trabajadores.csv', 'wb') as file:
    file.write(response.content)

# Ahora puedes leer el archivo como lo harías normalmente
df_trabajadores = pd.read_csv('trabajadores.csv')

# Endpoint para obtener el cargo
@app.get("/cargos")
async def obtener_cargos():
    try:
        # Obtener los 15 cargos más comunes
        cargos = df_trabajadores['Ultimo_Cargo'].value_counts().nlargest(15).index.tolist()
        return {"cargos": cargos}
    except Exception as e:
        print(f"Error al obtener cargos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoint para obtener recomendaciones basado en el cargo
@app.get("/recomendaciones")
async def obtener_recomendaciones(cargo: str, api_key: str = Depends(validar_api_key)):
    return obtener_mejor_candidato(cargo)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/", response_class=HTMLResponse)
def serve_home():
    with open("index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
