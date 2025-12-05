import customtkinter as ctk
from tkinter import ttk, filedialog
import threading
import time

from controllers.mcpp_controller import McppController


class AppUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración visual
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.title("Consulta de Cuentas Bancarias V1")
        self.geometry("1250x740")

        self.controller = McppController()
        self.file_path = None

        self.create_widgets()

    # -------------------------------------------------------------------
    # UI PRINCIPAL
    # -------------------------------------------------------------------
    def create_widgets(self):

        # Título principal
        title = ctk.CTkLabel(
            self,
            text="Consulta de Cuentas Bancarias",
            font=("Arial Rounded MT Bold", 30),
        )
        title.pack(pady=15)

        # Contenedor general
        main = ctk.CTkFrame(self, corner_radius=20, fg_color="#F4F6F9")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=2)

        # =====================================================================
        # 🟦 CARD IZQUIERDA — CONSULTA INDIVIDUAL (Tipo Quasar)
        # =====================================================================
        card_left = ctk.CTkFrame(
            main,
            corner_radius=20,
            fg_color="white",
            border_width=1,
            border_color="#DDE1E7",
        )
        card_left.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        ctk.CTkLabel(
            card_left, text="Consulta Individual", font=("Arial", 18, "bold")
        ).pack(pady=12)

        # Combobox criterio
        ctk.CTkLabel(card_left, text="Criterio:", anchor="w").pack(pady=2)
        self.cb_criterio = ctk.CTkComboBox(
            card_left,
            values=["NUMERO DE DOCUMENTO", "NUMERO DE CUENTA BANCARIA"],
            width=230,
        )
        self.cb_criterio.pack(pady=5)

        # Input valor
        ctk.CTkLabel(card_left, text="Valor:", anchor="w").pack(pady=2)
        self.txt_buscar = ctk.CTkEntry(card_left, width=230)
        self.txt_buscar.pack(pady=5)

        # Botón
        btn_ind = ctk.CTkButton(
            card_left,
            text="Analizar",
            width=230,
            fg_color="#1565C0",
            hover_color="#0D47A1",
            command=self.start_individual_query,
        )
        btn_ind.pack(pady=12)

        # Barra de progreso individual
        self.progress_ind = ctk.CTkProgressBar(card_left, width=230)
        self.progress_ind.set(0)
        self.progress_ind.pack(pady=5)
        self.progress_ind.pack_forget()

        # Banner
        self.banner_ind = ctk.CTkLabel(
            card_left,
            text="Aquí aparecerá el resultado individual.",
            text_color="#555",
            font=("Arial", 12),
        )
        self.banner_ind.pack(pady=6)

        # Tabla individual
        table_frame_ind = ctk.CTkFrame(card_left, fg_color="transparent")
        table_frame_ind.pack(fill="both", expand=True)

        self.table_individual = ttk.Treeview(
            table_frame_ind,
            columns=("index", "cuenta", "doc", "estado", "fecha"),
            show="headings",
            height=10,
        )

        self.table_individual.heading("index", text="#")
        self.table_individual.heading("cuenta", text="Número Cuenta")
        self.table_individual.heading("doc", text="T.Doc / N.Doc")
        self.table_individual.heading("estado", text="Estado / Condición")
        self.table_individual.heading("fecha", text="F. Modificación")

        self.table_individual.column("index", width=40, anchor="center")
        self.table_individual.column("cuenta", width=150)
        self.table_individual.column("doc", width=170)
        self.table_individual.column("estado", width=170, anchor="center")
        self.table_individual.column("fecha", width=130, anchor="center")

        self.table_individual.pack(side="left", fill="both", expand=True)

        scroll_ind = ttk.Scrollbar(
            table_frame_ind, orient="vertical", command=self.table_individual.yview
        )
        scroll_ind.pack(side="right", fill="y")
        self.table_individual.configure(yscrollcommand=scroll_ind.set)

        # =====================================================================
        # 🟩 CARD DERECHA — CONSULTA MASIVA
        # =====================================================================
        card_right = ctk.CTkFrame(
            main,
            corner_radius=20,
            fg_color="white",
            border_width=1,
            border_color="#DDE1E7",
        )
        card_right.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)

        ctk.CTkLabel(
            card_right, text="Consulta Masiva", font=("Arial", 18, "bold")
        ).pack(pady=12)

        ctk.CTkButton(
            card_right,
            text="Seleccionar Excel",
            width=260,
            command=self.select_file,
        ).pack(pady=6)

        self.lbl_file = ctk.CTkLabel(card_right, text="Ningún archivo seleccionado")
        self.lbl_file.pack()

        ctk.CTkButton(
            card_right,
            text="Procesar Archivo",
            width=260,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            command=self.process_file,
        ).pack(pady=12)

        self.progress = ctk.CTkProgressBar(card_right, width=260)
        self.progress.set(0)
        self.progress.pack(pady=8)
        self.progress.pack_forget()

        # Tabla masiva
        table_frame = ctk.CTkFrame(card_right, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, pady=10)

        self.table = ttk.Treeview(
            table_frame,
            columns=("dni", "cuenta", "estado"),
            show="headings",
        )
        self.table.heading("dni", text="DNI")
        self.table.heading("cuenta", text="Cuenta")
        self.table.heading("estado", text="Estado")

        self.table.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scroll.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scroll.set)

    # -------------------------------------------------------------------
    # MENSAJOS / BADGES
    # -------------------------------------------------------------------
    def badge_estado(self, estado):
        return "🟢 ACTIVA" if estado else "🔴 INACTIVA"

    # -------------------------------------------------------------------
    # CONSULTA INDIVIDUAL (THREAD)
    # -------------------------------------------------------------------
    def start_individual_query(self):
        threading.Thread(target=self.run_individual_query, daemon=True).start()

    def run_individual_query(self):
        criterio = self.cb_criterio.get()
        criterio_number = 2 if criterio == "NUMERO DE CUENTA BANCARIA" else 1
        valor = self.txt_buscar.get()

        # Mostrar progreso
        self.progress_ind.set(0)
        self.progress_ind.pack()
        self.banner_ind.configure(text="Consultando...")

        self.update_idletasks()

        # Animación
        for i in range(20):
            self.progress_ind.set(i / 20)
            time.sleep(0.02)

        # Llamada al controlador
        response = self.controller.analizar_cuentas_bancarias_individual(
            valor, criterio_number
        )

        # Limpiar tabla
        for row in self.table_individual.get_children():
            self.table_individual.delete(row)

        if not response or "data" not in response:
            self.banner_ind.configure(text="No se encontraron resultados.")
            return

        datos = response["data"]

        for i, item in enumerate(datos, start=1):
            doc = (
                f"{item.get('desTipoDocumento', '')}\n{item.get('numeroDocumento', '')}"
            )
            est = f"{item.get('desEsato', '')}\n{item.get('desCondicion', '')}"

            self.table_individual.insert(
                "",
                "end",
                values=(
                    i,
                    item.get("numeroCuenta", ""),
                    doc,
                    est,
                    item.get("fechaModificacion", ""),
                ),
            )

        self.progress_ind.set(1)
        self.banner_ind.configure(text="Consulta completada ✓")

    # -------------------------------------------------------------------
    # SELECCIONAR ARCHIVO
    # -------------------------------------------------------------------
    def select_file(self):
        path = filedialog.askopenfilename(
            title="Seleccionar Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls *.csv")],
        )
        if path:
            self.file_path = path
            self.lbl_file.configure(text=f"Archivo: {path}")
        else:
            self.lbl_file.configure(text="Ningún archivo seleccionado")

    # -------------------------------------------------------------------
    # CONSULTA MASIVA
    # -------------------------------------------------------------------
    def process_file(self):
        if not self.file_path:
            self.lbl_file.configure(text="⚠ Selecciona un archivo primero")
            return

        self.progress.pack()
        self.progress.set(0)
        self.update_idletasks()

        for row in self.table.get_children():
            self.table.delete(row)

        resultados = self.controller.analizar_cuentas_bancarias_masiva(self.file_path)

        if isinstance(resultados, dict) and resultados.get("error"):
            self.lbl_file.configure(text=f"Error: {resultados['message']}")
            return

        for item in resultados:
            self.table.insert(
                "",
                "end",
                values=(item["dni"], item["cuenta"], self.badge_estado(item["estado"])),
            )

        self.progress.set(1)
        self.lbl_file.configure(text="Procesamiento completado ✓")
