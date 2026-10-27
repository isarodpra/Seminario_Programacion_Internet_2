from datetime import datetime
import uuid
from db import get_connection, fetch_one

def registrar_pago(id_infraccion, metodo_pago, monto_pagado):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id_infraccion, estatus, monto, id_vehiculo
            FROM infraccion
            WHERE id_infraccion = %s
            FOR UPDATE
        """, (id_infraccion,))
        inf = cursor.fetchone()

        if not inf:
            raise ValueError("La infracción no existe")
        if inf["estatus"] != "Pendiente":
            raise ValueError("La multa no está pendiente")

        referencia = f"REF-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        cursor.execute("""
            INSERT INTO pago (fecha_pago, monto_pagado, metodo_pago, referencia, id_infraccion)
            VALUES (NOW(), %s, %s, %s, %s)
        """, (monto_pagado, metodo_pago, referencia, id_infraccion))

        id_pago = cursor.lastrowid

        cursor.execute("""
            UPDATE infraccion SET estatus = 'Pagada'
            WHERE id_infraccion = %s
        """, (id_infraccion,))

        # Liberar vehículo si ya no tiene multas pendientes
        cursor.execute("""
            SELECT COUNT(*) AS pendientes
            FROM infraccion
            WHERE id_vehiculo = %s AND estatus = 'Pendiente'
        """, (inf["id_vehiculo"],))
        pendientes = cursor.fetchone()["pendientes"]

        if pendientes == 0:
            cursor.execute("""
                UPDATE infraccion SET estatus = 'Liberada'
                WHERE id_vehiculo = %s
            """, (inf["id_vehiculo"],))

        conn.commit()
        return {"id_pago": id_pago, "referencia": referencia}

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()