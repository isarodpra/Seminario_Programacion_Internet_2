from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_file, jsonify
)
from config import Config
from db import fetch_one, fetch_all

import services.auth_service as auth_service
import services.multas_service as multas_service
import services.pagos_service as pagos_service
import services.descuentos_service as descuentos_service
import services.pdf_service as pdf_service
import services.reportes_service as reportes_service
import services.historial_service as historial_service


app = Flask(__name__)
app.config.from_object(Config)   # Carga SECRET_KEY y datos de BD


# ============================================================
# 3.4 — Backend: consulta de multas por placa o folio
# ============================================================
@app.route("/consulta", methods=["GET", "POST"])
def consulta():
    """
    Actividad 3.4: Consulta de multas por placa.
    También permite buscar por folio si se prefiere.
    """
    multas = []
    if request.method == "POST":
        placa = request.form.get("placa", "").strip().upper()
        if placa:
            multas = multas_service.consultar_por_placa(placa)
    return render_template("consulta.html", multas=multas)


@app.route("/detalle/<int:id_infraccion>")
def detalle(id_infraccion):
    """Muestra el detalle completo de una multa."""
    inf = multas_service.obtener_detalle(id_infraccion)
    return render_template("detalle.html", detalle=inf)


# ============================================================
# 3.3 — Autenticación (Ciudadano y Administrador)
# ============================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    tab = request.args.get("tab", "ciudadano")
    if request.method == "POST":
        # Distinguir entre inicio de sesión ciudadano o administrador
        if "identificador" in request.form and request.form.get("tipo") == "ciudadano":
            tab = "ciudadano"
            identificador = request.form.get("identificador", "").strip()
            ciudadano = auth_service.autenticar_ciudadano(identificador)
            if ciudadano:
                session["ciudadano"] = ciudadano
                flash(f"Bienvenido(a), {ciudadano['nombre']} {ciudadano['apellido']}")
                return redirect(url_for("inicio"))
            flash("No se encontró ningún registro para la placa, RFC o correo ingresado.")
        else:
            tab = "admin"
            usuario = request.form.get("usuario", "")
            contrasena = request.form.get("contrasena", "")
            admin = auth_service.autenticar(usuario, contrasena)
            if admin:
                session["admin"] = admin
                return redirect(url_for("admin_panel"))
            flash("Credenciales incorrectas")
    return render_template("login.html", tab=tab)


@app.route("/logout")
def logout():
    session.pop("admin", None)
    session.pop("ciudadano", None)
    return redirect(url_for("login"))



# ============================================================
# 3.7 y 3.9 — Pago de multa y formulario
# ============================================================
@app.route("/pagar/<int:id_infraccion>", methods=["GET", "POST"])
def pagar(id_infraccion):
    detalle = multas_service.obtener_detalle(id_infraccion)
    if not detalle:
        flash("La infracción solicitada no existe.")
        return redirect(url_for("consulta"))

    if detalle.get("estatus") != "Pendiente":
        pago_existente = fetch_one("SELECT id_pago FROM pago WHERE id_infraccion = %s ORDER BY id_pago DESC LIMIT 1", (id_infraccion,))
        if pago_existente:
            flash("Esta infracción ya fue liquidada con anterioridad. Mostrando comprobante oficial.")
            return redirect(url_for("comprobante", id_pago=pago_existente["id_pago"]))
        flash(f"La infracción no se encuentra pendiente de pago (Estatus actual: {detalle.get('estatus')}).")
        return redirect(url_for("detalle", id_infraccion=id_infraccion))

    if request.method == "POST":
        metodo = request.form["metodo_pago"]
        monto = float(request.form["monto"])
        resultado = pagos_service.registrar_pago(id_infraccion, metodo, monto)
        return redirect(url_for("comprobante", id_pago=resultado["id_pago"]))

    monto_final, desc = descuentos_service.calcular_monto_con_descuento(id_infraccion)
    return render_template(
        "pago.html",
        detalle=detalle,
        monto_final=monto_final,
        descuento=desc
    )


# ============================================================
# 3.8 y 3.9 — Generación y descarga de comprobante PDF
# ============================================================
@app.route("/comprobante/<int:id_pago>")
def comprobante(id_pago):
    pago = fetch_one("SELECT * FROM pago WHERE id_pago = %s", (id_pago,))
    if not pago:
        return "Pago no encontrado", 404

    inf = fetch_one("SELECT * FROM infraccion WHERE id_infraccion = %s", (pago["id_infraccion"],))
    veh = fetch_one("SELECT * FROM vehiculo WHERE id_vehiculo = %s", (inf["id_vehiculo"],))
    ciu = fetch_one("SELECT * FROM ciudadano WHERE id_ciudadano = %s", (veh["id_ciudadano"],))

    if request.args.get("pdf") == "1" or request.args.get("formato") == "pdf" or request.args.get("descargar") == "1":
        pdf = pdf_service.generar_comprobante_pdf(pago, inf, veh, ciu)
        return send_file(
            pdf,
            as_attachment=True,
            download_name=f"comprobante_{pago['referencia']}.pdf",
            mimetype="application/pdf"
        )

    corralon = None
    if inf.get("id_vehiculo"):
        corralon = fetch_one("SELECT * FROM corralon WHERE id_vehiculo = %s", (inf["id_vehiculo"],))

    return render_template(
        "comprobante.html",
        pago=pago,
        infraccion=inf,
        vehiculo=veh,
        ciudadano=ciu,
        corralon=corralon,
        pago_id=id_pago
    )


@app.route("/comprobante/<int:id_pago>/pdf")
def comprobante_pdf(id_pago):
    pago = fetch_one("SELECT * FROM pago WHERE id_pago = %s", (id_pago,))
    if not pago:
        return "Pago no encontrado", 404

    inf = fetch_one("SELECT * FROM infraccion WHERE id_infraccion = %s", (pago["id_infraccion"],))
    veh = fetch_one("SELECT * FROM vehiculo WHERE id_vehiculo = %s", (inf["id_vehiculo"],))
    ciu = fetch_one("SELECT * FROM ciudadano WHERE id_ciudadano = %s", (veh["id_ciudadano"],))

    pdf = pdf_service.generar_comprobante_pdf(pago, inf, veh, ciu)
    return send_file(
        pdf,
        as_attachment=True,
        download_name=f"comprobante_{pago['referencia']}.pdf",
        mimetype="application/pdf"
    )


# ============================================================
# 3.12 y 3.13 — Panel administrador y reportes
# ============================================================
@app.route("/admin")
def admin_panel():
    if "admin" not in session:
        return redirect(url_for("login"))
    reportes = reportes_service.resumen()
    return render_template("admin/panel.html", reportes=reportes)


@app.route("/admin/multas")
def admin_multas():
    if "admin" not in session:
        return redirect(url_for("login"))
    multas = fetch_all("""
        SELECT i.id_infraccion, i.folio, i.fecha, i.motivo, i.monto, i.estatus, v.placa,
               c.nombre AS corralon, c.area
        FROM infraccion i
        JOIN vehiculo v ON i.id_vehiculo = v.id_vehiculo
        LEFT JOIN corralon c ON c.id_vehiculo = v.id_vehiculo
        ORDER BY i.fecha DESC
    """)
    return render_template("admin/multas.html", multas=multas)


# ============================================================
# Registro de Multas (Operativo y Admin Principal)
# ============================================================
@app.route("/admin/multas/nueva", methods=["GET", "POST"])
def admin_nueva_multa():
    if "admin" not in session:
        return redirect(url_for("login"))

    corralones = multas_service.CORRALONES_GEO

    if request.method == "POST":
        placa = request.form.get("placa", "").strip().upper()
        motivo = request.form.get("motivo", "").strip()
        monto = request.form.get("monto", "0")
        fecha = request.form.get("fecha")
        folio = request.form.get("folio", "").strip().upper()
        estatus = request.form.get("estatus", "Pendiente")
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        anio = request.form.get("anio")

        remitir_corralon = request.form.get("remitir_corralon") == "1"
        nombre_corralon = request.form.get("nombre_corralon")
        direccion_corralon = request.form.get("direccion_corralon")
        area_corralon = request.form.get("area_corralon")

        try:
            res = multas_service.crear_multa(
                placa=placa,
                motivo=motivo,
                monto=monto,
                fecha=fecha,
                folio=folio,
                estatus=estatus,
                remitir_corralon=remitir_corralon,
                nombre_corralon=nombre_corralon,
                direccion_corralon=direccion_corralon,
                area_corralon=area_corralon,
                marca=marca,
                modelo=modelo,
                anio=int(anio) if anio else None
            )

            # Registrar en Historial de Auditoría
            usuario = session["admin"]["usuario"]
            rol = session["admin"]["rol"]
            accion = "CREAR_MULTA_ADMIN" if rol == "Admin" else "CREAR_MULTA_OPERATIVO"
            traslado_msg = f"Remitido a {nombre_corralon} (Área: {area_corralon})" if remitir_corralon else "Sin retención en corralón"
            detalles = f"Registro de nueva multa folio {res['folio']} para placa {placa} por ${float(monto):.2f}. Motivo: '{motivo}'. Traslado: {traslado_msg}."

            historial_service.registrar_accion(
                usuario=usuario,
                rol=rol,
                accion=accion,
                detalles=detalles,
                id_infraccion=res["id_infraccion"],
                folio=res["folio"],
                id_admin=session["admin"].get("id_admin")
            )

            flash(f"Multa {res['folio']} registrada exitosamente.")
            return redirect(url_for("admin_multas"))
        except Exception as e:
            flash(f"Error al registrar multa: {str(e)}")

    return render_template("admin/nueva_multa.html", corralones=corralones)


# ============================================================
# Admin Principal: Modificar cualquier dato de la multa
# ============================================================
@app.route("/admin/multas/editar/<int:id_infraccion>", methods=["GET", "POST"])
def admin_editar_multa(id_infraccion):
    if "admin" not in session:
        return redirect(url_for("login"))

    # Validación de rol: Solo Admin Principal puede editar todos los campos
    if session["admin"]["rol"] != "Admin":
        flash("Acceso restringido: Solo el Administrador Principal puede editar los datos legales de las multas.")
        return redirect(url_for("admin_multas"))

    detalle = multas_service.obtener_detalle(id_infraccion)
    if not detalle:
        flash("Infracción no encontrada.")
        return redirect(url_for("admin_multas"))

    corralones = multas_service.CORRALONES_GEO

    if request.method == "POST":
        folio = request.form.get("folio", "").strip().upper()
        fecha = request.form.get("fecha")
        motivo = request.form.get("motivo", "").strip()
        monto = request.form.get("monto", "0")
        estatus = request.form.get("estatus", "Pendiente")

        remitir_corralon = request.form.get("remitir_corralon") == "1"
        nombre_corralon = request.form.get("nombre_corralon")
        direccion_corralon = request.form.get("direccion_corralon")
        area_corralon = request.form.get("area_corralon")

        try:
            # Detectar cambios para la auditoría detallada
            cambios = []
            if detalle["folio"] != folio:
                cambios.append(f"Folio: {detalle['folio']} ➔ {folio}")
            if str(detalle["fecha"]) != str(fecha):
                cambios.append(f"Fecha: {detalle['fecha']} ➔ {fecha}")
            if detalle["motivo"] != motivo:
                cambios.append(f"Motivo modificado")
            if float(detalle["monto"]) != float(monto):
                cambios.append(f"Monto: ${float(detalle['monto']):.2f} ➔ ${float(monto):.2f}")
            if detalle["estatus"] != estatus:
                cambios.append(f"Estatus: {detalle['estatus']} ➔ {estatus}")

            corralon_anterior = detalle.get("corralon") or "Sin corralón"
            corralon_nuevo = nombre_corralon if remitir_corralon else "Sin corralón"
            if corralon_anterior != corralon_nuevo:
                cambios.append(f"Ubicación: {corralon_anterior} ➔ {corralon_nuevo}")

            multas_service.actualizar_multa_admin(
                id_infraccion=id_infraccion,
                folio=folio,
                fecha=fecha,
                motivo=motivo,
                monto=monto,
                estatus=estatus,
                remitir_corralon=remitir_corralon,
                nombre_corralon=nombre_corralon,
                direccion_corralon=direccion_corralon,
                area_corralon=area_corralon
            )

            # Registrar en el Historial de Auditoría
            desc_cambios = "; ".join(cambios) if cambios else "Sin cambios en los campos clave"
            detalles = f"Admin modificó la multa folio {folio} (Placa: {detalle['placa']}). Cambios realizados: {desc_cambios}."
            historial_service.registrar_accion(
                usuario=session["admin"]["usuario"],
                rol="Admin",
                accion="EDITAR_MULTA_ADMIN",
                detalles=detalles,
                id_infraccion=id_infraccion,
                folio=folio,
                id_admin=session["admin"].get("id_admin")
            )

            flash(f"Multa {folio} actualizada con éxito y registrada en el historial.")
            return redirect(url_for("admin_multas"))
        except Exception as e:
            flash(f"Error al actualizar multa: {str(e)}")

    return render_template("admin/editar_multa.html", detalle=detalle, corralones=corralones)


# ============================================================
# Admin Principal: Eliminar multa con registro en historial
# ============================================================
@app.route("/admin/multas/eliminar/<int:id_infraccion>", methods=["POST"])
def admin_eliminar_multa(id_infraccion):
    if "admin" not in session:
        return redirect(url_for("login"))

    # Validación de rol: Solo Admin Principal
    if session["admin"]["rol"] != "Admin":
        flash("Acceso restringido: Solo el Administrador Principal puede eliminar multas.")
        return redirect(url_for("admin_multas"))

    try:
        inf = multas_service.eliminar_multa(id_infraccion)

        # Registro en Auditoría
        detalles = f"Admin eliminó definitivamente la multa folio {inf['folio']} (Placa: {inf['placa']}, Monto: ${float(inf['monto']):.2f}, Motivo: '{inf['motivo']}')."
        historial_service.registrar_accion(
            usuario=session["admin"]["usuario"],
            rol="Admin",
            accion="ELIMINAR_MULTA_ADMIN",
            detalles=detalles,
            id_infraccion=id_infraccion,
            folio=inf["folio"],
            id_admin=session["admin"].get("id_admin")
        )

        flash(f"Multa {inf['folio']} eliminada exitosamente y registrada en el historial de auditoría.")
    except Exception as e:
        flash(f"Error al eliminar multa: {str(e)}")

    return redirect(url_for("admin_multas"))


# ============================================================
# Operativo: Actualizar únicamente retención y ubicación en corralón
# ============================================================
@app.route("/operativo/ubicacion/<int:id_infraccion>", methods=["GET", "POST"])
def operativo_ubicacion(id_infraccion):
    if "admin" not in session:
        return redirect(url_for("login"))

    detalle = multas_service.obtener_detalle(id_infraccion)
    if not detalle:
        flash("Infracción no encontrada.")
        return redirect(url_for("admin_multas"))

    corralones = multas_service.CORRALONES_GEO

    if request.method == "POST":
        remitir_corralon = request.form.get("remitir_corralon") == "1"
        nombre_corralon = request.form.get("nombre_corralon")
        direccion_corralon = request.form.get("direccion_corralon")
        area_corralon = request.form.get("area_corralon")
        estado_detencion = request.form.get("estado_detencion", "En resguardo")

        try:
            multas_service.actualizar_ubicacion_operativo(
                id_infraccion=id_infraccion,
                remitir_corralon=remitir_corralon,
                nombre_corralon=nombre_corralon,
                direccion_corralon=direccion_corralon,
                area_corralon=area_corralon
            )

            # Registrar en Historial
            usuario = session["admin"]["usuario"]
            rol = session["admin"]["rol"]
            loc_msg = f"Ingresado en {nombre_corralon} (Área: {area_corralon}) - Estado: {estado_detencion}" if remitir_corralon else "Vehículo retirado / sin retención en corralón"
            detalles = f"{rol} ({usuario}) actualizó ubicación/detención de vehículo {detalle['placa']} (Folio {detalle['folio']}): {loc_msg}."

            historial_service.registrar_accion(
                usuario=usuario,
                rol=rol,
                accion="ACTUALIZAR_UBICACION_OPERATIVO",
                detalles=detalles,
                id_infraccion=id_infraccion,
                folio=detalle["folio"],
                id_admin=session["admin"].get("id_admin")
            )

            flash("Ubicación y estado de retención del vehículo actualizados correctamente.")
            return redirect(url_for("admin_multas"))
        except Exception as e:
            flash(f"Error al actualizar ubicación: {str(e)}")

    return render_template("operativo/actualizar_ubicacion.html", detalle=detalle, corralones=corralones)


# ============================================================
# Nuevo Apartado: Historial de Cambios y Auditoría (Admin)
# ============================================================
@app.route("/admin/historial")
def admin_historial():
    if "admin" not in session:
        return redirect(url_for("login"))

    filtro_accion = request.args.get("accion")
    filtro_usuario = request.args.get("usuario")

    historial = historial_service.obtener_historial(
        filtro_accion=filtro_accion,
        filtro_usuario=filtro_usuario
    )
    acciones = historial_service.obtener_acciones_unicas()

    return render_template(
        "admin/historial.html",
        historial=historial,
        acciones=acciones,
        filtro_accion=filtro_accion,
        filtro_usuario=filtro_usuario
    )


@app.route("/admin/reportes")
def admin_reportes():
    if "admin" not in session:
        return redirect(url_for("login"))
    reportes = reportes_service.resumen()
    return render_template("admin/reportes.html", reportes=reportes)



# ============================================================
# Inicio / Presentación del Sistema y Videos
# ============================================================
@app.route("/inicio")
def inicio():
    """Página de inicio con información del sistema, funcionalidades y videos tutoriales."""
    return render_template("inicio.html")


# ============================================================
# Mapa Interactivo de Corralones para el Usuario
# ============================================================
@app.route("/mapa")
def mapa():
    """Mapa interactivo con los corralones oficiales de la CDMX."""
    corralones = multas_service.obtener_todos_los_corralones()
    return render_template("mapa.html", corralones=corralones)


@app.route("/api/corralones")
def api_corralones():
    """API REST para suministrar los datos de corralones al mapa."""
    corralones = multas_service.obtener_todos_los_corralones()
    return jsonify(corralones)



@app.route("/videos")
def videos():
    """Apartado directo de videos tutoriales para ciudadanos y administradores."""
    return redirect(url_for("inicio") + "#videos")


# ============================================================
# Ruta raíz: Redirige al inicio de sesión primero
# ============================================================
@app.route("/")
def index():
    if "admin" in session or "ciudadano" in session:
        return redirect(url_for("inicio"))
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)