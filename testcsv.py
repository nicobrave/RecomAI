import pandas as pd

# Ruta del archivo CSV
csv_path = 'C:/Users/Usuario/Desktop/RecomAI/fuego/Base de datos histórica de cicatrices de incendios chilenos - 1. Resumen.csv'

# Cargar el archivo CSV utilizando punto y coma como delimitador
df = pd.read_csv(csv_path, sep=';', quotechar='"', encoding='utf-8')

# Mostrar las primeras filas para verificar
print(df.head())
