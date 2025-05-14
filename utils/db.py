# Importaciones
import sqlite3, os, json, csv
from datetime import datetime

# Método que obtiene la lista de cabeceras de seguridad desde la base de datos
def obtener_cabeceras_seguridad():
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT nombre_cabecera FROM cabeceras_seguridad")
    cabeceras = [fila[0] for fila in cursor.fetchall()]

    conexion.close()
    return cabeceras

# Método que obtiene los patrones de errores SQL desde la base de datos
def obtener_errores_sql():
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT patron FROM errores_sql")
    errores = [fila[0].lower() for fila in cursor.fetchall()]
    conexion.close()
    return errores

# Método que guarda los resultados de un escaneo de cabeceras en la base de datos
def guardar_resultado_escaneo(resultado):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    url = resultado.get("URL", "desconocido")
    estado = resultado.get("Código de Estado", None)
    cabeceras_ausentes = resultado.get("Cabeceras Ausentes", [])
    vulnerabilidades = ", ".join(cabeceras_ausentes)
    cantidad = len(cabeceras_ausentes)

    if cantidad >= 3:
        nivel = "Alto"
    elif cantidad >= 1:
        nivel = "Medio"
    else:
        nivel = "Bajo"

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Comprueba si ya existe un escaneo con esa URL y si ya fue escaneada no la almacena de nuevo
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

# Método que guarda los resultados de un escaneo de formularios en la base de datos, evitando duplicados
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

# Método que guarda un ataque detectado en la base de datos
def guardar_ataque_detectado(url, metodo, accion, campo_nombre, tipo_payload, payload, evidencia):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO ataques_detectados (url, metodo, accion, campo_nombre, tipo_payload, payload, evidencia, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (url, metodo, accion, campo_nombre, tipo_payload, payload, evidencia, fecha))

    conexion.commit()
    conexion.close()

# Método que define la ruta para guardar los documentos de vulnerabilidades
def ruta_documentos_vulnerabilidades(nombre_archivo):
    carpeta = os.path.join(os.path.expanduser("~"), "Documents", "Datos escaner vulnerabilidades")
    os.makedirs(carpeta, exist_ok=True)
    return os.path.join(carpeta, nombre_archivo)

# Método que exporta los escaneos de cabeceras y formularios detectados a un archivo JSON
def exportar_a_json(nombre_archivo="export_resultados.json"):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    # Cabeceras
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

# Método que exporta los escaneos de cabeceras y formularios detectados a un archivo CSV
def exportar_a_csv(nombre_archivo="export_resultados.csv"):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    nombre_archivo = ruta_documentos_vulnerabilidades(nombre_archivo)
    with open(nombre_archivo, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)

        # Cabeceras
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

# Método que exporta ataques detectados a JSON
def exportar_ataques_a_json(nombre_archivo="export_ataques.json"):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT url, metodo, accion, campo_nombre, tipo_payload, payload, evidencia, fecha FROM ataques_detectados")
    ataques = cursor.fetchall()
    conexion.close()

    datos = [
        {
            "url": a[0],
            "metodo": a[1],
            "accion": a[2],
            "campo": a[3],
            "tipo": a[4],
            "payload": a[5],
            "evidencia": a[6],
            "fecha": a[7]
        }
        for a in ataques
    ]

    ruta = ruta_documentos_vulnerabilidades(nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

    return ruta

# Método que exporta ataques detectados a CSV
def exportar_ataques_a_csv(nombre_archivo="export_ataques.csv"):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT url, metodo, accion, campo_nombre, tipo_payload, payload, evidencia, fecha FROM ataques_detectados")
    ataques = cursor.fetchall()
    conexion.close()

    ruta = ruta_documentos_vulnerabilidades(nombre_archivo)
    with open(ruta, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Método", "Acción", "Campo", "Tipo", "Payload", "Evidencia", "Fecha"])
        for fila in ataques:
            writer.writerow(fila)

    return ruta






