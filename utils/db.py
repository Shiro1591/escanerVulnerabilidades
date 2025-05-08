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
        print("\nHistorial de escaneos:\n")
        for fila in filas:
            print(f"ID: {fila[0]}")
            print(f"URL: {fila[1]}")
            print(f"Fecha: {fila[2]}")
            print(f"Nivel de riesgo: {fila[3]}")
            print(f"Vulnerabilidades: {fila[4]}")
            print("-" * 40)

    conexion.close()

# Método que guarda los resultados del escaneo de cabeceras en la tabla resultados_escaneos
def guardar_resultado_escaneo(resultado):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    url = resultado.get("URL", "desconocido")
    estado = resultado.get("Código de Estado", None)
    vulnerabilidades = ", ".join(resultado.get("Cabeceras Ausentes", []))
    nivel = "Alto" if vulnerabilidades else "Bajo"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Verificar si ya existe esa URL
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



# Método que guarda un campo de formulario detectado
def guardar_formulario(url, metodo, accion, campo_nombre, campo_tipo, potencial):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    # Verificar si ese campo ya fue guardado para esa URL + acción + nombre de campo
    cursor.execute("""
        SELECT 1 FROM formularios_detectados
        WHERE url = ? AND accion = ? AND campo_nombre = ?
    """, (url, accion, campo_nombre))

    if cursor.fetchone():
        print(f"La URL '{url}' ya fue escaneada previamente. No se almacenará")
        conexion.close()
        return

    cursor.execute("""
        INSERT INTO formularios_detectados (url, metodo, accion, campo_nombre, campo_tipo, potencialmente_vulnerable)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (url, metodo, accion, campo_nombre, campo_tipo, int(potencial)))

    conexion.commit()
    conexion.close()


# Método que muestra todos los formularios detectados almacenados
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
            print("-" * 40)

    conexion.close()
