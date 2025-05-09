# Importaciones
import requests  # Para realizar peticiones HTTP
from bs4 import BeautifulSoup  # Para analizar el HTML
from utils.db import guardar_formulario  # Para guardar formularios detectados

# Lista de cabeceras HTTP de seguridad que deberían estar presentes
CABECERAS_SEGURIDAD = [
    "X-Frame-Options",
    "X-XSS-Protection",
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "Referrer-Policy"
]

# Función que escanea una URL y devuelve las cabeceras ausentes y presentes
def escanear_cabeceras(url):
    try:
        respuesta = requests.get(url, timeout=5)
        cabeceras = respuesta.headers
        ausentes = []

        for cabecera in CABECERAS_SEGURIDAD:
            if cabecera not in cabeceras:
                ausentes.append(cabecera)

        return {
            "URL": url,
            "Código de Estado": respuesta.status_code,
            "Cabeceras Presentes": [c for c in CABECERAS_SEGURIDAD if c in cabeceras],
            "Cabeceras Ausentes": ausentes,
            
        }

    except requests.RequestException as e:
        return {
            "URL": url,
            "Error": str(e)
        }
    
  

# Función que escanea los formularios de una página web y guarda los campos encontrados
def escanear_formularios(url):
    try:
        respuesta = requests.get(url, timeout=5)
        soup = BeautifulSoup(respuesta.text, "lxml")
        formularios = soup.find_all("form")

        if not formularios:
            # Si no se encuentra ningún formulario, se registra igualmente
            guardar_formulario(
                url=url,
                metodo="N/A",
                accion="Ningún formulario encontrado",
                campo_nombre="-",
                campo_tipo="-",
                potencial=False
            )
            print("No se encontraron formularios en la página.")
            return

        print(f"Se encontraron {len(formularios)} formulario(s) en {url}:\n")

        for i, formulario in enumerate(formularios, start=1):
            metodo = formulario.get("method", "GET").upper()
            accion = formulario.get("action", url)

            print(f"Formulario {i}:")
            print(f"Método: {metodo}")
            print(f"Acción: {accion}")

            inputs = formulario.find_all(["input", "textarea"])
            for input_tag in inputs:
                tipo = input_tag.get("type", "text")
                nombre = input_tag.get("name", "")
                potencial = tipo in ["text", "search", "email", "password"]

                print(f"Campo: {nombre} (tipo: {tipo}) {'Potencialmente vulnerable' if potencial else ''}")

                guardar_formulario(
                    url=url,
                    metodo=metodo,
                    accion=accion,
                    campo_nombre=nombre,
                    campo_tipo=tipo,
                    potencial=potencial
                )

    except requests.RequestException as e:
        print(f"Error al acceder a la URL: {e}")
