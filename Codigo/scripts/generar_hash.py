from werkzeug.security import generate_password_hash

usuarios = [
    ("admin",     "admin123"),
    ("operativo", "oper123"),
]

for usuario, pwd in usuarios:
    hash_pwd = generate_password_hash(pwd)
    print(f"Usuario: {usuario}")
    print(f"Contraseña original: {pwd}")
    print(f"Hash: {hash_pwd}")
    print("-" * 60)