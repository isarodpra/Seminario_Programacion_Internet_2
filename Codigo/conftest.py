"""
conftest.py — Configuración global de Pytest para GPMV.
Se ejecuta automáticamente ANTES de recolectar los tests.
Agrega la carpeta raíz (Codigo/) al sys.path para que los tests
puedan importar `app`, `db`, `config`, `services`, etc.
"""
import sys
import os

RAIZ = os.path.abspath(os.path.dirname(__file__))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import pytest

@pytest.fixture(autouse=True)
def _ensure_test_state():
    try:
        from db import execute
        execute("UPDATE infraccion SET estatus='Pendiente' WHERE id_infraccion = 1")
    except Exception:
        pass
    yield