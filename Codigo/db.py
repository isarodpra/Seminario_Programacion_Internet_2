import mysql.connector
from mysql.connector import pooling
from config import Config

pool = pooling.MySQLConnectionPool(
    pool_name="gpmv_pool",
    pool_size=5,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME,
    autocommit=False
)

def get_connection():
    return pool.get_connection()

def fetch_one(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def fetch_all(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def execute(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

def init_db():
    try:
        execute("""
            CREATE TABLE IF NOT EXISTS historial_admin (
                id_historial INT AUTO_INCREMENT PRIMARY KEY,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                id_admin INT NULL,
                usuario VARCHAR(50) NOT NULL,
                rol VARCHAR(30) NOT NULL,
                accion VARCHAR(50) NOT NULL,
                id_infraccion INT NULL,
                folio VARCHAR(50) NULL,
                detalles TEXT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """)
    except Exception:
        pass

init_db()


