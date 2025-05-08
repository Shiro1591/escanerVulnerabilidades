from utils.scanner import escanear_cabeceras, escanear_formularios
from utils.db import guardar_resultado_escaneo, mostrar_resultados, mostrar_formularios_detectados

if __name__ == "__main__":
    url = "http://testphp.vulnweb.com"
    resultado = escanear_cabeceras(url)
    escanear_formularios(url)
    guardar_resultado_escaneo(resultado)

