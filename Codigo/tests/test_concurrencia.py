"""
Verifica que dos pagos simultáneos sobre la misma multa
solo generen UN registro en la tabla `pago`.
"""
import threading
from db import fetch_one, execute
from services.pagos_service import registrar_pago


def preparar_infraccion_pendiente():
    """Resetea una infracción para la prueba."""
    execute("DELETE FROM pago WHERE id_infraccion = 2")
    execute("UPDATE infraccion SET estatus='Pendiente' WHERE id_infraccion = 2")


def test_pago_concurrente():
    preparar_infraccion_pendiente()

    resultados = []
    errores = []

    def intentar_pago():
        try:
            r = registrar_pago(2, "Transferencia", 800.00)
            resultados.append(r)
        except Exception as e:
            errores.append(str(e))

    hilos = [threading.Thread(target=intentar_pago) for _ in range(5)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    # Solo uno debe haber tenido éxito
    assert len(resultados) == 1, f"Se esperaba 1 pago exitoso, hubo {len(resultados)}"
    assert len(errores) == 4, f"Se esperaban 4 fallos, hubo {len(errores)}"

    # Verificar en la BD
    pagos = fetch_one(
        "SELECT COUNT(*) AS total FROM pago WHERE id_infraccion = 2"
    )
    assert pagos["total"] == 1, "Solo debe haber 1 pago registrado"
    print("✅ Condición de carrera evitada correctamente")