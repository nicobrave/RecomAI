import pandas as pd
import openai
import folium
import os
import datetime
import requests

# Cargar el CSV de incendios históricos
csv_path = "fuego/Base de datos histórica de cicatrices de incendios chilenos - 1. Resumen.csv"

# Leer el archivo CSV
df = pd.read_csv(csv_path, sep=';', quotechar='"', encoding='utf-8')

# Asegúrate de que las columnas tienen los nombres correctos
df.columns = df.columns.str.replace('Latitude', 'Latitude').str.replace('Longitude', 'Longitude')

# Configurar la API key de OpenAI desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

def obtener_datos_climaticos(lat, lon):
    """
    Obtener los datos climáticos en tiempo real utilizando la API de OpenWeather.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")  # Obtén la API Key de OpenWeather
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # Retorna los datos en formato JSON
        else:
            print(f"Error al obtener datos climáticos: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error al hacer la solicitud a OpenWeather: {e}")
        return None

def generar_mapa_incendios(df, lat, lon):
    """
    Genera un mapa con los incendios cercanos en un radio específico y muestra los puntos de interés.
    """
    mapa = folium.Map(location=[lat, lon], zoom_start=8)
    
    # Añadir marcador de la ubicación del usuario
    folium.Marker([lat, lon], popup="Tu ubicación", icon=folium.Icon(color="blue")).add_to(mapa)

    # Filtrar incendios cercanos
    df_filtrado = df[(df['Latitude'] <= lat + 0.5) & (df['Latitude'] >= lat - 0.5) &
                     (df['Longitude'] <= lon + 0.5) & (df['Longitude'] >= lon - 0.5)]

    # Añadir incendios históricos al mapa
    for _, row in df_filtrado.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']],
                      popup=f"Incendio: {row['FireName_CONAF']}, Área: {row['Area_CONAF [ha]']} ha",
                      icon=folium.Icon(color="red")).add_to(mapa)

    # Guardar el mapa en una ruta accesible desde el navegador
    output_path = os.path.join('static', 'mapas', f'mapa_incendios_{lat}_{lon}.html')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    mapa.save(output_path)
    
    # Retornar la ruta relativa para que el navegador la pueda acceder
    return f'/static/mapas/mapa_incendios_{lat}_{lon}.html'

def obtener_recomendacion_fuego(lat, lon):
    try:
        # Obtener datos climáticos
        datos_climaticos = obtener_datos_climaticos(lat, lon)
        if datos_climaticos:
            temperatura = datos_climaticos['main']['temp']
            humedad = datos_climaticos['main']['humidity']
            velocidad_viento = datos_climaticos['wind']['speed']

            # Usar los datos climáticos en el prompt de OpenAI
            prompt = (
                f"Estoy en las coordenadas latitud {lat} y longitud {lon}, "
                f"con una temperatura de {temperatura}°C, humedad de {humedad}% y viento a {velocidad_viento} m/s. "
                f"Deseo obtener recomendaciones para la prevención de incendios forestales para la temporada actual. Incorpora los datos ambientales obtenidos en vivo y justifica la recomendaciones basadas en estos factores climáticos para reducir el riesgo de incendios. Es importante que reflejes en la respuesta la locación, hora y factores ambientales para otorgar veracidad. No excedas los 1000 caracteres en la respuesta."
            )
            
            # Generar recomendación con OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en prevención de incendios forestales."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.2
            )
            recomendacion_openai = response.choices[0]['message']['content'].strip()

            # Generar el mapa de incendios cercanos
            mapa_path = generar_mapa_incendios(df, lat, lon)

            return recomendacion_openai, mapa_path
        else:
            return "No se pudieron obtener los datos climáticos.", None
    
    except Exception as e:
        print(f"Error en obtener_recomendacion_fuego: {e}")
        return None, None
