"""
Pruebas de carga con Locust.
Ejecutar con:
    locust -f tests/locustfile.py --host=http://127.0.0.1:5000
"""
import random
from locust import HttpUser, task, between

PLACAS = ["ABC1234", "XYZ5678", "QWE9012"]
FOLIOS = ["FOL-2026-0001", "FOL-2026-0002", "FOL-2026-0003", "FOL-2026-0004"]


class CiudadanoUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def consultar_multas(self):
        placa = random.choice(PLACAS)
        with self.client.post("/consulta", data={"placa": placa},
                              catch_response=True) as r:
            if r.status_code == 200 and "FOL-" in r.text:
                r.success()
            else:
                r.failure("Consulta no devolvió multas")

    @task(2)
    def ver_detalle(self):
        id_inf = random.randint(1, 4)
        self.client.get(f"/detalle/{id_inf}")

    @task(1)
    def ver_login(self):
        self.client.get("/login")


class AdminUser(HttpUser):
    wait_time = between(2, 5)

    def on_start(self):
        """Login inicial del admin."""
        self.client.post("/login",
                         data={"usuario": "admin", "contrasena": "admin123"})

    @task(2)
    def panel_admin(self):
        self.client.get("/admin")

    @task(1)
    def reportes(self):
        self.client.get("/admin/reportes")

    @task(1)
    def listar_multas(self):
        self.client.get("/admin/multas")