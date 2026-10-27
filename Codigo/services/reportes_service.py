from db import fetch_all

def pagos_por_mes():
    return fetch_all("""
        SELECT DATE_FORMAT(fecha_pago, '%Y-%m') AS mes,
               COUNT(*) AS cantidad,
               SUM(monto_pagado) AS total
        FROM pago
        GROUP BY mes
        ORDER BY mes DESC
    """)

def multas_por_estatus():
    return fetch_all("""
        SELECT estatus, COUNT(*) AS cantidad
        FROM infraccion
        GROUP BY estatus
    """)

def resumen():
    return {
        "pagos_por_mes": pagos_por_mes(),
        "multas_por_estatus": multas_por_estatus()
    }