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
        self.identificadores_registros = []
        self.siguiente_identificador = 0
        self.registro_en_edicion = None
        self.ventana_historial = None
        self.tabla_historial = None
        
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
        
        self.boton_guardar = ttk.Button(btn_frame, text="Añadir Registro", command=self.guardar_en_memoria)
        self.boton_guardar.pack(side="left", padx=5, expand=True, fill="x")
        self.boton_cancelar_edicion = ttk.Button(
            btn_frame, text="Cancelar edición", command=self.cancelar_edicion
        )
        ttk.Button(btn_frame, text="Ver historial", command=self.mostrar_historial).pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(btn_frame, text="Descargar Excel", command=self.exportar_excel).pack(side="right", padx=5, expand=True, fill="x")

    def mostrar_historial(self):
        """Abre el historial de registros de la sesión actual."""
        if self.ventana_historial is not None and self.ventana_historial.winfo_exists():
            self.ventana_historial.deiconify()
            self.ventana_historial.lift()
            self.actualizar_tabla_historial()
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Historial de registros")
        ventana.geometry("1050x400")
        self.ventana_historial = ventana
        ventana.protocol("WM_DELETE_WINDOW", self.cerrar_historial)

        columnas = ("Guía", "Mes", "Día", "Cliente", "Prenda", "Valor", "Ciudad", "Dirección")
        contenedor = ttk.Frame(ventana, padding=10)
        contenedor.pack(fill="both", expand=True)

        tabla = ttk.Treeview(contenedor, columns=columnas, show="headings", selectmode="browse")
        for columna in columnas:
            tabla.heading(columna, text=columna)
            tabla.column(columna, width=110, minwidth=75)
        tabla.column("Dirección", width=180)

        barra_vertical = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
        barra_horizontal = ttk.Scrollbar(contenedor, orient="horizontal", command=tabla.xview)
        tabla.configure(yscrollcommand=barra_vertical.set, xscrollcommand=barra_horizontal.set)
        tabla.grid(row=0, column=0, sticky="nsew")
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)
        tabla.bind("<Double-1>", lambda _event: self.editar_registro_seleccionado())
        self.tabla_historial = tabla

        botones = ttk.Frame(ventana, padding=(10, 0, 10, 10))
        botones.pack(fill="x")
        ttk.Button(botones, text="Editar registro", command=self.editar_registro_seleccionado).pack(side="left", padx=5)
        ttk.Button(botones, text="Eliminar registro", command=self.eliminar_registro_seleccionado).pack(side="left", padx=5)

        self.actualizar_tabla_historial()

    def cerrar_historial(self):
        if self.ventana_historial is not None:
            self.ventana_historial.destroy()
        self.ventana_historial = None
        self.tabla_historial = None

    def actualizar_tabla_historial(self):
        if self.tabla_historial is None or not self.tabla_historial.winfo_exists():
            return

        self.tabla_historial.delete(*self.tabla_historial.get_children())
        for identificador, registro in zip(self.identificadores_registros, self.datos_registrados):
            valores = tuple(registro[campo] for campo in self.tabla_historial["columns"])
            self.tabla_historial.insert("", "end", iid=str(identificador), values=valores)

    def editar_registro_seleccionado(self):
        if self.tabla_historial is None:
            return
        seleccion = self.tabla_historial.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un registro para editar.")
            return

        identificador = int(seleccion[0])
        indice = self.identificadores_registros.index(identificador)
        registro = self.datos_registrados[indice]
        self.var_guia.set(registro["Guía"])
        self.al_cambiar_guia(None)
        self.var_mes.set(registro["Mes"])
        self.var_dia.set(registro["Día"])
        self.var_cliente.set(registro["Cliente"])
        self.var_prenda.set(registro["Prenda"])
        self.var_valor.set(registro["Valor"])
        self.var_ciudad.set(registro["Ciudad"])
        self.var_direccion.set(registro["Dirección"])
        self.registro_en_edicion = identificador
        self.boton_guardar.configure(text="Actualizar Registro")
        self.boton_cancelar_edicion.pack(side="left", padx=5, expand=True, fill="x")
        self.root.lift()

    def eliminar_registro_seleccionado(self):
        if self.tabla_historial is None:
            return
        seleccion = self.tabla_historial.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un registro para eliminar.")
            return

        identificador = int(seleccion[0])
        if not messagebox.askyesno("Confirmar eliminación", "¿Deseas eliminar el registro seleccionado?"):
            return

        indice = self.identificadores_registros.index(identificador)
        del self.datos_registrados[indice]
        del self.identificadores_registros[indice]
        if self.registro_en_edicion == identificador:
            self.cancelar_edicion()
        self.reconstruir_historial_sugerencias()
        self.actualizar_tabla_historial()

    def cancelar_edicion(self):
        self.registro_en_edicion = None
        self.boton_guardar.configure(text="Añadir Registro")
        self.boton_cancelar_edicion.pack_forget()
        self.limpiar_campos()

    def limpiar_campos(self):
        self.var_mes.set("")
        self.var_dia.set("")
        self.var_cliente.set("")
        self.var_prenda.set("")
        self.var_valor.set("")
        self.var_ciudad.set("")
        self.var_direccion.set("")

    def reconstruir_historial_sugerencias(self):
        self.historial_por_guia = {}
        for registro in self.datos_registrados:
            guia = registro["Guía"]
            historial = self.historial_por_guia.setdefault(
                guia,
                {
                    "Mes": set(), "Día": set(), "Cliente": set(), "Prenda": set(),
                    "Valor": set(), "Ciudad": set(), "Dirección": set()
                }
            )
            for campo, valores in historial.items():
                valor = registro[campo].strip()
                if valor:
                    valores.add(valor)

        historial_guia = self.obtener_historial_guia_actual()
        for campo, widget in self.widgets_combos.items():
            widget.configure(values=list(historial_guia[campo]))

    def obtener_historial_guia_actual(self):
        """Retorna el historial específico de la guía seleccionada actual. Si no existe, lo crea."""
        guia_actual = self.var_guia.get()
        if guia_actual not in self.historial_por_guia:
            self.historial_por_guia[guia_actual] = {
                "Mes": set(), "Día": set(), "Cliente": set(), "Prenda": set(),
                "Valor": set(), "Ciudad": set(), "Dirección": set()
            }
        return self.historial_por_guia[guia_actual]

    def al_cambiar_guia(self, _event):
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
        
        if self.registro_en_edicion is None:
            self.datos_registrados.append(registro)
            self.identificadores_registros.append(self.siguiente_identificador)
            self.siguiente_identificador += 1
            mensaje = f"Registro para {guia_actual} añadido correctamente."
        else:
            indice = self.identificadores_registros.index(self.registro_en_edicion)
            self.datos_registrados[indice] = registro
            mensaje = f"Registro para {guia_actual} actualizado correctamente."
            self.registro_en_edicion = None
            self.boton_guardar.configure(text="Añadir Registro")
            self.boton_cancelar_edicion.pack_forget()

        self.reconstruir_historial_sugerencias()
        self.actualizar_tabla_historial()
        messagebox.showinfo("Éxito", mensaje)
        self.limpiar_campos()

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
