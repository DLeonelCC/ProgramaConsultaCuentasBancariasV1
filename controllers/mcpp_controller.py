import time
import pandas as pd
from services.mcpp_service import McppApiService


class McppController:
    def __init__(self):
        self.api = McppApiService()

    # ----------------------------------------------------
    # BÚSQUEDA INDIVIDUAL
    # ----------------------------------------------------
    def analizar_cuentas_bancarias_individual(self, texto_buscar, criterio):
        max_attempts = 2
        attempt = 0

        while attempt < max_attempts:
            try:
                response = self.api.search_cuentas_bancarias(texto_buscar, criterio)

                time.sleep(0.3)  # igual que el usleep de PHP

                if isinstance(response, dict) and "data" in response:
                    return response

                raise Exception("Respuesta inválida del API")

            except Exception as e:
                print(f"Intento {attempt + 1} falló: {e}")
                attempt += 1
                time.sleep(0.5 * attempt)

        return {
            "success": False,
            "message": "No se pudo obtener la información bancaria. Intente nuevamente.",
        }

    # ----------------------------------------------------
    # PROCESO MASIVO
    # ----------------------------------------------------
    def analizar_cuentas_bancarias_masiva(self, file_path):
        try:
            # Detectar extensión
            extension = file_path.lower().split(".")[-1]

            if extension == "csv":
                df = pd.read_csv(file_path, dtype=str)

            elif extension == "xls":
                df = pd.read_excel(file_path, dtype=str, engine="xlrd")

            elif extension == "xlsx":
                df = pd.read_excel(file_path, dtype=str, engine="openpyxl")

            else:
                return {
                    "error": True,
                    "message": "Formato no soportado. Use CSV, XLS o XLSX.",
                }

        except Exception as e:
            return {"error": True, "message": f"Error leyendo el archivo: {e}"}

        tabla = []

        # Recorre filas (igual que Laravel)
        for index, row in df.iterrows():

            try:
                dni = str(
                    row.get("dni")
                    or row.get("DNI")
                    or row.get("NUM_DOC")
                    or row.get("num_doc")
                    or ""
                ).strip()

                cuenta_excel = str(
                    row.get("cuenta")
                    or row.get("CUENTA")
                    or row.get("NUM_CTA")
                    or row.get("num_cta")
                    or ""
                ).replace(" ", "")
            except:
                continue

            if not dni.isdigit() or len(dni) != 8:
                continue

            max_attempts = 2
            attempt = 0
            response = None

            while attempt < max_attempts:
                try:
                    # Llamada a la API
                    response = self.api.search_cuentas_bancarias(dni, 1)
                    time.sleep(0.3)

                    if isinstance(response, dict) and "data" in response:
                        break

                    raise Exception("Respuesta inválida del API")

                except Exception as e:
                    print(f"Intento falló para DNI {dni}: {e}")
                    attempt += 1
                    time.sleep(0.5 * attempt)

            estado = False

            if response and "data" in response:
                for item in response["data"]:
                    numero = str(item.get("numeroCuenta", "")).replace(" ", "")
                    if numero == cuenta_excel:
                        estado = True
                        break

            tabla.append(
                {
                    "dni": dni,
                    "cuenta": cuenta_excel,
                    "estado": estado,
                }
            )

        return tabla
