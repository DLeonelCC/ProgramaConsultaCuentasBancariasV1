import customtkinter as ctk
from tkinter import filedialog, ttk
from controllers.mcpp_controller import McppController


class AppUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Consulta de Cuentas Bancarias - MCPPP")
        self.geometry("1200x700")
        ctk.set_appearance_mode("light")

        self.controller = McppController()
        self.file_path = None

        self.create_widgets()

    # ---------------- UI ----------------
    def create_widgets(self):

        # Título
        title = ctk.CTkLabel(
            self,
            text="Consulta Masiva de Cuentas Bancarias",
            font=("Arial", 22, "bold"),
        )
        title.pack(pady=10)

        # Frame principal
        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # --- BOTÓN CARGAR ARCHIVO ---
        btn_select = ctk.CTkButton(
            frame, text="Seleccionar Archivo Excel", command=self.select_file
        )
        btn_select.pack(pady=10)

        # Mostrar archivo seleccionado
        self.lbl_file = ctk.CTkLabel(frame, text="Ningún archivo seleccionado")
        self.lbl_file.pack()

        # --- BOTÓN PROCESAR ---
        btn_process = ctk.CTkButton(
            frame, text="Analizar Archivo", command=self.process_file
        )
        btn_process.pack(pady=15)

        # --- TABLA RESULTADOS ---
        self.table = ttk.Treeview(
            frame, columns=("dni", "cuenta", "estado"), show="headings"
        )
        self.table.heading("dni", text="DNI")
        self.table.heading("cuenta", text="Cuenta")
        self.table.heading("estado", text="Estado")

        self.table.column("dni", width=150, anchor="center")
        self.table.column("cuenta", width=200, anchor="center")
        self.table.column("estado", width=150, anchor="center")

        self.table.pack(fill="both", expand=True, pady=10)

    # ---------------- LÓGICA ----------------
    def select_file(self):
        path = filedialog.askopenfilename(
            title="Seleccionar Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls *.csv")],
        )

        if path:
            self.file_path = path
            self.lbl_file.configure(text=f"Archivo seleccionado: {path}")
        else:
            self.lbl_file.configure(text="Ningún archivo seleccionado")

    def process_file(self):
        if not self.file_path:
            self.lbl_file.configure(text="⚠ Selecciona un archivo primero")
            return

        # Limpiar tabla
        for row in self.table.get_children():
            self.table.delete(row)

        # Procesar con el controlador
        resultados = self.controller.analizar_cuentas_bancarias_masiva(self.file_path)

        if isinstance(resultados, dict) and resultados.get("error"):
            self.lbl_file.configure(text=f"Error: {resultados['message']}")
            return

        # Agregar filas a la tabla
        for item in resultados:
            estado = "Correcto" if item["estado"] else "Incorrecto"
            self.table.insert("", "end", values=(item["dni"], item["cuenta"], estado))
