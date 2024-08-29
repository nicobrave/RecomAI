import pandas as pd
import openai
import os

# Cargar la API key desde el entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

df_trabajadores = pd.read_csv(r"C:\Users\Usuario\Desktop\RecomAI\trabajadores.csv")

def obtener_mejor_candidato(cargo: str):
    # Filtramos los trabajadores por el cargo
    candidatos = df_trabajadores[df_trabajadores['Ultimo_Cargo'].str.contains(cargo, case=False, na=False)]
    
    if candidatos.empty:
        return "No se encontró una recomendación adecuada."
    
    # Tomamos el primer candidato después de ordenar por experiencia, educación, etc.
    mejor_candidato = candidatos.iloc[0]
    
    # Construimos el nombre completo
    nombre_completo = f"{mejor_candidato['names']} {mejor_candidato['lastName']} {mejor_candidato['mothers_LastName']}"
    
    # Creamos el prompt para OpenAI
    prompt = f"Recomienda al mejor candidato para el cargo de {cargo} basándote en el siguiente perfil:\n\n" \
             f"Nombre completo: {nombre_completo}\n" \
             f"Cargo anterior: {mejor_candidato['Ultimo_Cargo']}\n" \
             f"Experiencia: {mejor_candidato['Ultimo_Detalle_Experiencia']}\n" \
             f"Educación: {mejor_candidato['Ultimo_Estudio']}\n" \
             f"Remuneración: {mejor_candidato['Remuneracion']}\n"
    
    # Llamamos a OpenAI para obtener la recomendación
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Actúa como un reclutador."},
                  {"role": "user", "content": prompt}]
    )
    
    # Devolvemos la recomendación y el nombre completo del candidato
    return {
        "nombre_completo": nombre_completo,
        "recomendacion": response.choices[0].message['content']
    }