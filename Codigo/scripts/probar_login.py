from werkzeug.security import check_password_hash
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import fetch_one, fetch_all

print("=" * 60)
print("DIAGNÓSTICO DE LOGIN")
print("=" * 60)

# 1. ¿A qué BD está conectado Python?
bd = fetch_one("SELECT DATABASE() AS bd")
print(f"1. Base de datos conectada: {bd['bd']}")

# 2. ¿Cuántos usuarios hay?
total = fetch_one("SELECT COUNT(*) AS total FROM usuario_admin")
print(f"2. Usuarios en la tabla: {total['total']}")

# 3. Listar usuarios
print("3. Usuarios registrados:")
usuarios = fetch_all("SELECT id_admin, usuario, rol, LENGTH(contrasena) AS len FROM usuario_admin")
for u in usuarios:
    print(f"   - id={u['id_admin']} | usuario='{u['usuario']}' | rol={u['rol']} | hash_len={u['len']}")

# 4. Buscar admin
print("4. Buscando 'admin':")
fila = fetch_one("SELECT * FROM usuario_admin WHERE usuario = %s", ("admin",))
if fila:
    print(f"   ✅ Encontrado. Rol: {fila['rol']}")
    ok = check_password_hash(fila["contrasena"], "admin123")
    print(f"   ¿Contraseña 'admin123' válida? → {'✅ SÍ' if ok else '❌ NO'}")
else:
    print("   ❌ NO encontrado")

print("=" * 60)