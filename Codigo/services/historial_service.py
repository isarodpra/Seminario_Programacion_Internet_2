"""
historial_service.py — Servicio de Auditoría y Registro de Cambios para GPMV CDMX.
Registra todas las acciones administrativas y operativas sobre multas, estatus y corralones.
"""
from db import fetch_all, execute

def registrar_accion(usuario, rol, accion, detalles, id_infraccion=None, folio=None, id_admin=None):
    """
    Registra una acción de auditoría en la tabla historial_admin.
    """
    sql = """
        INSERT INTO historial_admin (fecha_hora, id_admin, usuario, rol, accion, id_infraccion, folio, detalles)
        VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s)
    """
    return execute(sql, (id_admin, usuario, rol, accion, id_infraccion, folio, detalles))

def obtener_historial(filtro_accion=None, filtro_usuario=None, limite=150):
    """
    Obtiene los registros de auditoría ordenados del más reciente al más antiguo.
    """
    condiciones = []
    params = []

    if filtro_accion and filtro_accion.strip():
        condiciones.append("accion = %s")
        params.append(filtro_accion.strip())

    if filtro_usuario and filtro_usuario.strip():
        condiciones.append("usuario = %s")
        params.append(filtro_usuario.strip())

    where_clause = ""
    if condiciones:
        where_clause = "WHERE " + " AND ".join(condiciones)

    sql = f"""
        SELECT id_historial, fecha_hora, id_admin, usuario, rol, accion, id_infraccion, folio, detalles
        FROM historial_admin
        {where_clause}
        ORDER BY fecha_hora DESC, id_historial DESC
        LIMIT %s
    """
    params.append(limite)
    return fetch_all(sql, tuple(params))

def obtener_acciones_unicas():
    """
    Retorna la lista de tipos de acciones únicas registradas para poblar filtros.
    """
    filas = fetch_all("SELECT DISTINCT accion FROM historial_admin ORDER BY accion ASC")
    return [f["accion"] for f in filas] if filas else []
