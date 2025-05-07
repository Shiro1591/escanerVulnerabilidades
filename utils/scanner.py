# Importaciones
import requests

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
