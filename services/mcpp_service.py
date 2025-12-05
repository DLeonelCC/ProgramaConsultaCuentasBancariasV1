import requests
import time


class McppApiService:
    def __init__(self):
        self.base_url = "https://apps4.mineco.gob.pe/dggfrhapp/privado/planilla/"
        self.session = requests.Session()
        self.cookies_cache = None
        self.cookies_timestamp = 0
        self.cache_ttl = 3000  # Igual que en tu Laravel (en segundos)

    # -----------------------------------------------------
    # LOGIN Y COOKIES
    # -----------------------------------------------------
    def get_session_cookies(self):
        if self.cookies_cache and (
            time.time() - self.cookies_timestamp < self.cache_ttl
        ):
            return self.cookies_cache

        login_url = "https://apps4.mineco.gob.pe/dggfrhapp/j_spring_security_check"
        payload = {
            "j_username": "43053748",
            "j_password": "Cartagena070685",
            "nroIntentos": 1,
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://apps4.mineco.gob.pe/dggfrhapp/",
            "Origin": "https://apps4.mineco.gob.pe",
        }

        # 1. HACER LOGIN CAPTURANDO REDIRECTS
        response = self.session.post(
            login_url, data=payload, headers=headers, allow_redirects=True
        )

        # 2. CAPTURAR TODAS LAS COOKIES DEL SESSION
        cookies_dict = self.session.cookies.get_dict()  # <--- ESTA ES LA CLAVE

        if "JSESSIONID" not in cookies_dict:
            raise Exception("No se encontró JSESSIONID en las cookies del session.")

        # Armar string como navegador
        cookies_string = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])

        # Guardar en caché
        self.cookies_cache = cookies_string
        self.cookies_timestamp = time.time()

        return cookies_string

    # -----------------------------------------------------
    # REQUEST CON HEADERS
    # -----------------------------------------------------
    def request_headers(self):
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://apps4.mineco.gob.pe/dggfrhapp/",
            "Origin": "https://apps4.mineco.gob.pe",
            "Cookie": self.get_session_cookies(),
        }

    # -----------------------------------------------------
    # MÉTODO PRINCIPAL — BUSCAR CUENTAS BANCARIAS
    # -----------------------------------------------------
    def search_cuentas_bancarias(self, texto_buscar, criterio):
        url = self.base_url + "consultas/cuentasBancoNacion/getAllCuentasBancoNacion"

        data = {
            "draw": 2,
            "start": 0,
            "length": 50,
            "columns": [
                {
                    "data": "numeroCuenta",
                    "name": "",
                    "searchable": "false",
                    "orderable": "false",
                    "search": {"value": "", "regex": "false"},
                },
                {
                    "data": "desTipoDocumento",
                    "name": "",
                    "searchable": "false",
                    "orderable": "false",
                    "search": {"value": "", "regex": "false"},
                },
                {
                    "data": "numeroDocumento",
                    "name": "",
                    "searchable": "false",
                    "orderable": "false",
                    "search": {"value": "", "regex": "false"},
                },
                {
                    "data": "desEsato",
                    "name": "",
                    "searchable": "false",
                    "orderable": "false",
                    "search": {"value": "", "regex": "false"},
                },
                {
                    "data": "desCondicion",
                    "name": "",
                    "searchable": "false",
                    "orderable": "false",
                    "search": {"value": "", "regex": "false"},
                },
                {
                    "data": "fechaModificacion",
                    "name": "",
                    "searchable": "false",
                    "orderable": "false",
                    "search": {"value": "", "regex": "false"},
                },
            ],
            "search": {"value": "", "regex": "false"},
            "criterio": criterio,
            "textoBuscar": texto_buscar,
            "buscarGrilla": 0,
        }

        response = self.session.post(
            url, data=data, headers=self.request_headers(), timeout=60
        )

        if response.status_code != 200:
            return {
                "error": True,
                "status": response.status_code,
                "message": "Error en API",
                "body": response.text,
            }

        return response.json()
