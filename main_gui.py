# Importaciones
import sqlite3, os, platform, subprocess
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from utils.scanner import escanear_cabeceras as escanear_cabeceras_funcion
from utils.scanner import escanear_formularios as escanear_formularios_funcion
from utils.db import guardar_resultado_escaneo, exportar_a_json, exportar_a_csv


# Funciones de cada botón
def escanear_cabeceras():
    # Ventana secundaria con diseño más limpio
    ventana_secundaria = ttk.Toplevel(title="Escaneo de Cabeceras")
    ventana_secundaria.geometry("700x540")
    ventana_secundaria.resizable(False, False)

    # Título de sección
    ttk.Label(
        ventana_secundaria,
        text="Escaneo de Cabeceras HTTP",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    # Contenedor de entrada y botón
    frame_url = ttk.Frame(ventana_secundaria)
    frame_url.pack(pady=10)

    ttk.Label(frame_url, text="Introduce una URL:", font=("Segoe UI", 11)).pack(anchor="w", padx=10)
    entrada_url = ttk.Entry(frame_url, width=70)
    entrada_url.pack(padx=10, pady=(0, 10))

    def ejecutar_escaneo():
        url = entrada_url.get()
        if not url:
            messagebox.showwarning("Campo vacío", "Por favor, introduce una URL.")
            return

        resultado = escanear_cabeceras_funcion(url)
        guardar_resultado_escaneo(resultado)
        area_resultados.delete("1.0", "end")

        if "Error" in resultado:
            area_resultados.insert("end", f"Error al escanear la URL:\n{resultado['Error']}")
        else:
            area_resultados.insert("end", f"URL: {resultado['URL']}\n")
            area_resultados.insert("end", f"Código de Estado: {resultado['Código de Estado']}\n\n")
            area_resultados.insert("end", "Cabeceras Presentes:\n")
            for cabecera in resultado["Cabeceras Presentes"]:
                area_resultados.insert("end", f"  - {cabecera}\n")
            area_resultados.insert("end", "\nCabeceras Ausentes:\n")
            for cabecera in resultado["Cabeceras Ausentes"]:
                area_resultados.insert("end", f"  - {cabecera}\n")

    # Botón para escanear
    ttk.Button(frame_url, text="Escanear", width=20, command=ejecutar_escaneo, bootstyle="primary").pack(pady=5)

    # Área de resultados
    area_resultados = ttk.Text(ventana_secundaria, height=20)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

def escanear_formularios():
    # Ventana secundaria con diseño profesional
    ventana_secundaria = ttk.Toplevel(title="Escaneo de Formularios")
    ventana_secundaria.geometry("700x540")
    ventana_secundaria.resizable(False, False)

    # Título de la ventana
    ttk.Label(
        ventana_secundaria,
        text="Escaneo de Formularios HTML",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    # Contenedor para el campo de entrada y botón
    frame_url = ttk.Frame(ventana_secundaria)
    frame_url.pack(pady=10)

    ttk.Label(frame_url, text="Introduce una URL:", font=("Segoe UI", 11)).pack(anchor="w", padx=10)
    entrada_url = ttk.Entry(frame_url, width=70)
    entrada_url.pack(padx=10, pady=(0, 10))

    def ejecutar_escaneo():
        url = entrada_url.get()
        if not url:
            messagebox.showwarning("Campo vacío", "Por favor, introduce una URL.")
            return

        area_resultados.delete("1.0", "end")

        try:
            import io
            import sys
            buffer = io.StringIO()
            sys.stdout = buffer
            escanear_formularios_funcion(url)
            sys.stdout = sys.__stdout__
            resultado = buffer.getvalue()
            area_resultados.insert("end", resultado)
        except Exception as e:
            sys.stdout = sys.__stdout__
            area_resultados.insert("end", f"Error durante el escaneo: {e}")

    # Botón para lanzar el escaneo
    ttk.Button(frame_url, text="Escanear", width=20, command=ejecutar_escaneo, bootstyle="primary").pack(pady=5)

    # Área de resultados
    area_resultados = ttk.Text(ventana_secundaria, height=20)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

def escaneo_completo():
    # Ventana secundaria con diseño mejorado
    ventana_secundaria = ttk.Toplevel(title="Escaneo Completo")
    ventana_secundaria.geometry("750x600")
    ventana_secundaria.resizable(False, False)

    # Título superior
    ttk.Label(
        ventana_secundaria,
        text="Escaneo Completo (Cabeceras + Formularios)",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    # Contenedor para la entrada y el botón
    frame_url = ttk.Frame(ventana_secundaria)
    frame_url.pack(pady=10)

    ttk.Label(frame_url, text="Introduce una URL:", font=("Segoe UI", 11)).pack(anchor="w", padx=10)
    entrada_url = ttk.Entry(frame_url, width=70)
    entrada_url.pack(padx=10, pady=(0, 10))

    def ejecutar_escaneo_completo():
        url = entrada_url.get()
        if not url:
            messagebox.showwarning("Campo vacío", "Por favor, introduce una URL.")
            return

        area_resultados.delete("1.0", "end")

        try:
            import io
            import sys
            buffer = io.StringIO()
            sys.stdout = buffer

            # Escaneo de cabeceras
            cabeceras = escanear_cabeceras_funcion(url)
            guardar_resultado_escaneo(cabeceras)

            print("=== ESCANEO DE CABECERAS ===")
            if "Error" in cabeceras:
                print(f"Error: {cabeceras['Error']}")
            else:
                print(f"URL: {cabeceras['URL']}")
                print(f"Código de Estado: {cabeceras['Código de Estado']}")
                print("Cabeceras Presentes:")
                for c in cabeceras["Cabeceras Presentes"]:
                    print(f"  - {c}")
                print("\nCabeceras Ausentes:")
                for c in cabeceras["Cabeceras Ausentes"]:
                    print(f"  - {c}")

            print("\n=== ESCANEO DE FORMULARIOS ===")
            escanear_formularios_funcion(url)

            sys.stdout = sys.__stdout__
            resultado = buffer.getvalue()
            area_resultados.insert("end", resultado)

        except Exception as e:
            sys.stdout = sys.__stdout__
            area_resultados.insert("end", f"Error durante el escaneo completo: {e}")

    # Botón de acción
    ttk.Button(frame_url, text="Escanear Todo", width=20, command=ejecutar_escaneo_completo, bootstyle="primary").pack(pady=5)

    # Área de resultados
    area_resultados = ttk.Text(ventana_secundaria, height=25)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

def ver_resultados():
    ventana_secundaria = ttk.Toplevel(title="Historial de Escaneos por URL")
    ventana_secundaria.geometry("850x600")
    ventana_secundaria.resizable(False, False)

    # Título visual principal
    ttk.Label(
        ventana_secundaria,
        text="Historial de Escaneos",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    # Contenedor del área de resultados
    frame_contenido = ttk.Frame(ventana_secundaria)
    frame_contenido.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    area_resultados = ttk.Text(frame_contenido, height=30, font=("Segoe UI", 10))
    area_resultados.pack(fill="both", expand=True)

    # Acceso a base de datos
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT DISTINCT url FROM resultados_escaneos")
    urls_cabeceras = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT url FROM formularios_detectados")
    urls_formularios = [row[0] for row in cursor.fetchall()]

    urls_unicas = sorted(set(urls_cabeceras + urls_formularios))

    for url in urls_unicas:
        area_resultados.insert("end", f"\n=== URL: {url} ===\n")

        # Escaneo de cabeceras
        cursor.execute("""
            SELECT fecha_escaneo, nivel_riesgo, vulnerabilidades
            FROM resultados_escaneos WHERE url = ?
        """, (url,))
        fila = cursor.fetchone()
        if fila:
            area_resultados.insert("end", "\n[Escaneo de Cabeceras]\n")
            area_resultados.insert("end", f"Fecha: {fila[0]}\n")
            area_resultados.insert("end", f"Nivel de riesgo: {fila[1]}\n")
            area_resultados.insert("end", f"Cabeceras ausentes: {fila[2]}\n")

        # Formularios
        cursor.execute("""
            SELECT metodo, accion, campo_nombre, campo_tipo, potencialmente_vulnerable
            FROM formularios_detectados WHERE url = ?
        """, (url,))
        formularios = cursor.fetchall()

        if formularios:
            area_resultados.insert("end", "\n[Formularios Detectados]\n")
            agrupados = {}
            for f in formularios:
                clave = (f[0], f[1])
                if clave not in agrupados:
                    agrupados[clave] = []
                agrupados[clave].append(f)

            for i, ((metodo, accion), campos) in enumerate(agrupados.items(), start=1):
                area_resultados.insert("end", f"\n  Formulario {i}:\n")
                area_resultados.insert("end", f"    Método: {metodo}\n")
                area_resultados.insert("end", f"    Acción: {accion}\n")
                area_resultados.insert("end", f"    Campos:\n")
                for campo in campos:
                    nombre, tipo, vuln = campo[2], campo[3], campo[4]
                    marca = " [vulnerable]" if vuln else ""
                    area_resultados.insert("end", f"      - {nombre} (tipo: {tipo}){marca}\n")

    conexion.close()

def exportar_resultados():
    ventana_exportar = ttk.Toplevel(title="Exportar Resultados")
    ventana_exportar.geometry("500x250")
    ventana_exportar.resizable(False, False)

    ttk.Label(
        ventana_exportar,
        text="Exportar Resultados",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    frame = ttk.Frame(ventana_exportar)
    frame.pack(pady=10, padx=10, fill="x")

    # Campo de ruta
    ttk.Label(frame, text="Nombre del archivo (sin extensión):").pack(anchor="w")
    entrada_ruta = ttk.Entry(frame, width=50)
    entrada_ruta.pack(pady=5)

    # Formato de exportación
    ttk.Label(frame, text="Selecciona formato de exportación:").pack(anchor="w", pady=(10, 0))
    formato_var = ttk.StringVar(value="json")
    opciones = ttk.Frame(frame)
    opciones.pack(anchor="w", pady=5)
    ttk.Radiobutton(opciones, text="JSON", variable=formato_var, value="json").pack(side="left", padx=5)
    ttk.Radiobutton(opciones, text="CSV", variable=formato_var, value="csv").pack(side="left", padx=5)

    def ejecutar_exportacion():
        nombre = entrada_ruta.get().strip()
        if not nombre:
            messagebox.showwarning("Campo vacío", "Debes introducir un nombre de archivo.")
            return

        formato = formato_var.get()
        ruta = f"{nombre}.{formato}"

        if formato == "json":
            archivo = exportar_a_json(ruta)
        else:
            archivo = exportar_a_csv(ruta)

        abrir_carpeta_contenedora(archivo)
        messagebox.showinfo("Exportación completada", f"Archivo guardado como:\n{archivo}")

        ventana_exportar.destroy()

    ttk.Button(ventana_exportar, text="Exportar", width=20, command=ejecutar_exportacion, bootstyle="primary").pack(pady=10)

def abrir_carpeta_contenedora(ruta_archivo):
    ruta_absoluta = os.path.abspath(ruta_archivo)
    carpeta = os.path.dirname(ruta_absoluta)

    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.startfile(carpeta)
        elif sistema == "Darwin":  # macOS
            subprocess.Popen(["open", carpeta])
        else:  # Linux
            subprocess.Popen(["xdg-open", carpeta])
    except Exception as e:
        messagebox.showwarning("Error al abrir carpeta", f"No se pudo abrir la carpeta:\n{carpeta}\n\n{e}")


# Interfaz gráfica principal
# Ventana principal con tema moderno
ventana = ttk.Window(themename="flatly")
ventana.title("Escáner de Vulnerabilidades Web")
ventana.geometry("640x460")
ventana.resizable(False, False)

# Frame superior para el título
header = ttk.Frame(ventana)
header.pack(fill="x", pady=(20, 10))

ttk.Label(
    header,
    text="Escáner de Vulnerabilidades Web",
    font=("Segoe UI", 20, "bold"),
    anchor="center"
).pack()

# Frame central para los botones, centrado horizontalmente
frame_botones = ttk.Frame(ventana)
frame_botones.pack(pady=30)

# Lista de botones y funciones
botones = [
    ("Escanear Cabeceras", escanear_cabeceras),
    ("Escanear Formularios", escanear_formularios),
    ("Escaneo Completo", escaneo_completo),
    ("Ver Resultados", ver_resultados),
    ("Exportar Resultados", exportar_resultados),
]

# Añadir botones estilizados
for texto, accion in botones:
    ttk.Button(
        frame_botones,
        text=texto,
        width=32,
        command=accion,
        bootstyle="primary"
    ).pack(pady=6)

# Pie de página opcional
footer = ttk.Label(
    ventana,
    text="2025 - Mauro Purriños Vento",
    font=("Segoe UI", 9),
    anchor="center"
)
footer.pack(side="bottom", pady=(10, 5))

# Ejecutar la interfaz
ventana.mainloop()
