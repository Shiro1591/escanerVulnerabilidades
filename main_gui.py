# Importaciones
import sqlite3, os, platform, subprocess
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from utils.scanner import escanear_cabeceras as escanear_cabeceras_funcion, escanear_formularios as escanear_formularios_funcion, simular_ataques as ejecutar_ataques
from utils.db import guardar_resultado_escaneo, exportar_a_json, exportar_a_csv, exportar_ataques_a_json, exportar_ataques_a_csv
from db.init_db import init_db


# Funciones de cada botón

# Método que escanea las cabeceras HTTP de una URL
def escanear_cabeceras():
    # Ventana secundaria 
    ventana_secundaria = ttk.Toplevel(title="Escaneo de Cabeceras")
    ventana_secundaria.geometry("700x540")
    ventana_secundaria.resizable(False, False)

    # Título de la ventana
    ttk.Label(
        ventana_secundaria,
        text="Escaneo de Cabeceras HTTP",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    frame_url = ttk.Frame(ventana_secundaria)
    frame_url.pack(pady=10)

    ttk.Label(frame_url, text="Introduce una URL:", font=("Segoe UI", 11)).pack(anchor="w", padx=10)
    entrada_url = ttk.Entry(frame_url, width=70)
    entrada_url.pack(padx=10, pady=(0, 10))

    # Método que ejecuta el escaneo de cabeceras
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

    # Muestra los resultados
    area_resultados = ttk.Text(ventana_secundaria, height=20)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

# Método que escanea formularios HTML de una URL
def escanear_formularios():
    # Ventana secundaria 
    ventana_secundaria = ttk.Toplevel(title="Escaneo de Formularios")
    ventana_secundaria.geometry("700x540")
    ventana_secundaria.resizable(False, False)

    # Título de la ventana
    ttk.Label(
        ventana_secundaria,
        text="Escaneo de Formularios HTML",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    frame_url = ttk.Frame(ventana_secundaria)
    frame_url.pack(pady=10)

    ttk.Label(frame_url, text="Introduce una URL:", font=("Segoe UI", 11)).pack(anchor="w", padx=10)
    entrada_url = ttk.Entry(frame_url, width=70)
    entrada_url.pack(padx=10, pady=(0, 10))

    # Método que ejecuta el escaneo de formularios
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

    # Botón para escanear
    ttk.Button(frame_url, text="Escanear", width=20, command=ejecutar_escaneo, bootstyle="primary").pack(pady=5)

    # Muestra los resultados
    area_resultados = ttk.Text(ventana_secundaria, height=20)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

# Método que escanea cabeceras y formularios de una URL
def escaneo_completo():
    # Ventana secundaria
    ventana_secundaria = ttk.Toplevel(title="Escaneo Completo")
    ventana_secundaria.geometry("750x600")
    ventana_secundaria.resizable(False, False)

    # Título de la ventana
    ttk.Label(
        ventana_secundaria,
        text="Escaneo Completo (Cabeceras + Formularios)",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    frame_url = ttk.Frame(ventana_secundaria)
    frame_url.pack(pady=10)

    ttk.Label(frame_url, text="Introduce una URL:", font=("Segoe UI", 11)).pack(anchor="w", padx=10)
    entrada_url = ttk.Entry(frame_url, width=70)
    entrada_url.pack(padx=10, pady=(0, 10))

    # Método que ejecuta el escaneo completo
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

            # Escaneo de formularios
            print("\n=== ESCANEO DE FORMULARIOS ===")
            escanear_formularios_funcion(url)

            sys.stdout = sys.__stdout__
            resultado = buffer.getvalue()
            area_resultados.insert("end", resultado)

        except Exception as e:
            sys.stdout = sys.__stdout__
            area_resultados.insert("end", f"Error durante el escaneo completo: {e}")

    # Botón para escanear
    ttk.Button(frame_url, text="Escanear Todo", width=20, command=ejecutar_escaneo_completo, bootstyle="primary").pack(pady=5)

    # Muestra los resultados
    area_resultados = ttk.Text(ventana_secundaria, height=25)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

# Método que muestra los resultados de los escaneos
def ver_resultados():
    ventana_secundaria = ttk.Toplevel(title="Historial de Escaneos por URL")
    ventana_secundaria.geometry("850x600")
    ventana_secundaria.resizable(False, False)

    # Título de la ventana
    ttk.Label(
        ventana_secundaria,
        text="Historial de Escaneos",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    # Muestra los resultados
    frame_contenido = ttk.Frame(ventana_secundaria)
    frame_contenido.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    area_resultados = ttk.Text(frame_contenido, height=30, font=("Segoe UI", 10))
    area_resultados.pack(fill="both", expand=True)

    # Accede a la base de datos
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

        # Escaneo de formularios
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

# Método que exporta los resultados a un archivo JSON o CSV
def exportar_resultados():
    ventana_exportar = ttk.Toplevel(title="Exportar Resultados")
    ventana_exportar.geometry("500x300")
    ventana_exportar.resizable(False, False)

    ttk.Label(
        ventana_exportar,
        text="Exportar Resultados",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    frame = ttk.Frame(ventana_exportar)
    frame.pack(pady=10, padx=10, fill="x")

    # Nombre del archivo
    ttk.Label(frame, text="Nombre del archivo (sin extensión):").pack(anchor="w")
    entrada_ruta = ttk.Entry(frame, width=50)
    entrada_ruta.pack(pady=5)

    # Selección de qué exportar
    ttk.Label(frame, text="¿Qué deseas exportar?").pack(anchor="w", pady=(10, 0))
    tipo_exportacion = ttk.StringVar(value="escaneos")
    opciones_tipo = ttk.Frame(frame)
    opciones_tipo.pack(anchor="w", pady=5)
    ttk.Radiobutton(opciones_tipo, text="Resultados de escaneos", variable=tipo_exportacion, value="escaneos").pack(side="left", padx=5)
    ttk.Radiobutton(opciones_tipo, text="Ataques detectados", variable=tipo_exportacion, value="ataques").pack(side="left", padx=5)

    # Formato de exportación
    ttk.Label(frame, text="Selecciona formato de exportación:").pack(anchor="w", pady=(10, 0))
    formato_var = ttk.StringVar(value="json")
    opciones_formato = ttk.Frame(frame)
    opciones_formato.pack(anchor="w", pady=5)
    ttk.Radiobutton(opciones_formato, text="JSON", variable=formato_var, value="json").pack(side="left", padx=5)
    ttk.Radiobutton(opciones_formato, text="CSV", variable=formato_var, value="csv").pack(side="left", padx=5)

    def ejecutar_exportacion():
        nombre = entrada_ruta.get().strip()
        if not nombre:
            messagebox.showwarning("Campo vacío", "Debes introducir un nombre de archivo.")
            return

        tipo = tipo_exportacion.get()
        formato = formato_var.get()
        ruta = f"{nombre}.{formato}"

        # Exporta el formato seleccionado
        if tipo == "escaneos":
            archivo = exportar_a_json(ruta) if formato == "json" else exportar_a_csv(ruta)
        else:
            archivo = exportar_ataques_a_json(ruta) if formato == "json" else exportar_ataques_a_csv(ruta)

        abrir_carpeta_contenedora(archivo)
        messagebox.showinfo("Exportación completada", f"Archivo guardado como:\n{archivo}")
        ventana_exportar.destroy()

    ttk.Button(ventana_exportar, text="Exportar", width=20, command=ejecutar_exportacion, bootstyle="primary").pack(pady=10)

# Método que abre la carpeta donde se ha guardado el archivo exportado, según el sistema operativo
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

# Método que simula ataques en formularios con payloads
def simular_ataque():
    ventana_secundaria = ttk.Toplevel(title="Simular Ataque (XSS / SQLi)")
    ventana_secundaria.geometry("700x540")
    ventana_secundaria.resizable(False, False)

    # Título de la ventana
    ttk.Label(
        ventana_secundaria,
        text="Simulación de Ataques en Formularios",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    frame_url = ttk.Frame(ventana_secundaria)
    frame_url.pack(pady=10)

    ttk.Label(frame_url, text="Introduce una URL escaneada previamente:", font=("Segoe UI", 11)).pack(anchor="w", padx=10)
    entrada_url = ttk.Entry(frame_url, width=70)
    entrada_url.pack(padx=10, pady=(0, 10))

    # Selector de tipo de ataque
    ttk.Label(frame_url, text="Tipo de ataque a simular:", font=("Segoe UI", 11)).pack(anchor="w", padx=10)
    tipo_var = ttk.StringVar(value="Ambos")

    frame_tipo = ttk.Frame(frame_url)
    frame_tipo.pack(anchor="w", padx=10, pady=5)

    ttk.Radiobutton(frame_tipo, text="Ambos", variable=tipo_var, value="Ambos").pack(side="left", padx=5)
    ttk.Radiobutton(frame_tipo, text="Solo XSS", variable=tipo_var, value="XSS").pack(side="left", padx=5)
    ttk.Radiobutton(frame_tipo, text="Solo SQLi", variable=tipo_var, value="SQLi").pack(side="left", padx=5)      
       
    # Área para mostrar resultados
    area_resultados = ttk.Text(ventana_secundaria, height=20)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

    # Método que ejecuta la simulación
    def ejecutar_simulacion():
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
            tipo = tipo_var.get()
            ejecutar_ataques(url, tipo)
            sys.stdout = sys.__stdout__
            resultado = buffer.getvalue()
            area_resultados.insert("end", resultado)
        except Exception as e:
            sys.stdout = sys.__stdout__
            area_resultados.insert("end", f"Error durante la simulación: {e}")

    ttk.Button(frame_url, text="Simular Ataque", width=20, command=ejecutar_simulacion).pack(pady=5)

# Método que muestra los ataques detectados guardados en la base de datos
def ver_ataques_detectados():
    ventana_secundaria = ttk.Toplevel(title="Ataques Detectados")
    ventana_secundaria.geometry("850x600")
    ventana_secundaria.resizable(False, False)

    # Título
    ttk.Label(
        ventana_secundaria,
        text="Historial de Ataques Detectados",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 10))

    frame_contenido = ttk.Frame(ventana_secundaria)
    frame_contenido.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    area_resultados = ttk.Text(frame_contenido, height=30, font=("Segoe UI", 10))
    area_resultados.pack(fill="both", expand=True)

    # Consulta base de datos
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT url, metodo, accion, campo_nombre, tipo_payload, payload, evidencia, fecha
        FROM ataques_detectados
        ORDER BY url ASC, fecha DESC
    """)
    ataques = cursor.fetchall()
    conexion.close()

    if not ataques:
        area_resultados.insert("end", "No se han detectado ataques aún.")
        return

    # Agrupa por URL
    agrupados = {}
    for fila in ataques:
        url = fila[0]
        if url not in agrupados:
            agrupados[url] = []
        agrupados[url].append(fila)

    # Muestra agrupado
    for url, registros in agrupados.items():
        area_resultados.insert("end", f"\n=== URL: {url} ===\n")
        for fila in registros:
            _, metodo, accion, campo, tipo, payload, evidencia, fecha = fila
            tag = "xss" if tipo.lower() == "xss" else "sqli" if tipo.lower() == "sqli" else "info"

            area_resultados.insert("end", f"[{fecha}]\n", tag)
            area_resultados.insert("end", f"- Método: {metodo}\n", tag)
            area_resultados.insert("end", f"- Acción: {accion}\n", tag)
            area_resultados.insert("end", f"- Campo: {campo}\n", tag)
            area_resultados.insert("end", f"- Tipo: {tipo}\n", tag)
            area_resultados.insert("end", f"- Payload: {payload}\n", tag)
            area_resultados.insert("end", f"- Evidencia: {evidencia}\n")
            area_resultados.insert("end", "-" * 60 + "\n", "info")

# Crea la base de datos si no existe
init_db()





# Interfaz gráfica principal
# Ventana principal 
ventana = ttk.Window(themename="darkly")
ventana.title("Escáner de Vulnerabilidades Web")
ventana.geometry("640x460")
ventana.resizable(False, False)

# Espacio para título
header = ttk.Frame(ventana)
header.pack(fill="x", pady=(20, 10))

# Título de la ventana
ttk.Label(
    header,
    text="Escáner de Vulnerabilidades Web",
    font=("Segoe UI", 20, "bold"),
    anchor="center"
).pack()

# Espacio para botones
frame_botones = ttk.Frame(ventana)
frame_botones.pack(pady=30)

# Lista de botones y funciones
botones = [
    ("Escanear Cabeceras", escanear_cabeceras),
    ("Escanear Formularios", escanear_formularios),
    ("Escaneo Completo", escaneo_completo),
    ("Ver Resultados", ver_resultados),
    ("Simular ataque", simular_ataque),
    ("Ver Ataques Detectados", ver_ataques_detectados),
    ("Exportar Resultados", exportar_resultados)
]

# Añade los botones a la ventana 
for texto, accion in botones:
    ttk.Button(
        frame_botones,
        text=texto,
        width=32,
        command=accion,
        bootstyle="primary"
    ).pack(pady=6)

# Método que añade y muestra un contador de ataques detectados
def contar_ataques():
    try:
        conexion = sqlite3.connect("db/scanner.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM ataques_detectados")
        cantidad = cursor.fetchone()[0]
        conexion.close()
        return cantidad
    except:
        return 0

# Contador de ataques detectadoss
contador = contar_ataques()
ttk.Label(
    ventana,
    text=f"Ataques detectados: {contador}",
    font=("Segoe UI", 10),
    anchor="center"
).pack(side= "top", pady=(0, 0))


# Pie de página 
footer = ttk.Label(
    ventana,
    text="2025 - Mauro Purriños Vento",
    font=("Segoe UI", 8),
    anchor="center"
)
footer.pack(side="bottom", pady=(0, 0))

# Ejecuta la interfaz
ventana.mainloop()
