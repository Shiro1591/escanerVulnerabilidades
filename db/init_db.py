# Importaciones 
import sqlite3
import os

# Método que inicializa la base de datos y crea las tablas necesarias
def init_db():

    # Verifica si la carpeta "db" existe, si no, la crea
    if not os.path.exists("db"):
        os.makedirs("db")

    conn = sqlite3.connect("db/scanner.db")
    cursor = conn.cursor()

    # Ejecuta el script para crear las tablas
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS resultados_escaneos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            fecha_escaneo TEXT,
            nivel_riesgo TEXT,
            vulnerabilidades TEXT
        );

        CREATE TABLE IF NOT EXISTS payloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            cadena TEXT NOT NULL,
            descripcion TEXT
        );

        CREATE TABLE IF NOT EXISTS cabeceras_seguridad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cabecera TEXT NOT NULL,
            valor_recomendado TEXT,
            descripcion TEXT
        );
                         
        CREATE TABLE IF NOT EXISTS formularios_detectados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            metodo TEXT,
            accion TEXT,
            campo_nombre TEXT,
            campo_tipo TEXT,
            potencialmente_vulnerable INTEGER
        );
    """)

    # Hace commit para guardar los cambios y cierra la conexión
    conn.commit()
    conn.close()

    # Ejecuta la función que crea la BD solo si se esta ejecutando directamente
if __name__ == "__main__":
    init_db()
