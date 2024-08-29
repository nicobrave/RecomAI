from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
import config  # Importa config para cargar la API key
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

@app.get("/recomendaciones")
async def obtener_recomendaciones(cargo: str, usuario=Depends(validar_api_key)):
    try:
        recomendacion = obtener_mejor_candidato(cargo)
        return recomendacion
    except Exception as e:
        print(f"Error al obtener la recomendación: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/recomendaciones")
async def obtener_recomendaciones(cargo: str):
    try:
        recomendacion = obtener_mejor_candidato(cargo)
        return recomendacion
    except Exception as e:
        print(f"Error al obtener la recomendación: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
