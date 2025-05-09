# Importaciones
import sqlite3, os, json, csv
from datetime import datetime

# Muestra por consola los resultados de escaneos de cabeceras
def mostrar_resultados():
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM resultados_escaneos")
    filas = cursor.fetchall()

    if not filas:
        print("No hay resultados guardados.")
    else:
        print("\nHistorial de escaneos:\n")
        for fila in filas:
            print(f"ID: {fila[0]}") 
            print(f"URL: {fila[1]}")
            print(f"Fecha: {fila[2]}")
            print(f"Nivel de riesgo: {fila[3]}")
            print(f"Vulnerabilidades: {fila[4]}")
            print("-" * 40)

    conexion.close()

# Guarda un escaneo de cabeceras en la base de datos si la URL aún no fue registrada
def guardar_resultado_escaneo(resultado):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    url = resultado.get("URL", "desconocido")
    estado = resultado.get("Código de Estado", None)
    vulnerabilidades = ", ".join(resultado.get("Cabeceras Ausentes", []))
    cantidad = len(vulnerabilidades)
    if cantidad >= 3:
        nivel = "Alto"
    elif cantidad >= 1:
        nivel = "Medio"
    else:
        nivel = "Bajo"

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # No guardar si ya existe un escaneo para esa URL
    cursor.execute("SELECT 1 FROM resultados_escaneos WHERE url = ?", (url,))
    if cursor.fetchone():
        conexion.close()
        return False

    cursor.execute("""
        INSERT INTO resultados_escaneos (url, fecha_escaneo, nivel_riesgo, vulnerabilidades)
        VALUES (?, ?, ?, ?)
    """, (url, fecha, nivel, vulnerabilidades))

    conexion.commit()
    conexion.close()
    return True

# Guarda un campo detectado en un formulario si no está duplicado
def guardar_formulario(url, metodo, accion, campo_nombre, campo_tipo, potencial):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT 1 FROM formularios_detectados
        WHERE url = ? AND accion = ? AND campo_nombre = ?
    """, (url, accion, campo_nombre))

    if cursor.fetchone():
        conexion.close()
        return

    cursor.execute("""
        INSERT INTO formularios_detectados (url, metodo, accion, campo_nombre, campo_tipo, potencialmente_vulnerable)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (url, metodo, accion, campo_nombre, campo_tipo, int(potencial)))

    conexion.commit()
    conexion.close()

# Muestra por consola todos los formularios detectados almacenados
def mostrar_formularios_detectados():
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM formularios_detectados")
    filas = cursor.fetchall()

    if not filas:
        print("No hay formularios detectados en la base de datos.")
    else:
        print("\nFormularios detectados en escaneos anteriores:\n")
        for fila in filas:
            print(f"ID: {fila[0]}")
            print(f"URL: {fila[1]}")
            print(f"Método: {fila[2]}")
            print(f"Acción: {fila[3]}")
            print(f"Campo: {fila[4]} (tipo: {fila[5]})")
            print(f"¿Potencialmente vulnerable?: {'Sí' if fila[6] else 'No'}")

    conexion.close()

# Define la ruta para guardar los documentos de vulnerabilidades
def ruta_documentos_vulnerabilidades(nombre_archivo):
    carpeta = os.path.join(os.path.expanduser("~"), "Documents", "Datos vulnerabilidades")
    os.makedirs(carpeta, exist_ok=True)
    return os.path.join(carpeta, nombre_archivo)

# Exporta los resultados de escaneos y formularios detectados a un archivo JSON
def exportar_a_json(nombre_archivo="export_resultados.json"):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    # Escaneos
    cursor.execute("SELECT url, fecha_escaneo, nivel_riesgo, vulnerabilidades FROM resultados_escaneos")
    escaneos = cursor.fetchall()
    escaneos_json = [
        {
            "url": fila[0],
            "fecha_escaneo": fila[1],
            "nivel_riesgo": fila[2],
            "cabeceras_ausentes": fila[3].split(", ") if fila[3] else []
        }
        for fila in escaneos
    ]

    # Formularios
    cursor.execute("SELECT url, metodo, accion, campo_nombre, campo_tipo, potencialmente_vulnerable FROM formularios_detectados")
    formularios = cursor.fetchall()
    formularios_json = [
        {
            "url": fila[0],
            "metodo": fila[1],
            "accion": fila[2],
            "campo_nombre": fila[3],
            "campo_tipo": fila[4],
            "vulnerable": bool(fila[5])
        }
        for fila in formularios
    ]

    conexion.close()

    datos = {
        "escaneos": escaneos_json,
        "formularios": formularios_json
    }

    nombre_archivo = ruta_documentos_vulnerabilidades(nombre_archivo)
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

    return nombre_archivo

# Exporta los resultados de escaneos y formularios detectados a un archivo CSV
def exportar_a_csv(nombre_archivo="export_resultados.csv"):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    nombre_archivo = ruta_documentos_vulnerabilidades(nombre_archivo)
    with open(nombre_archivo, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)

        # Escaneos
        writer.writerow(["[ESCANEOS DE CABECERAS]"])
        writer.writerow(["URL", "Fecha", "Nivel de Riesgo", "Cabeceras Ausentes"])
        cursor.execute("SELECT url, fecha_escaneo, nivel_riesgo, vulnerabilidades FROM resultados_escaneos")
        for fila in cursor.fetchall():
            writer.writerow(fila)

        writer.writerow([])

        # Formularios
        writer.writerow(["[FORMULARIOS DETECTADOS]"])
        writer.writerow(["URL", "Método", "Acción", "Campo", "Tipo", "Vulnerable"])
        cursor.execute("SELECT url, metodo, accion, campo_nombre, campo_tipo, potencialmente_vulnerable FROM formularios_detectados")
        for fila in cursor.fetchall():
            writer.writerow(fila)

    conexion.close()
    return nombre_archivo


