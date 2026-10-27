from db import fetch_all, fetch_one, execute
import datetime


def consultar_por_placa(placa):
    sql = """
        SELECT i.id_infraccion, i.folio, i.fecha, i.motivo, i.monto, i.estatus,
               v.placa, v.marca, v.modelo, v.anio,
               c.nombre AS corralon, c.direccion, c.area
        FROM infraccion i
        JOIN vehiculo v ON i.id_vehiculo = v.id_vehiculo
        LEFT JOIN corralon c ON c.id_vehiculo = v.id_vehiculo
        WHERE v.placa = %s
        ORDER BY i.fecha DESC
    """
    return fetch_all(sql, (placa,))

def consultar_por_folio(folio):
    sql = """
        SELECT i.id_infraccion, i.folio, i.fecha, i.motivo, i.monto, i.estatus,
               v.placa, v.marca, v.modelo, v.anio
        FROM infraccion i
        JOIN vehiculo v ON i.id_vehiculo = v.id_vehiculo
        WHERE i.folio = %s
    """
    return fetch_one(sql, (folio,))

def obtener_detalle(id_infraccion):
    sql = """
        SELECT i.*, v.placa, v.marca, v.modelo, v.anio,
               c.nombre AS corralon, c.direccion, c.area
        FROM infraccion i
        JOIN vehiculo v ON i.id_vehiculo = v.id_vehiculo
        LEFT JOIN corralon c ON c.id_vehiculo = v.id_vehiculo
        WHERE i.id_infraccion = %s
    """
    detalle = fetch_one(sql, (id_infraccion,))
    if detalle and detalle.get("corralon"):
        geo = obtener_info_geo_corralon(detalle["corralon"])
        detalle["latitud"] = geo["lat"]
        detalle["longitud"] = geo["lng"]
        detalle["telefono"] = geo["telefono"]
        detalle["horario"] = geo["horario"]
        detalle["zona"] = geo["zona"]
    return detalle

CORRALONES_GEO = {
    "Corralón Central": {
        "lat": 19.3734, "lng": -99.1795, "zona": "Centro",
        "telefono": "55 5242 5100", "horario": "24 horas / 365 días",
        "direccion": "Av. Insurgentes Sur 1234, Benito Juárez, CDMX",
        "capacidad": "450 vehículos", "referencia": "Cerca del Parque Hundido"
    },
    "Corralón Norte": {
        "lat": 19.4712, "lng": -99.1558, "zona": "Norte",
        "telefono": "55 5781 2933", "horario": "24 horas / 365 días",
        "direccion": "Calz. Vallejo 567, Gustavo A. Madero, CDMX",
        "capacidad": "600 vehículos", "referencia": "Eje 4 Norte y Vallejo"
    },
    "Corralón Oriente": {
        "lat": 19.4089, "lng": -99.0732, "zona": "Oriente",
        "telefono": "55 5763 8122", "horario": "24 horas / 365 días",
        "direccion": "Av. Zaragoza 890, Iztacalco, CDMX",
        "capacidad": "500 vehículos", "referencia": "Metro Agrícola Oriental"
    },
    "Corralón Poniente": {
        "lat": 19.3985, "lng": -99.2014, "zona": "Poniente",
        "telefono": "55 5277 4410", "horario": "24 horas / 365 días",
        "direccion": "Av. Observatorio 102, Miguel Hidalgo, CDMX",
        "capacidad": "350 vehículos", "referencia": "Metro Tacubaya"
    },
    "Corralón Sur": {
        "lat": 19.3015, "lng": -99.1764, "zona": "Sur",
        "telefono": "55 5652 9011", "horario": "24 horas / 365 días",
        "direccion": "Anillo Periférico Sur 4121, Tlalpan, CDMX",
        "capacidad": "550 vehículos", "referencia": "Cerca de Cuicuilco"
    }
}

def obtener_info_geo_corralon(nombre):
    for key, data in CORRALONES_GEO.items():
        if key.lower() in (nombre or "").lower() or (nombre or "").lower() in key.lower():
            return data
    # Fallback default en CDMX
    return {
        "lat": 19.4326, "lng": -99.1332, "zona": "Centro",
        "telefono": "55 5242 5100", "horario": "24 horas / 365 días",
        "direccion": "Ciudad de México",
        "capacidad": "400 vehículos", "referencia": "Oficinas de Tránsito CDMX"
    }

def obtener_todos_los_corralones():
    db_corralones = fetch_all("SELECT DISTINCT nombre, direccion, area FROM corralon")
    resultado = []
    vistos = set()
    for c in (db_corralones or []):
        nombre = c["nombre"]
        vistos.add(nombre)
        geo = obtener_info_geo_corralon(nombre)
        resultado.append({
            "nombre": nombre,
            "direccion": c.get("direccion") or geo["direccion"],
            "area": c.get("area", "A-01"),
            "lat": geo["lat"],
            "lng": geo["lng"],
            "zona": geo["zona"],
            "telefono": geo["telefono"],
            "horario": geo["horario"],
            "capacidad": geo["capacidad"],
            "referencia": geo["referencia"]
        })
    # Agregar los demás oficiales de la CDMX para un mapa completo y robusto
    for nombre, geo in CORRALONES_GEO.items():
        if not any(nombre.lower() in v.lower() for v in vistos):
            resultado.append({
                "nombre": nombre,
                "direccion": geo["direccion"],
                "area": "General",
                "lat": geo["lat"],
                "lng": geo["lng"],
                "zona": geo["zona"],
                "telefono": geo["telefono"],
                "horario": geo["horario"],
                "capacidad": geo["capacidad"],
                "referencia": geo["referencia"]
            })
    return resultado


def generar_siguiente_folio():
    """Genera un folio oficial consecutivo único con formato FOL-YYYY-XXXX."""
    anio = datetime.datetime.now().year
    ultimo = fetch_one("SELECT MAX(id_infraccion) AS max_id FROM infraccion")
    next_num = (ultimo["max_id"] or 0) + 1
    return f"FOL-{anio}-{next_num:04d}"


def obtener_o_crear_vehiculo(placa, marca=None, modelo=None, anio=None):
    """Busca un vehículo por placa o lo registra automáticamente."""
    placa = (placa or "").strip().upper()
    if not placa:
        raise ValueError("La placa vehicular es obligatoria")
    v = fetch_one("SELECT * FROM vehiculo WHERE UPPER(placa) = %s", (placa,))
    if v:
        return v["id_vehiculo"]
    id_v = execute("""
        INSERT INTO vehiculo (placa, marca, modelo, anio)
        VALUES (%s, %s, %s, %s)
    """, (placa, (marca or "No especificada").strip(), (modelo or "General").strip(), anio or 2022))
    return id_v


def crear_multa(placa, motivo, monto, fecha=None, folio=None, estatus="Pendiente",
                remitir_corralon=False, nombre_corralon=None, direccion_corralon=None, area_corralon=None,
                marca=None, modelo=None, anio=None):
    """
    Crea una nueva multa para un vehículo.
    Permite simular el traslado o retención a un corralón si remitir_corralon es True.
    """
    id_vehiculo = obtener_o_crear_vehiculo(placa, marca, modelo, anio)
    
    if not folio or not folio.strip():
        folio = generar_siguiente_folio()
    else:
        folio = folio.strip().upper()
        # Verificar si el folio ya existe
        existente = fetch_one("SELECT id_infraccion FROM infraccion WHERE folio = %s", (folio,))
        if existente:
            folio = generar_siguiente_folio()

    if not fecha:
        fecha = datetime.date.today().strftime("%Y-%m-%d")

    monto = float(monto)
    id_infraccion = execute("""
        INSERT INTO infraccion (folio, fecha, motivo, monto, estatus, id_vehiculo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (folio, fecha, motivo.strip(), monto, estatus, id_vehiculo))

    # Manejo del depósito / corralón
    if remitir_corralon and nombre_corralon:
        geo = obtener_info_geo_corralon(nombre_corralon)
        dir_final = (direccion_corralon or geo.get("direccion", "Ciudad de México")).strip()
        area_final = (area_corralon or "A-01").strip().upper()

        existente_corr = fetch_one("SELECT id_corralon FROM corralon WHERE id_vehiculo = %s", (id_vehiculo,))
        if existente_corr:
            execute("""
                UPDATE corralon SET nombre = %s, direccion = %s, area = %s WHERE id_corralon = %s
            """, (nombre_corralon, dir_final, area_final, existente_corr["id_corralon"]))
        else:
            execute("""
                INSERT INTO corralon (nombre, direccion, area, id_vehiculo)
                VALUES (%s, %s, %s, %s)
            """, (nombre_corralon, dir_final, area_final, id_vehiculo))

    return {"id_infraccion": id_infraccion, "folio": folio, "id_vehiculo": id_vehiculo}


def actualizar_multa_admin(id_infraccion, folio, fecha, motivo, monto, estatus,
                           remitir_corralon=False, nombre_corralon=None, direccion_corralon=None, area_corralon=None):
    """
    Función exclusiva de Admin Principal:
    Permite modificar cualquier dato de la multa, estatus y ubicación física en corralón.
    """
    inf = obtener_detalle(id_infraccion)
    if not inf:
        raise ValueError("Infracción no encontrada")

    id_vehiculo = inf["id_vehiculo"]

    execute("""
        UPDATE infraccion
        SET folio = %s, fecha = %s, motivo = %s, monto = %s, estatus = %s
        WHERE id_infraccion = %s
    """, (folio.strip().upper(), fecha, motivo.strip(), float(monto), estatus, id_infraccion))

    # Actualizar o retirar del corralón
    if remitir_corralon and nombre_corralon:
        geo = obtener_info_geo_corralon(nombre_corralon)
        dir_final = (direccion_corralon or geo.get("direccion", "Ciudad de México")).strip()
        area_final = (area_corralon or "A-01").strip().upper()

        existente = fetch_one("SELECT id_corralon FROM corralon WHERE id_vehiculo = %s", (id_vehiculo,))
        if existente:
            execute("""
                UPDATE corralon SET nombre = %s, direccion = %s, area = %s WHERE id_corralon = %s
            """, (nombre_corralon, dir_final, area_final, existente["id_corralon"]))
        else:
            execute("""
                INSERT INTO corralon (nombre, direccion, area, id_vehiculo)
                VALUES (%s, %s, %s, %s)
            """, (nombre_corralon, dir_final, area_final, id_vehiculo))
    else:
        # Si se desmarca la remisión a corralón, se retira el vehículo del corralón
        execute("DELETE FROM corralon WHERE id_vehiculo = %s", (id_vehiculo,))

    return inf


def actualizar_ubicacion_operativo(id_infraccion, remitir_corralon, nombre_corralon=None,
                                   direccion_corralon=None, area_corralon=None):
    """
    Función exclusiva de Operativo:
    Únicamente permite actualizar el estado de traslado/detención y la ubicación del vehículo (corralón y área).
    NO puede modificar monto, motivo ni folio.
    """
    inf = obtener_detalle(id_infraccion)
    if not inf:
        raise ValueError("Infracción no encontrada")

    id_vehiculo = inf["id_vehiculo"]

    if remitir_corralon and nombre_corralon:
        geo = obtener_info_geo_corralon(nombre_corralon)
        dir_final = (direccion_corralon or geo.get("direccion", "Ciudad de México")).strip()
        area_final = (area_corralon or "A-01").strip().upper()

        existente = fetch_one("SELECT id_corralon FROM corralon WHERE id_vehiculo = %s", (id_vehiculo,))
        if existente:
            execute("""
                UPDATE corralon SET nombre = %s, direccion = %s, area = %s WHERE id_corralon = %s
            """, (nombre_corralon, dir_final, area_final, existente["id_corralon"]))
        else:
            execute("""
                INSERT INTO corralon (nombre, direccion, area, id_vehiculo)
                VALUES (%s, %s, %s, %s)
            """, (nombre_corralon, dir_final, area_final, id_vehiculo))
    else:
        execute("DELETE FROM corralon WHERE id_vehiculo = %s", (id_vehiculo,))

    return inf


def eliminar_multa(id_infraccion):
    """
    Función exclusiva de Admin Principal:
    Elimina una multa del sistema y actualiza el corralón si ya no quedan multas pendientes.
    """
    inf = obtener_detalle(id_infraccion)
    if not inf:
        raise ValueError("Infracción no encontrada")

    id_vehiculo = inf["id_vehiculo"]
    execute("DELETE FROM infraccion WHERE id_infraccion = %s", (id_infraccion,))

    # Si ya no tiene multas restantes, retirar de corralón
    restantes = fetch_one("SELECT COUNT(*) AS total FROM infraccion WHERE id_vehiculo = %s", (id_vehiculo,))
    if restantes and restantes["total"] == 0:
        execute("DELETE FROM corralon WHERE id_vehiculo = %s", (id_vehiculo,))

    return inf
