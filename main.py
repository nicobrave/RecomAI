from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
import config
import openai
import os
import pandas as pd
=======
import openai
import os
import config  # Importa config para cargar la API key
>>>>>>> 9ce8628c109b7d6b84123870c8e60c04925f3405
from auth import validar_api_key
from recommendations import obtener_mejor_candidato

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=["*"],
=======
    allow_origins=["https://recomai.vercel.app/"],
>>>>>>> 9ce8628c109b7d6b84123870c8e60c04925f3405
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
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
=======
@app.get("/recomendaciones")
async def obtener_recomendaciones(cargo: str, usuario=Depends(validar_api_key)):
    try:
        recomendacion = obtener_mejor_candidato(cargo)
        return recomendacion
    except Exception as e:
        print(f"Error al obtener la recomendación: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.options("/recomendaciones")
async def opciones():
    return JSONResponse({"status": "ok"}, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
>>>>>>> 9ce8628c109b7d6b84123870c8e60c04925f3405
