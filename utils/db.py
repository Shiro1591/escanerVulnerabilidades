# Importaciones
import sqlite3
from datetime import datetime

# Método que muestra todos los resultados de la tabla resultados_escaneos
def mostrar_resultados():
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM resultados_escaneos")
    filas = cursor.fetchall()

    if not filas:
        print("No hay resultados guardados.")
    else:
        print("Historial de escaneos:")
        for fila in filas:
            print(f"ID: {fila[0]}")
            print(f"URL: {fila[1]}")
            print(f"Fecha: {fila[2]}")
            print(f"Nivel de riesgo: {fila[3]}")
            print(f"Vulnerabilidades: {fila[4]}")
            print("-" * 40)

    conexion.close()


# Método que guarda los resultados del escaneo en la tabla resultados_escaneos
def guardar_resultado_escaneo(resultado):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    url = resultado.get("URL", "desconocido")
    estado = resultado.get("Código de Estado", None)
    vulnerabilidades = ", ".join(resultado.get("Cabeceras Ausentes", []))
    nivel = "Alto" if vulnerabilidades else "Bajo"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO resultados_escaneos (url, fecha_escaneo, nivel_riesgo, vulnerabilidades)
        VALUES (?, ?, ?, ?)
    """, (url, fecha, nivel, vulnerabilidades))
    
    conexion.commit()
    conexion.close()
    print(f"Resultados del escaneo guardados para {url}.")
