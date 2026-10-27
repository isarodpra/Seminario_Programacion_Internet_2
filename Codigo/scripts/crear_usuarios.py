from werkzeug.security import generate_password_hash
import sys
import os

# Permite importar db.py desde la carpeta Codigo/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import fetch_one, execute

# Lista de usuarios a crear
usuarios = [
    ("admin",     "admin123", "Admin"),
    ("operativo", "oper123",  "Operativo"),
]

print("=" * 60)
print("CREANDO USUARIOS ADMIN")
print("=" * 60)

for usuario, pwd, rol in usuarios:
    # 1. Verificar si ya existe
    existe = fetch_one(
        "SELECT id_admin FROM usuario_admin WHERE usuario = %s",
        (usuario,)
    )

    if existe:
        print(f"⚠️  El usuario '{usuario}' ya existe. Actualizando contraseña...")
        nuevo_hash = generate_password_hash(pwd)
        execute(
            "UPDATE usuario_admin SET contrasena = %s, rol = %s WHERE usuario = %s",
            (nuevo_hash, rol, usuario)
        )
    else:
        print(f"➕ Insertando usuario '{usuario}' con rol {rol}...")
        nuevo_hash = generate_password_hash(pwd)
        execute(
            "INSERT INTO usuario_admin (usuario, contrasena, rol) VALUES (%s, %s, %s)",
            (usuario, nuevo_hash, rol)
        )

    # 2. Verificar
    fila = fetch_one(
        "SELECT id_admin, usuario, rol, LENGTH(contrasena) AS len "
        "FROM usuario_admin WHERE usuario = %s",
        (usuario,)
    )
    print(f"   ✅ id={fila['id_admin']} | usuario={fila['usuario']} | "
          f"rol={fila['rol']} | hash_len={fila['len']}")
    print("-" * 60)

# 3. Resumen final
print("\nRESUMEN:")
todos = fetch_one("SELECT COUNT(*) AS total FROM usuario_admin")
print(f"Total de usuarios en la tabla: {todos['total']}")
print("=" * 60)