import pandas as pd
import requests
import openai
import io
import os
import re
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cargar los datos
url = "https://drive.google.com/uc?export=download&id=1ZaYiCQ7oJEEcNHPT0z_UAvQvNLN4AN9W"
response = requests.get(url)
df_trabajadores = pd.read_csv(io.StringIO(response.text))

# Función para generar la recomendación utilizando OpenAI
def generar_recomendacion_openai(df_trabajadores, cargo=None, comuna=None, nivel_estudio=None, detalle_experiencia=None):
    try:
        # Crear perfiles de cada trabajador utilizando todas las columnas
        perfiles = []
        for index, row in df_trabajadores.iterrows():
            perfil = {
                "Nombre Completo": f"{row['names']} {row['lastName']} {row['mothers_LastName']}",
                "Genero": row['Genero'],
                "Fecha Nacimiento": row['Fecha_Nacimiento'],
                "Comuna": row['Comuna'],
                "Telefono": row['Telefono'],
                "Estado Laboral": row['Estado_Laboral'],
                "Remuneracion": row['Remuneracion'],
                "Ultimo Estudio": row['Ultimo_Estudio'],
                "Ultimo Cargo": row['Ultimo_Cargo'],
                "Ultimo Detalle de Experiencia": row['Ultimo_Detalle_Experiencia'],
                "Discapacidad": row['Discapacidad'],
                "Activo": row['Activo'],
                "Origen": row['Origen'],
                "Tipo de Usuario": row['Tipo_Usuario']
            }
            perfiles.append(perfil)

        # Ver los perfiles antes de aplicar cualquier filtro
        print(f"Total de perfiles sin filtrar: {len(perfiles)}")

        # Convertir las columnas relevantes a tipo string y manejar NaN
        for perfil in perfiles:
            perfil['Ultimo Cargo'] = str(perfil['Ultimo Cargo']).strip().lower() if pd.notna(perfil['Ultimo Cargo']) else ""
            perfil['Comuna'] = str(perfil['Comuna']).strip().lower() if pd.notna(perfil['Comuna']) else ""
            perfil['Ultimo Estudio'] = str(perfil['Ultimo Estudio']).strip().lower() if pd.notna(perfil['Ultimo Estudio']) else ""
            perfil['Ultimo Detalle de Experiencia'] = str(perfil['Ultimo Detalle de Experiencia']).strip().lower() if pd.notna(perfil['Ultimo Detalle de Experiencia']) else ""

        # Dividir la búsqueda por palabras clave
        palabras_clave = cargo.lower().strip().split() if cargo else []
        print(f"Palabras clave de búsqueda: {palabras_clave}")

        # Buscar el número de años de experiencia si está especificado en el texto de búsqueda
        anos_experiencia = None
        match = re.search(r'(\d+) años de experiencia', cargo)
        if match:
            anos_experiencia = match.group(1)  # Convertir a cadena para comparación
            print(f"Años de experiencia especificados: {anos_experiencia}")

        # Filtrar por cargo y comuna exacta
        if cargo is not None:
            perfiles_filtrados = [p for p in perfiles if any(palabra in p['Ultimo Cargo'] for palabra in palabras_clave)]
            print(f"Perfiles después de filtrar por cargo: {len(perfiles_filtrados)}")

            # Filtrar por comuna exacta
            if comuna is not None:
                perfiles_filtrados_comuna = [p for p in perfiles_filtrados if comuna.lower().strip() == p['Comuna']]
                print(f"Perfiles después de filtrar por comuna exacta ('{comuna}'): {len(perfiles_filtrados_comuna)}")
            else:
                perfiles_filtrados_comuna = perfiles_filtrados
        else:
            perfiles_filtrados_comuna = perfiles

        # Si no se encuentran perfiles exactos en la comuna, consultamos a la IA para sugerir comunas cercanas
        if len(perfiles_filtrados_comuna) == 0 and comuna is not None:
            # Crear un prompt dinámico para consultar a la IA sobre comunas cercanas
            prompt = f"Por favor, sugiere comunas que estén geográficamente cerca de '{comuna}' y que sean factibles para un desplazamiento razonable."

            # Llamar al modelo de OpenAI para obtener una lista de comunas cercanas
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "Eres un asistente experto en geografía y ayudando en reclutamientode recursos humanos."},
                          {"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5
            )

            # Procesar la respuesta de la IA para obtener las comunas sugeridas
            comunas_sugeridas = [comuna.strip() for comuna in response.choices[0].message['content'].lower().split(",")]
            print(f"Comunas sugeridas por la IA: {comunas_sugeridas}")

            # Buscar perfiles en las comunas sugeridas
            perfiles_filtrados_comuna = [p for p in perfiles_filtrados if any(sugerida in p['Comuna'] for sugerida in comunas_sugeridas)]
            print(f"Perfiles después de filtrar por comunas sugeridas: {len(perfiles_filtrados_comuna)}")

        # Filtrar por detalle de experiencia si se especifica
        if detalle_experiencia is not None:
            detalle_experiencia = detalle_experiencia.lower().strip()
            perfiles_filtrados_comuna = [p for p in perfiles_filtrados_comuna if detalle_experiencia in p['Ultimo Detalle de Experiencia']]
            print(f"Perfiles después de filtrar por detalle de experiencia: {len(perfiles_filtrados_comuna)}")

        # Si se especificaron años de experiencia, filtrar más por años de experiencia
        if anos_experiencia is not None:
            perfiles_filtrados_comuna = [p for p in perfiles_filtrados_comuna if anos_experiencia in p['Ultimo Detalle de Experiencia']]
            print(f"Perfiles después de filtrar por años de experiencia: {len(perfiles_filtrados_comuna)}")

        # Priorizar perfiles con discapacidad
        perfiles_filtrados_comuna.sort(key=lambda x: x['Discapacidad'] != 'Sí', reverse=True)
        print(f"Perfiles después de priorizar discapacidad: {len(perfiles_filtrados_comuna)}")

        # Si no se encuentran perfiles ni siquiera parcialmente, devolver una recomendación general
        if len(perfiles_filtrados_comuna) == 0:
            return {"recomendacion": "No se encontraron perfiles exactos, pero aquí tienes una recomendación general: considera ajustar los criterios de búsqueda."}

        # Limitar el número de perfiles enviados a OpenAI (ej. 10 perfiles)
        perfiles_finales = perfiles_filtrados_comuna[:10]

        # Crear el prompt en formato de mensajes para el modelo de chat
        messages = [
            {"role": "user", "content": f"Eres experto reclutando perfiles para minería y entiendes la flexibilidad en los criterios ingresados para privilegiar siempre una recomendación de perfil de manera clara y cercana, con un vocabulario simple y que no exceda los 1000 caracteres. Quiero la respuesta en un párrafo lineal y coherente sin redundancias y muy amigable. Ayúdame buscando perfiles adecuados para el cargo '{cargo}' en la comuna '{comuna}'. Lo más importante es el cargo del postulante, si bien la ubicación es un factor importante, por lo que se priorizan perfiles cercanos a esta comuna, siempre debe tener un peso mayor el cargo solicitado. Si no encuentras un perfil exacto, sugiere el más apto o el que podría servir, pero solo uno, en el cargo según su experiencia y justifica la ubicación y la decisión sobre ese candidato. Ten alta consideración con los perfiles con discapacidad, menciónalo si cumple. Aquí tienes los perfiles:"}
        ]

        for perfil in perfiles_finales:
            perfil_info = (
                f"Nombre: {perfil['Nombre Completo']}\n"
                f"Cargo: {perfil['Ultimo Cargo']}\n"
                f"Comuna: {perfil['Comuna']}\n"
                f"Estudio: {perfil['Ultimo Estudio']}\n"
                f"Detalles de experiencia: {perfil['Ultimo Detalle de Experiencia']}\n"
                f"Discapacidad: {perfil['Discapacidad']}\n"
            )
            messages.append({"role": "user", "content": perfil_info})

        # Llamar al endpoint de chat para el modelo gpt-3.5-turbo
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )

        # Retornar la recomendación generada por OpenAI
        return {"recomendacion": response.choices[0].message['content'].strip()}
    except Exception as e:
        print(f"Error al generar la recomendación: {e}")
        return {"error": f"Error interno al generar la recomendación: {e}"}
