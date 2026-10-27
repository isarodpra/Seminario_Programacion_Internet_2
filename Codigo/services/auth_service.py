from werkzeug.security import check_password_hash
from db import fetch_one

def autenticar(usuario, contrasena):
    admin = fetch_one(
        "SELECT * FROM usuario_admin WHERE usuario = %s",
        (usuario,)
    )
    if admin and check_password_hash(admin["contrasena"], contrasena):
        return admin
    return None

def autenticar_ciudadano(identificador):
    """
    Autentica o identifica a un ciudadano mediante su Placa, RFC o Correo.
    Permite el acceso al portal ciudadano.
    """
    identificador = (identificador or "").strip()
    if not identificador:
        return None
    sql = """
        SELECT c.id_ciudadano, c.nombre, c.apellido, c.correo, c.telefono, c.rfc,
               v.placa, v.marca, v.modelo, v.anio
        FROM ciudadano c
        LEFT JOIN vehiculo v ON c.id_ciudadano = v.id_ciudadano
        WHERE UPPER(v.placa) = UPPER(%s)
           OR UPPER(c.rfc) = UPPER(%s)
           OR LOWER(c.correo) = LOWER(%s)
        LIMIT 1
    """
    return fetch_one(sql, (identificador, identificador, identificador))