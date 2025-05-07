from utils.scanner import escanear_cabeceras
from utils.db import guardar_resultado_escaneo, mostrar_resultados

if __name__ == "__main__":
    url = " http://http.badssl.com/"
    resultado = escanear_cabeceras(url)
    print("Resultado del escaneo:")
    print(resultado)

    guardar_resultado_escaneo(resultado)

    # Mostrar historial completo
    mostrar_resultados()
