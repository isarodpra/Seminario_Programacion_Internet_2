from services.pagos_service import registrar_pago
from db import fetch_one

def test_registrar_pago():
    # Usar una infracción de prueba con estatus Pendiente
    infraccion = fetch_one("SELECT id_infraccion FROM infraccion WHERE estatus='Pendiente' LIMIT 1")
    if not infraccion:
        return

    resultado = registrar_pago(infraccion["id_infraccion"], "Transferencia", 500.00)
    assert "id_pago" in resultado
    assert resultado["referencia"].startswith("REF-")