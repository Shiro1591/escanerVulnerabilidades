# Importaciones
import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from utils.scanner import escanear_cabeceras as escanear_cabeceras_funcion
from utils.scanner import escanear_formularios as escanear_formularios_funcion
from utils.db import guardar_resultado_escaneo, mostrar_resultados, mostrar_formularios_detectados

# Funciones de cada botón
def escanear_cabeceras():
    ventana_secundaria = ttk.Toplevel(title="Escaneo de Cabeceras")
    ventana_secundaria.geometry("600x500")

    ttk.Label(ventana_secundaria, text="Introduce una URL:", font=("Segoe UI", 12)).pack(pady=10)
    entrada_url = ttk.Entry(ventana_secundaria, width=60)
    entrada_url.pack()

    area_resultados = ttk.Text(ventana_secundaria, height=20)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

    def ejecutar_escaneo():
        url = entrada_url.get()
        if not url:
            messagebox.showwarning("Campo vacío", "Por favor, introduce una URL.")
            return

        resultado = escanear_cabeceras_funcion(url)
        guardado = guardar_resultado_escaneo(resultado)
        if not guardado:
            area_resultados.insert("end", "\nEsta URL ya fue escaneada previamente. No se almacenará de nuevo\n")


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

    ttk.Button(ventana_secundaria, text="Escanear", command=ejecutar_escaneo).pack(pady=5)

def escanear_formularios():
    ventana_secundaria = ttk.Toplevel(title="Escaneo de Formularios")
    ventana_secundaria.geometry("600x500")

    ttk.Label(ventana_secundaria, text="Introduce una URL:", font=("Segoe UI", 12)).pack(pady=10)
    entrada_url = ttk.Entry(ventana_secundaria, width=60)
    entrada_url.pack()

    area_resultados = ttk.Text(ventana_secundaria, height=20)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

    def ejecutar_escaneo():
        url = entrada_url.get()
        if not url:
            messagebox.showwarning("Campo vacío", "Por favor, introduce una URL.")
            return

        area_resultados.delete("1.0", "end")

        try:
            # Redirigir salida de consola al widget de texto
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

    ttk.Button(ventana_secundaria, text="Escanear", command=ejecutar_escaneo).pack(pady=5)

def escaneo_completo():
    ventana_secundaria = ttk.Toplevel(title="Escaneo Completo")
    ventana_secundaria.geometry("600x600")

    ttk.Label(ventana_secundaria, text="Introduce una URL:", font=("Segoe UI", 12)).pack(pady=10)
    entrada_url = ttk.Entry(ventana_secundaria, width=60)
    entrada_url.pack()

    area_resultados = ttk.Text(ventana_secundaria, height=30)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

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

            # Ejecutar escaneos
            cabeceras = escanear_cabeceras_funcion(url)
            guardar_resultado_escaneo(cabeceras)

            print("\n=== ESCANEO DE CABECERAS ===")
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

    ttk.Button(ventana_secundaria, text="Escanear Todo", command=ejecutar_escaneo_completo).pack(pady=5)

def ver_resultados():
    ventana_secundaria = ttk.Toplevel(title="Historial de Resultados")
    ventana_secundaria.geometry("750x600")

    ttk.Label(ventana_secundaria, text="Filtrar por URL (parcial):").pack(pady=(10, 0))
    filtro_entry = ttk.Entry(ventana_secundaria, width=50)
    filtro_entry.pack(pady=(0, 10))

    area_resultados = ttk.Text(ventana_secundaria, height=35)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

    def cargar_resultados():
        area_resultados.delete("1.0", "end")
        filtro = filtro_entry.get().lower()

        conexion = sqlite3.connect("db/scanner.db")
        cursor = conexion.cursor()

        # Escaneos de cabeceras
        cursor.execute("SELECT * FROM resultados_escaneos")
        escaneos = cursor.fetchall()

        area_resultados.insert("end", "=== ESCANEOS DE CABECERAS ===\n")
        for fila in escaneos:
            if filtro in fila[1].lower():
                area_resultados.insert("end", f"\nURL: {fila[1]}\nFecha: {fila[2]}\nNivel de riesgo: {fila[3]}\nVulnerabilidades: {fila[4]}\n")

        # Formularios
        cursor.execute("SELECT * FROM formularios_detectados")
        formularios = cursor.fetchall()

        if formularios:
            area_resultados.insert("end", "\n=== FORMULARIOS DETECTADOS ===\n")
            agrupados = {}
            for f in formularios:
                if filtro in f[1].lower():
                    if f[1] not in agrupados:
                        agrupados[f[1]] = []
                    agrupados[f[1]].append(f)

            for url, campos in agrupados.items():
                area_resultados.insert("end", f"\nURL: {url}\n")
                formularios_por_accion = {}
                for campo in campos:
                    key = (campo[2], campo[3])  # método, acción
                    if key not in formularios_por_accion:
                        formularios_por_accion[key] = []
                    formularios_por_accion[key].append(campo)

                for i, ((metodo, accion), campos_form) in enumerate(formularios_por_accion.items(), start=1):
                    area_resultados.insert("end", f"  Formulario {i}:\n")
                    area_resultados.insert("end", f"    Método: {metodo}\n")
                    area_resultados.insert("end", f"    Acción: {accion}\n")
                    area_resultados.insert("end", f"    Campos:\n")
                    for campo in campos_form:
                        vuln = " [vulnerable]" if campo[6] else ""
                        area_resultados.insert("end", f"      - {campo[4]} (tipo: {campo[5]}){vuln}\n")

        conexion.close()

    ttk.Button(ventana_secundaria, text="Buscar", command=cargar_resultados).pack(pady=(0, 5))

    # Mostrar todos los resultados al abrir
    cargar_resultados()

def ver_resultados():
    ventana_secundaria = ttk.Toplevel(title="Historial de Resultados")
    ventana_secundaria.geometry("750x600")

    area_resultados = ttk.Text(ventana_secundaria, height=35)
    area_resultados.pack(padx=10, pady=10, fill="both", expand=True)

    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    # Escaneos de cabeceras
    cursor.execute("SELECT * FROM resultados_escaneos")
    escaneos = cursor.fetchall()

    area_resultados.insert("end", "=== ESCANEOS DE CABECERAS ===\n")
    for fila in escaneos:
        area_resultados.insert("end", f"\nURL: {fila[1]}\nFecha: {fila[2]}\nNivel de riesgo: {fila[3]}\nVulnerabilidades: {fila[4]}\n")

    # Formularios
    cursor.execute("SELECT * FROM formularios_detectados")
    formularios = cursor.fetchall()

    if formularios:
        area_resultados.insert("end", "\n=== FORMULARIOS DETECTADOS ===\n")
        agrupados = {}
        for f in formularios:
            if f[1] not in agrupados:
                agrupados[f[1]] = []
            agrupados[f[1]].append(f)

        for url, campos in agrupados.items():
            area_resultados.insert("end", f"\nURL: {url}\n")
            formularios_por_accion = {}
            for campo in campos:
                key = (campo[2], campo[3])  # método, acción
                if key not in formularios_por_accion:
                    formularios_por_accion[key] = []
                formularios_por_accion[key].append(campo)

            for i, ((metodo, accion), campos_form) in enumerate(formularios_por_accion.items(), start=1):
                area_resultados.insert("end", f"  Formulario {i}:\n")
                area_resultados.insert("end", f"    Método: {metodo}\n")
                area_resultados.insert("end", f"    Acción: {accion}\n")
                area_resultados.insert("end", f"    Campos:\n")
                for campo in campos_form:
                    vuln = " [vulnerable]" if campo[6] else ""
                    area_resultados.insert("end", f"      - {campo[4]} (tipo: {campo[5]}){vuln}\n")

    conexion.close()


def exportar_resultados(): messagebox.showinfo("Acción", "Exportar Resultados")

# Ventana principal
ventana = ttk.Window(themename="flatly")
ventana.title("Escáner de Vulnerabilidades Web")
ventana.geometry("600x400")

# Título grande
ttk.Label(
    ventana,
    text="Escáner de Vulnerabilidades Web",
    font=("Segoe UI", 18, "bold")
).pack(pady=(30, 20))

# Contenedor para los botones
contenedor = ttk.Frame(ventana)
contenedor.pack(pady=10)

# Lista de botones con texto y función asociada
botones = [
    ("Escanear Cabeceras", escanear_cabeceras),
    ("Escanear Formularios", escanear_formularios),
    ("Escaneo Completo", escaneo_completo),
    ("Ver Resultados", ver_resultados),
    ("Exportar Resultados", exportar_resultados),
]

# Crear los botones en el contenedor
for texto, accion in botones:
    ttk.Button(contenedor, text=texto, width=30, command=accion).pack(pady=5)

# Ejecutar interfaz
ventana.mainloop()
