"""
Pruebas de aceptación basadas en las historias de usuario.
Cada test corresponde a un criterio Given/When/Then.
"""
import pytest
from app import app
from db import fetch_one
import services.multas_service as multas_service
import services.auth_service as auth_service


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------- HU-01: Consultar multas por placa ----------
def test_hu01_consulta_por_placa(client):
    r = client.post("/consulta", data={"placa": "ABC1234"})
    assert r.status_code == 200
    assert b"FOL-2026-0001" in r.data
    assert b"FOL-2026-0002" in r.data


# ---------- HU-05: Estatus actualizado ----------
def test_hu05_estatus_visible(client):
    r = client.post("/consulta", data={"placa": "ABC1234"})
    assert b"Pendiente" in r.data


# ---------- HU-06: Login de administrador ----------
def test_hu06_login_admin(client):
    r = client.post("/login", data={"usuario": "admin", "contrasena": "admin123"},
                    follow_redirects=True)
    assert r.status_code == 200
    assert b"Panel administrador" in r.data


def test_hu06_login_credenciales_invalidas(client):
    r = client.post("/login", data={"usuario": "admin", "contrasena": "mala"},
                    follow_redirects=True)
    assert b"incorrectos" in r.data.lower() or b"incorrectas" in r.data.lower()


# ---------- HU-07: Listar multas (requiere login) ----------
def test_hu07_listar_multas_admin(client):
    with client.session_transaction() as sess:
        sess["admin"] = {"id_admin": 1, "usuario": "admin", "rol": "Admin"}
    r = client.get("/admin/multas")
    assert r.status_code == 200
    assert b"FOL-2026-0001" in r.data


# ---------- HU-08: Descuento por pronto pago ----------
def test_hu08_descuento_aplicado():
    from services.descuentos_service import calcular_monto_con_descuento
    monto, desc = calcular_monto_con_descuento(1)
    assert desc > 0
    assert monto < 1200.00


# ---------- HU-09: Reportes ----------
def test_hu09_reportes(client):
    with client.session_transaction() as sess:
        sess["admin"] = {"id_admin": 1, "usuario": "admin", "rol": "Admin"}
    r = client.get("/admin/reportes")
    assert r.status_code == 200
    assert b"Reportes" in r.data


# ---------- HU-03: Corralón visible ----------
def test_hu03_corralon_en_detalle(client):
    r = client.get("/detalle/1")
    assert b"Corral" in r.data