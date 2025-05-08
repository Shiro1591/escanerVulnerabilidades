# Importaciones
import requests
from bs4 import BeautifulSoup
from utils.db import guardar_formulario

# Cabeceras de seguridad que debería tener una página web
CABECERAS_SEGURIDAD = [
    "X-Frame-Options",
    "X-XSS-Protection",
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "Referrer-Policy"
]

# Función que escanea una URL y devuelve las cabeceras ausentes
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
            "Cabeceras Ausentes": ausentes
        }

    except requests.RequestException as e:
        return {
            "URL": url,
            "Error": str(e)
        }

# Función que detecta formularios en una página web
def escanear_formularios(url):
    try:
        respuesta = requests.get(url, timeout=5)
        soup = BeautifulSoup(respuesta.text, "lxml")
        formularios = soup.find_all("form")

        if not formularios:
            from utils.db import guardar_formulario
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


        print(f"\nSe encontraron {len(formularios)} formulario(s) en {url}:\n")

        for i, formulario in enumerate(formularios, start=1):
            metodo = formulario.get("method", "GET").upper()
            accion = formulario.get("action", url)

            print(f"Formulario {i}:")
            print(f"  Método: {metodo}")
            print(f"  Acción: {accion}")

            inputs = formulario.find_all(["input", "textarea"])
            for input_tag in inputs:
                tipo = input_tag.get("type", "text")
                nombre = input_tag.get("name", "")
                potencial = tipo in ["text", "search", "email", "password"]

                print(f"    Campo: {nombre} (tipo: {tipo}) {'Potencialmente vulnerable' if potencial else ''}")

                # Guardar en base de datos
                guardar_formulario(
                    url=url,
                    metodo=metodo,
                    accion=accion,
                    campo_nombre=nombre,
                    campo_tipo=tipo,
                    potencial=potencial
                )

            print("-" * 40)

    except requests.RequestException as e:
        print(f"Error al acceder a la URL: {e}")