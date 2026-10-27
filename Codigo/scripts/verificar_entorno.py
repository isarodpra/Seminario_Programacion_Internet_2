"""
Verifica que el entorno cumple con los requisitos mínimos.
Ejecutar en cada equipo antes de lanzar la aplicación:

    python scripts\\verificar_entorno.py
"""
import sys
import os
import platform

# ---------------------------------------------------------------
# Agregar la carpeta raíz del proyecto (Codigo/) al sys.path
# para poder importar `db`, `config`, `services`, etc.
# ---------------------------------------------------------------
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

print("=" * 60)
print("VERIFICACIÓN DE ENTORNO — GPMV CDMX")
print("=" * 60)

# 1. Python
print(f"1. Python: {sys.version}")
assert sys.version_info >= (3, 10), "Se requiere Python 3.10 o superior"

# 2. Plataforma
print(f"2. Sistema operativo: {platform.system()} {platform.release()}")

# 3. MySQL
try:
    from db import fetch_one
    r = fetch_one("SELECT VERSION() AS v")
    print(f"3. MySQL/MariaDB: {r['v']}")
except Exception as e:
    print(f"❌ Error al conectar a MySQL: {e}")
    sys.exit(1)

# 4. Base de datos
try:
    bd = fetch_one("SELECT DATABASE() AS bd")
    print(f"4. Base de datos conectada: {bd['bd']}")
    assert bd["bd"] == "gestor_multas", "Debe ser gestor_multas"
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# 5. Tablas
try:
    tablas = fetch_one("""
        SELECT COUNT(*) AS total
        FROM information_schema.tables
        WHERE table_schema = 'gestor_multas'
    """)
    print(f"5. Tablas encontradas: {tablas['total']}")
    assert tablas["total"] >= 7, "Se esperan al menos 7 tablas"
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# 6. Dependencias
try:
    import flask
    import mysql.connector
    import reportlab
    import werkzeug
    print(f"6. Flask: {flask.__version__}")
    print(f"   mysql-connector-python: {mysql.connector.__version__}")
    print(f"   reportlab: {reportlab.Version}")
    print(f"   werkzeug: {werkzeug.__version__}")
except ImportError as e:
    print(f"❌ Dependencia faltante: {e}")
    sys.exit(1)

print("\n✅ ENTORNO APTO PARA EJECUTAR GPMV")
print("=" * 60)