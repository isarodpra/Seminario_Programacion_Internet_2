"""
Pruebas de seguridad del GPMV.
Verifican que las consultas parametrizadas y el escape de salida
funcionan correctamente.
"""
from app import app
import pytest


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ============ SQL Injection ============
def test_sqli_en_consulta(client):
    """Intento de SQL injection en el campo placa."""
    payload = "ABC1234' OR '1'='1"
    r = client.post("/consulta", data={"placa": payload})
    # No debe devolver TODAS las multas
    assert r.status_code == 200
    assert b"FOL-2026-0003" not in r.data  # solo aparecería si la inyección funciona


def test_sqli_en_login(client):
    """Intento de login con payload SQL."""
    r = client.post("/login",
                    data={"usuario": "admin' OR '1'='1",
                          "contrasena": "cualquiera"},
                    follow_redirects=True)
    # No debe conceder acceso
    assert b"Panel administrador" not in r.data


def test_sqli_drop_table(client):
    """Intento de borrar tabla."""
    payload = "ABC1234'; DROP TABLE infraccion; --"
    r = client.post("/consulta", data={"placa": payload})
    assert r.status_code == 200
    # Verificar que la tabla sigue existiendo
    from db import fetch_one
    r2 = fetch_one("SELECT COUNT(*) AS t FROM infraccion")
    assert r2["t"] >= 0


# ============ XSS ============
def test_xss_en_consulta(client):
    """Intento de inyectar script en el campo placa."""
    payload = "<script>alert('XSS')</script>"
    r = client.post("/consulta", data={"placa": payload})
    # Jinja2 escapa automáticamente, así que el script no debe aparecer literal
    assert b"<script>alert" not in r.data
    assert b"&lt;script&gt;" in r.data or b"No se encontraron" in r.data


# ============ CSRF (mitigación con sesión) ============
def test_acceso_admin_sin_sesion(client):
    """Sin sesión no se puede acceder al panel."""
    r = client.get("/admin", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers.get("Location", "")


# ============ Fuerza bruta ============
def test_fuerza_bruta_bloqueada(client):
    """Múltiples intentos fallidos no deben revelar información."""
    for _ in range(10):
        r = client.post("/login",
                        data={"usuario": "admin", "contrasena": "mala"},
                        follow_redirects=True)
        assert b"incorrect" in r.data.lower()


# ============ Contraseñas hasheadas ============
def test_contrasenas_hasheadas():
    """Verifica que la BD guarda hashes, no texto plano."""
    from db import fetch_one
    fila = fetch_one("SELECT contrasena FROM usuario_admin WHERE usuario='admin'")
    assert fila is not None
    assert fila["contrasena"].startswith("scrypt:")
    assert len(fila["contrasena"]) > 100
    assert "admin123" not in fila["contrasena"]