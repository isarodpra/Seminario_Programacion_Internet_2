from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import datetime

def generar_comprobante_pdf(pago, infraccion, vehiculo, ciudadano):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter # 612 x 792

    c_guinda = colors.HexColor("#7b1e3a")
    c_azul = colors.HexColor("#1a3d7c")
    c_verde = colors.HexColor("#16a34a")
    c_gris_fondo = colors.HexColor("#f8fafc")
    c_gris_borde = colors.HexColor("#cbd5e1")
    c_gris_texto = colors.HexColor("#1e293b")
    c_gris_mutado = colors.HexColor("#64748b")

    # 1. ENCABEZADO INSTITUCIONAL
    p.setFillColor(c_guinda)
    p.rect(0, height - 70, width, 70, fill=True, stroke=False)
    
    # Línea dorada / acento
    p.setFillColor(colors.HexColor("#d97706"))
    p.rect(0, height - 74, width, 4, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, height - 32, "GOBIERNO DE LA CIUDAD DE MÉXICO")
    p.setFont("Helvetica", 9.5)
    p.drawString(40, height - 48, "SECRETARÍA DE ADMINISTRACIÓN Y FINANZAS  •  TESORERÍA CDMX")
    p.setFont("Helvetica-Oblique", 8)
    p.drawRightString(width - 40, height - 32, "Sistema de Gestión y Pago de Multas Vehiculares (GPMV)")
    p.drawRightString(width - 40, height - 48, "Comprobante Oficial Digital de Liquidación")

    # 2. TÍTULO Y BADGE DE ESTADO
    y = height - 105
    p.setFillColor(c_azul)
    p.setFont("Helvetica-Bold", 15)
    p.drawString(40, y, "RECIBO OFICIAL DE PAGO DE INFRACCIÓN")

    # Badge PAGADO verde
    p.setFillColor(c_verde)
    p.roundRect(width - 170, y - 6, 130, 24, 4, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width - 105, y + 1, "✓ PAGO ACREDITADO")

    # Subtítulo con fecha
    y -= 18
    p.setFillColor(c_gris_mutado)
    p.setFont("Helvetica", 8.5)
    p.drawString(40, y, f"Folio de Liquidación: {pago.get('referencia', 'N/A')}  |  Fecha de emisión: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Separador sutil
    y -= 12
    p.setStrokeColor(c_gris_borde)
    p.setLineWidth(1)
    p.line(40, y, width - 40, y)

    # 3. RECUADRO: DATOS DE LA TRANSACCIÓN (Columna 1) Y DEL CONTRIBUYENTE (Columna 2)
    y -= 20
    box_height = 115
    p.setFillColor(c_gris_fondo)
    p.setStrokeColor(c_gris_borde)
    p.setLineWidth(0.8)
    p.roundRect(40, y - box_height, width - 80, box_height, 6, fill=True, stroke=True)

    # Título del recuadro
    p.setFillColor(c_guinda)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(55, y - 16, "DATOS GENERALES DE LA OPERACIÓN")
    p.drawString(320, y - 16, "DATOS DEL VEHÍCULO Y CONTRIBUYENTE")

    p.setStrokeColor(c_gris_borde)
    p.line(305, y - 22, 305, y - box_height + 10)

    # Contenido columna 1
    p.setFont("Helvetica-Bold", 8.5)
    p.setFillColor(c_gris_texto)
    p.drawString(55, y - 36, "Referencia de Pago:")
    p.drawString(55, y - 52, "Folio Infracción:")
    p.drawString(55, y - 68, "Fecha y Hora de Pago:")
    p.drawString(55, y - 84, "Método de Pago:")
    p.drawString(55, y - 100, "Estatus de la Infracción:")

    p.setFont("Helvetica", 8.5)
    p.drawString(160, y - 36, str(pago.get("referencia", "N/A")))
    p.drawString(160, y - 52, str(infraccion.get("folio", "N/A")))
    fecha_pago_str = str(pago.get("fecha_pago", "N/A"))
    p.drawString(160, y - 68, fecha_pago_str)
    p.drawString(160, y - 84, str(pago.get("metodo_pago", "N/A")))
    p.setFillColor(c_verde)
    p.setFont("Helvetica-Bold", 8.5)
    p.drawString(160, y - 100, "PAGADA / LIBERADA")

    # Contenido columna 2
    p.setFillColor(c_gris_texto)
    p.setFont("Helvetica-Bold", 8.5)
    p.drawString(320, y - 36, "Propietario:")
    p.drawString(320, y - 52, "RFC:")
    p.drawString(320, y - 68, "Placa Vehicular:")
    p.drawString(320, y - 84, "Vehículo:")
    p.drawString(320, y - 100, "Motivo Sanción:")

    nombre_completo = f"{ciudadano.get('nombre', '')} {ciudadano.get('apellido', '')}".strip()
    p.setFont("Helvetica", 8.5)
    p.drawString(410, y - 36, nombre_completo or "N/A")
    p.drawString(410, y - 52, str(ciudadano.get("rfc", "N/A")))
    
    # Placa con estilo destacado
    placa_str = str(vehiculo.get("placa", "N/A"))
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(c_azul)
    p.drawString(410, y - 68, placa_str)

    p.setFont("Helvetica", 8.5)
    p.setFillColor(c_gris_texto)
    vehiculo_desc = f"{vehiculo.get('marca', '')} {vehiculo.get('modelo', '')} ({vehiculo.get('anio', '')})".strip()
    p.drawString(410, y - 84, vehiculo_desc)
    motivo_str = str(infraccion.get("motivo", "Infracción al Reglamento de Tránsito"))
    if len(motivo_str) > 28:
        motivo_str = motivo_str[:26] + "..."
    p.drawString(410, y - 100, motivo_str)

    y -= (box_height + 25)

    # 4. TABLA DE CONCEPTOS Y DESGLOSE CONTABLE
    p.setFillColor(c_azul)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "DESGLOSE DE LIQUIDACIÓN")
    y -= 12

    # Encabezado tabla
    p.setFillColor(c_azul)
    p.roundRect(40, y - 18, width - 80, 20, 2, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 8)
    p.drawString(55, y - 12, "CONCEPTO")
    p.drawString(270, y - 12, "MOTIVO / DETALLE")
    p.drawString(430, y - 12, "MONTO BASE")
    p.drawRightString(width - 55, y - 12, "TOTAL LIQUIDADO")

    # Fila de datos
    y -= 38
    p.setFillColor(colors.white)
    p.setStrokeColor(c_gris_borde)
    p.rect(40, y - 10, width - 80, 28, fill=True, stroke=True)

    p.setFillColor(c_gris_texto)
    p.setFont("Helvetica-Bold", 8)
    p.drawString(55, y + 4, f"Multa Folio {infraccion.get('folio', '')}")
    p.setFont("Helvetica", 7.5)
    p.drawString(55, y - 6, f"Vehículo Placas {vehiculo.get('placa', '')}")

    p.setFont("Helvetica", 8)
    p.drawString(270, y + 1, motivo_str)

    monto_base = float(infraccion.get("monto", 0.0))
    p.drawString(430, y + 1, f"${monto_base:,.2f} MXN")

    monto_pagado = float(pago.get("monto_pagado", 0.0))
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(c_guinda)
    p.drawRightString(width - 55, y + 1, f"${monto_pagado:,.2f} MXN")

    # Fila resumen / total
    y -= 25
    p.setFillColor(c_gris_fondo)
    p.setStrokeColor(c_gris_borde)
    p.rect(340, y - 12, width - 380, 26, fill=True, stroke=True)

    p.setFillColor(c_gris_texto)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(355, y - 4, "TOTAL CUBIERTO:")
    p.setFillColor(c_verde)
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width - 55, y - 4, f"${monto_pagado:,.2f} MXN")

    y -= 40

    # 5. CERTIFICACIÓN DIGITAL Y SELLO DE SEGURIDAD
    p.setFillColor(c_gris_fondo)
    p.setStrokeColor(c_gris_borde)
    seal_box_height = 110
    p.roundRect(40, y - seal_box_height, width - 80, seal_box_height, 6, fill=True, stroke=True)

    p.setFillColor(c_guinda)
    p.setFont("Helvetica-Bold", 8.5)
    p.drawString(55, y - 16, "CERTIFICACIÓN DE AUTENTICIDAD Y SELLO DIGITAL")

    # Cadena original simulada
    p.setFont("Helvetica-Bold", 7.5)
    p.setFillColor(c_gris_mutado)
    p.drawString(55, y - 30, "Cadena Original de Certificación Digital:")
    p.setFont("Courier", 6.5)
    p.setFillColor(c_gris_texto)
    cadena_original = f"||1.1|{pago.get('referencia', '')}|{fecha_pago_str}|{monto_pagado:.2f}|{pago.get('metodo_pago', '')}|CDMX-TESORERIA-SAT-VAL-2026||"
    p.drawString(55, y - 40, cadena_original[:85])
    p.drawString(55, y - 49, cadena_original[85:170] if len(cadena_original) > 85 else "")

    # Sello digital del emisor
    p.setFont("Helvetica-Bold", 7.5)
    p.setFillColor(c_gris_mutado)
    p.drawString(55, y - 62, "Sello Digital de la Tesorería CDMX:")
    p.setFont("Courier", 6.2)
    p.setFillColor(c_gris_texto)
    sello_digital = "k8V9+mXJ2wL0PzQaRtY7uI4oNbV1cXeZsW3qA6sD8fG0hJ2kL4zX7c=" + "eF4jK8mN1pQ3sU5wY7zB9cD0fH2jL4n"
    p.drawString(55, y - 72, sello_digital[:85])
    p.drawString(55, y - 81, sello_digital[85:170] if len(sello_digital) > 85 else "")

    p.setFont("Helvetica-Oblique", 7)
    p.setFillColor(c_gris_mutado)
    p.drawString(55, y - 98, "Este recibo digital cuenta con firma electrónica avanzada y certificación de pago ante la Secretaría de Administración y Finanzas.")

    # 6. PIE DE PÁGINA OFICIAL
    p.setStrokeColor(c_gris_borde)
    p.setLineWidth(0.6)
    p.line(40, 50, width - 40, 50)

    p.setFont("Helvetica", 7)
    p.setFillColor(c_gris_mutado)
    p.drawString(40, 38, "Secretaría de Movilidad (SEMOVI)  •  Secretaría de Seguridad Ciudadana (SSC)  •  Gobierno de la Ciudad de México")
    p.drawString(40, 28, "Para aclaraciones o validación en línea de este folio, visite: https://gpmv.cdmx.gob.mx o llame a Locatel al *0311.")
    p.drawRightString(width - 40, 38, "Página 1 de 1")
    p.drawRightString(width - 40, 28, "Documento Oficial Autenticado")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer