from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import config
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
df_trabajadores = pd.read_csv(r"C:\Users\Usuario\Desktop\RecomAI\trabajadores.csv")

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