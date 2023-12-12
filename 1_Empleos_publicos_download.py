# Descargar URL
# Obtener fecha y hora para dar nombre a los archivos
from datetime import datetime
# Obtener la hora actual del sistema
fecha_actual = datetime.now()
# Convertir la hora a un formato de string
fecha_actual = fecha_actual.strftime("%Y%m%d")
#  Nombrar html descargado
nombre_html_descargado = './output/empleos_publicos_' + fecha_actual + '.html'
# Obtener URL

respuesta = input("¿Quieres utilizar el criterio de busqueda profesionales o  introducir una url alternativa? \n (1) Buscar empleos profesionales. \n (2) Introducir url.")

if respuesta == '1':
    url = 'https://www.empleospublicos.cl/pub/convocatorias/convocatorias.aspx?cargos=Profesionales&i=2'
    print("Se cargó la url de busqueda de trabajos profesionales.")
else:
    url = input("Introducir código html:")
    print("Se cargó la url alternativa.")

# Descargar archivo html

import requests

# Realizar la solicitud HTTP GET
response = requests.get(url)

# Verificar que la solicitud fue exitosa
if response.status_code == 200:
    # Guardar el contenido en un archivo
    with open(nombre_html_descargado, 'w', encoding='utf-8') as file:
        file.write(response.text)
else:
    print(f'Error al descargar el archivo: {response.status_code}')

#  Obtener datos desde el html
# Librerias
from bs4 import BeautifulSoup
import pandas as pd
# Abrir archivo html
with open(nombre_html_descargado, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")
# Identificar los elementos que tienen la etiqueta class 'caja row primerEmpleo'
divs = soup.find_all("div", {"class": "caja row primerEmpleo"})
# Extraer la data
data = []
for div in divs:
    # Extract job title
    job_title = div.find("div", {"id": "bx_titulos"})
    job_title = job_title.get_text(strip=True) if job_title else None

    # Extract organization
    organization = div.find("div", {"id": "bx_resumen"}).find("strong")
    organization = organization.get_text(strip=True) if organization else None

    # Extract job description
    description = div.find("div", {"id": "bx_resumen"})
    if description:
        # Remove strong tag to isolate the description
        if description.strong:
            description.strong.decompose()
        description = description.get_text(strip=True, separator="\n")

    # Extract application deadline
    deadline = div.find("div", {"id": "bx_resumen"}).find("em")
    deadline = deadline.get_text(strip=True) if deadline else None

    # Extract link to job posting
    link = div.find("a", {"class": "btnverficha"})
    link = link['href'] if link else None

    # Append extracted data to the list
    data.append({
        "Titulo": job_title,
        "Organizacion": organization,
        "Descripcion": description,
        "Deadline": deadline,
        "Link": link
    })

# Transformar en un pd.df
df = pd.DataFrame(data)
# Crea el link completo e indica la fecha límite
df['Link_completo'] = 'https://www.empleospublicos.cl/pub/convocatorias/' + df['Link']
df['fecha_limite'] = df['Deadline'].str.slice(-10)
# Exporta la convocatoria
nombre_df_completo = "./output/df_completo_" + fecha_actual + ".xlsx"
df.to_excel(nombre_df_completo, index=False, engine='openpyxl')
# Definir el nombre del archivo de texto
nombre_archivo = "./input/exclusion_organizacion.txt"

# Inicializar una lista vacía para almacenar las palabras
exclusion_organizacion = []

# Abrir el archivo y leer cada línea
with open(nombre_archivo, 'r') as archivo:
    for linea in archivo:
        # Añadir la palabra a la lista, eliminando espacios en blanco y saltos de línea
        exclusion_organizacion.append(linea.strip())

# Ahora 'palabras' es una lista que contiene todas las palabras del archivo
print(exclusion_organizacion)
# Crear un vector con todos los textos para excluir del título de la oferta laboral. 

# Definir el nombre del archivo de texto
nombre_archivo = "./input/exclusion_profesiones.txt"

# Inicializar una lista vacía para almacenar las palabras
exclusion_profesiones = []

# Abrir el archivo y leer cada línea
with open(nombre_archivo, 'r') as archivo:
    for linea in archivo:
        # Añadir la palabra a la lista, eliminando espacios en blanco y saltos de línea
        exclusion_profesiones.append(linea.strip())
# Excluir del df las organizaciones que no son de interés

# Crear una máscara booleana con 'True' para las filas donde ninguna de las palabras está presente
mascara = ~df['Organizacion'].str.contains('|'.join(exclusion_organizacion), case=False, na=False)

# Filtrar el DataFrame usando la máscara
df = df[mascara]

# Excluir del df las organizaciones que no son de interés

# Crear una máscara booleana con 'True' para las filas donde ninguna de las palabras está presente
mascara = ~df['Titulo'].str.contains('|'.join(exclusion_profesiones), case=False, na=False)

# Filtrar el DataFrame usando la máscara
df = df[mascara]
# Selecciona las columnas relevantes y exporta el df filtrado
nombre_df_filtrado = "./output/df_filtrado_" + fecha_actual + ".xlsx"
df[["Titulo", "Organizacion", "Descripcion", "Link_completo", "fecha_limite"]].to_excel(nombre_df_filtrado, index=False, engine='openpyxl')
