import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

class FormularioGuias:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de Guías y Clientes")
        self.root.geometry("450x450")
        
        # Variables del formulario
        self.var_guia = tk.StringVar(value="GUIA 1")
        self.var_mes = tk.StringVar()
        self.var_dia = tk.StringVar()
        self.var_cliente = tk.StringVar()
        self.var_prenda = tk.StringVar()
        self.var_valor = tk.StringVar()
        self.var_ciudad = tk.StringVar()
        self.var_direccion = tk.StringVar()
        
        # Lista en memoria para almacenar los registros agregados
        self.datos_registrados = []
        
        # AHORA EL HISTORIAL SE DIVIDIRÁ POR GUÍA DINÁMICAMENTE
        self.historial_por_guia = {}
        
        self.widgets_combos = {}
        self.crear_interfaz()

    def crear_interfaz(self):
        frame = ttk.LabelFrame(self.root, text=" Datos del Registro ", padding=15)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Guía principal (Solo lectura)
        ttk.Label(frame, text="Seleccionar Guía:").grid(row=0, column=0, sticky="w", pady=4)
        combo_guia = ttk.Combobox(frame, textvariable=self.var_guia, values=[f"GUIA {i}" for i in range(1, 101)], state="readonly")
        combo_guia.grid(row=0, column=1, sticky="ew", padx=10, pady=4)
        
        # ENLACE: Detectar cuando cambias de guía para refrescar las sugerencias de los combos
        combo_guia.bind("<<ComboboxSelected>>", self.al_cambiar_guia)
        
        # Campos con autocompletado dinámico utilizando Combobox editables
        campos = [
            ("Mes:", self.var_mes, "Mes"),
            ("Día:", self.var_dia, "Día"),
            ("Cliente:", self.var_cliente, "Cliente"),
            ("Prenda:", self.var_prenda, "Prenda"),
            ("Valor:", self.var_valor, "Valor"),
            ("Ciudad:", self.var_ciudad, "Ciudad"),
            ("Dirección:", self.var_direccion, "Dirección"),
        ]
        
        for idx, (label_text, variable, nombre_campo) in enumerate(campos, start=1):
            ttk.Label(frame, text=label_text).grid(row=idx, column=0, sticky="w", pady=4)
            
            # Un Combobox con state="normal" permite escribir libremente como un Entry
            cb = ttk.Combobox(frame, textvariable=variable, state="normal")
            cb.grid(row=idx, column=1, sticky="ew", padx=10, pady=4)
            
            self.widgets_combos[nombre_campo] = cb
            # Evento que filtra las opciones dinámicamente mientras el usuario escribe
            cb.bind("<KeyRelease>", lambda event, nc=nombre_campo, v=variable, w=cb: self.filtrar_sugerencias(event, nc, v, w))
            
        frame.grid_columnconfigure(1, weight=1)
            
        # Botones de acción
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Añadir Registro", command=self.guardar_en_memoria).pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(btn_frame, text="Descargar Excel", command=self.exportar_excel).pack(side="right", padx=5, expand=True, fill="x")

    def obtener_historial_guia_actual(self):
        """Retorna el historial específico de la guía seleccionada actual. Si no existe, lo crea."""
        guia_actual = self.var_guia.get()
        if guia_actual not in self.historial_por_guia:
            self.historial_por_guia[guia_actual] = {
                "Mes": set(), "Día": set(), "Cliente": set(), "Prenda": set(),
                "Valor": set(), "Ciudad": set(), "Dirección": set()
            }
        return self.historial_por_guia[guia_actual]

    def al_cambiar_guia(self, event):
        """Actualiza las listas de los combobox con el historial correspondiente a la nueva guía."""
        historial_guia = self.obtener_historial_guia_actual()
        for campo, cb in self.widgets_combos.items():
            cb.configure(values=list(historial_guia[campo]))

    def filtrar_sugerencias(self, event, nombre_campo, variable, widget):
        """Filtra y muestra la lista desplegable basándose únicamente en el historial de la guía activa."""
        if event.keysym in ["Up", "Down", "Return", "Escape", "Left", "Right", "Shift_L", "Shift_R"]:
            return
            
        texto_ingresado = variable.get().lower()
        
        # Obtener el historial ligado a la guía activa
        historial_guia = self.obtener_historial_guia_actual()
        historial_campo = historial_guia[nombre_campo]
        
        if not texto_ingresado:
            widget.configure(values=list(historial_campo))
            widget.event_generate("<<ComboboxClose>>")
            return
            
        # Buscar coincidencias dentro de esta guía
        coincidencias = [opcion for opcion in historial_campo if texto_ingresado in opcion.lower()]
        
        if coincidencias:
            widget.configure(values=coincidencias)
            widget.event_generate("<Down>") 
        else:
            widget.configure(values=[])
            widget.event_generate("<<ComboboxClose>>")

    def guardar_en_memoria(self):
        if not self.var_cliente.get() or not self.var_prenda.get():
            messagebox.showwarning("Advertencia", "Por favor, llena los campos principales (Cliente y Prenda)")
            return
            
        guia_actual = self.var_guia.get()
        registro = {
            "Guía": guia_actual,
            "Mes": self.var_mes.get(),
            "Día": self.var_dia.get(),
            "Cliente": self.var_cliente.get(),
            "Prenda": self.var_prenda.get(),
            "Valor": self.var_valor.get(),
            "Ciudad": self.var_ciudad.get(),
            "Dirección": self.var_direccion.get()
        }
        
        # Añadir al listado general
        self.datos_registrados.append(registro)
        
        # Alimentar el historial de memoria ligado exclusivamente a ESTA guía
        historial_guia = self.obtener_historial_guia_actual()
        for campo, valor in registro.items():
            if campo != "Guía" and valor.strip():
                historial_guia[campo].add(valor.strip())
                # Actualizar inmediatamente los valores visuales del combobox activo
                self.widgets_combos[campo].configure(values=list(historial_guia[campo]))
        
        messagebox.showinfo("Éxito", f"Registro para {guia_actual} añadido correctamente.")
        
        # Limpiar los campos para preparar el siguiente registro
        self.var_cliente.set("")
        self.var_prenda.set("")
        self.var_valor.set("")
        self.var_direccion.set("")

    def exportar_excel(self):
        if not self.datos_registrados:
            messagebox.showwarning("Error", "No hay datos registrados para exportar.")
            return
            
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx")],
            title="Guardar reporte de guías"
        )
        
        if ruta_archivo:
            df = pd.DataFrame(self.datos_registrados)
            
            # --- SECCIÓN DE ORDENAMIENTO DE GUÍAS ---
            df['Num_Guia'] = df['Guía'].str.extract(r'(\d+)').astype(int)
            df = df.sort_values(by='Num_Guia', ascending=True)
            df = df.drop(columns=['Num_Guia'])
            # ----------------------------------------
            
            df.to_excel(ruta_archivo, index=False)
            messagebox.showinfo("Guardado", f"Archivo exportado con éxito en:\n{ruta_archivo}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioGuias(root)
    root.mainloop()
