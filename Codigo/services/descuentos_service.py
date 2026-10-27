from db import fetch_one

def obtener_descuento(id_infraccion):
    return fetch_one("""
        SELECT porcentaje, vigencia
        FROM descuento
        WHERE id_infraccion = %s AND vigencia >= CURDATE()
    """, (id_infraccion,))

def calcular_monto_con_descuento(id_infraccion):
    inf = fetch_one("SELECT monto FROM infraccion WHERE id_infraccion = %s", (id_infraccion,))
    if not inf:
        raise ValueError("Infracción no encontrada")

    desc = obtener_descuento(id_infraccion)
    if desc:
        monto_final = float(inf["monto"]) * (1 - float(desc["porcentaje"]) / 100)
        return round(monto_final, 2), float(desc["porcentaje"])

    return float(inf["monto"]), 0