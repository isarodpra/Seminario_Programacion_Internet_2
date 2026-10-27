from db import fetch_one

def test_conexion():
    r = fetch_one("SELECT 1 AS ok")
    assert r["ok"] == 1