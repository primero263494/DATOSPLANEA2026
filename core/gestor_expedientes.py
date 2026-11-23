# -*- coding: utf-8 -*-
"""
Gestor de Expedientes Urbanísticos, Lista de Chequeo, Carga Documental e Informes Técnicos
Secretaría de Planeación y Desarrollo Territorial - El Carmen de Viboral
"""

import io
import os
import json
import shutil
import sqlite3
from datetime import datetime

DB_PATH = os.path.join("expedientes", "planeacion_carmen.db")
FILES_DIR = os.path.join("expedientes", "documentos_radicados")

def inicializar_bd():
    os.makedirs("expedientes", exist_ok=True)
    os.makedirs(FILES_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS expedientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            radicado TEXT UNIQUE NOT NULL,
            fecha_radicacion TEXT NOT NULL,
            tipo_tramite TEXT NOT NULL,
            titular_nombre TEXT NOT NULL,
            titular_documento TEXT NOT NULL,
            matricula_inmobiliaria TEXT,
            cedula_catastral TEXT,
            direccion_predio TEXT,
            clasificacion_suelo TEXT,
            area_lote_m2 REAL DEFAULT 0,
            area_construida_m2 REAL DEFAULT 0,
            valor_liquidado REAL DEFAULT 0,
            estado TEXT DEFAULT 'EN REVISIÓN',
            observaciones_tecnicas TEXT DEFAULT '',
            checklist_json TEXT DEFAULT '{}',
            datos_verificacion_json TEXT DEFAULT '{}'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS documentos_expediente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            radicado TEXT NOT NULL,
            categoria TEXT NOT NULL,
            nombre_archivo TEXT NOT NULL,
            ruta_guardada TEXT NOT NULL,
            fecha_carga TEXT NOT NULL,
            observacion TEXT DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()

def crear_o_actualizar_expediente(datos: dict):
    inicializar_bd()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM expedientes WHERE radicado = ?", (datos["radicado"],))
    existe = cur.fetchone()

    if existe:
        cur.execute("""
            UPDATE expedientes SET
                tipo_tramite = ?, titular_nombre = ?, titular_documento = ?,
                matricula_inmobiliaria = ?, cedula_catastral = ?, direccion_predio = ?,
                clasificacion_suelo = ?, area_lote_m2 = ?, area_construida_m2 = ?,
                valor_liquidado = ?, estado = ?, observaciones_tecnicas = ?,
                checklist_json = ?, datos_verificacion_json = ?
            WHERE radicado = ?
        """, (
            datos["tipo_tramite"], datos["titular_nombre"], datos["titular_documento"],
            datos.get("matricula_inmobiliaria", ""), datos.get("cedula_catastral", ""),
            datos.get("direccion_predio", ""), datos.get("clasificacion_suelo", ""),
            datos.get("area_lote_m2", 0.0), datos.get("area_construida_m2", 0.0),
            datos.get("valor_liquidado", 0.0), datos.get("estado", "EN REVISIÓN"),
            datos.get("observaciones_tecnicas", ""),
            json.dumps(datos.get("checklist", {}), ensure_ascii=False),
            json.dumps(datos.get("verificacion", {}), ensure_ascii=False),
            datos["radicado"]
        ))
    else:
        cur.execute("""
            INSERT INTO expedientes (
                radicado, fecha_radicacion, tipo_tramite, titular_nombre, titular_documento,
                matricula_inmobiliaria, cedula_catastral, direccion_predio, clasificacion_suelo,
                area_lote_m2, area_construida_m2, valor_liquidado, estado,
                observaciones_tecnicas, checklist_json, datos_verificacion_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datos["radicado"], datetime.now().strftime("%Y-%m-%d %H:%M"),
            datos["tipo_tramite"], datos["titular_nombre"], datos["titular_documento"],
            datos.get("matricula_inmobiliaria", ""), datos.get("cedula_catastral", ""),
            datos.get("direccion_predio", ""), datos.get("clasificacion_suelo", ""),
            datos.get("area_lote_m2", 0.0), datos.get("area_construida_m2", 0.0),
            datos.get("valor_liquidado", 0.0), datos.get("estado", "EN REVISIÓN"),
            datos.get("observaciones_tecnicas", ""),
            json.dumps(datos.get("checklist", {}), ensure_ascii=False),
            json.dumps(datos.get("verificacion", {}), ensure_ascii=False)
        ))

    conn.commit()
    conn.close()

def eliminar_expediente_completo(radicado: str) -> bool:
    """Elimina un expediente/trámite de la base de datos y borra sus documentos asociados."""
    inicializar_bd()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT ruta_guardada FROM documentos_expediente WHERE radicado = ?", (radicado,))
    rutas = [r[0] for r in cur.fetchall()]
    for ruta in rutas:
        if ruta and os.path.exists(ruta):
            try:
                os.remove(ruta)
            except OSError:
                pass

    carpeta_radicado = os.path.join(FILES_DIR, radicado.replace("/", "_").replace(" ", "_"))
    if os.path.isdir(carpeta_radicado):
        try:
            shutil.rmtree(carpeta_radicado)
        except OSError:
            pass

    cur.execute("DELETE FROM documentos_expediente WHERE radicado = ?", (radicado,))
    cur.execute("DELETE FROM expedientes WHERE radicado = ?", (radicado,))
    eliminado = cur.rowcount > 0

    conn.commit()
    conn.close()
    return eliminado

def listar_expedientes() -> list:
    inicializar_bd()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM expedientes ORDER BY id DESC")
    filas = [dict(r) for r in cur.fetchall()]
    conn.close()
    return filas

def guardar_documento_expediente(radicado: str, categoria: str, nombre_archivo: str, contenido_bytes: bytes, observacion: str = ""):
    inicializar_bd()
    carpeta_radicado = os.path.join(FILES_DIR, radicado.replace("/", "_").replace(" ", "_"))
    os.makedirs(carpeta_radicado, exist_ok=True)
    ruta_final = os.path.join(carpeta_radicado, nombre_archivo)

    with open(ruta_final, "wb") as f:
        f.write(contenido_bytes)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO documentos_expediente (radicado, categoria, nombre_archivo, ruta_guardada, fecha_carga, observacion)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (radicado, categoria, nombre_archivo, ruta_final, datetime.now().strftime("%Y-%m-%d %H:%M"), observacion))
    conn.commit()
    conn.close()

def eliminar_documento_expediente(doc_id: int) -> bool:
    """Elimina un documento cargado específico de un expediente y borra su archivo físico."""
    inicializar_bd()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT ruta_guardada FROM documentos_expediente WHERE id = ?", (doc_id,))
    fila = cur.fetchone()
    if fila:
        ruta = fila[0]
        if ruta and os.path.exists(ruta):
            try:
                os.remove(ruta)
            except OSError:
                pass
    cur.execute("DELETE FROM documentos_expediente WHERE id = ?", (doc_id,))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok

def listar_documentos_expediente(radicado: str) -> list:
    inicializar_bd()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM documentos_expediente WHERE radicado = ? ORDER BY id DESC", (radicado,))
    filas = [dict(r) for r in cur.fetchall()]
    conn.close()
    return filas

def generar_informe_tecnico_markdown(exp: dict, docs: list) -> str:
    """
    Genera el Acta / Concepto Técnico de Revisión Urbanística, Arquitectónica y Estructural
    conforme al Decreto 1077 de 2015, Acuerdo 012 de 2017, Decreto 152 de 2018 y Decreto 001 de 2026.
    """
    checklist = json.loads(exp.get("checklist_json") or "{}")
    verificacion = json.loads(exp.get("datos_verificacion_json") or "{}")

    cumplidos = [k for k, v in checklist.items() if v == "CUMPLE"]
    pendientes = [k for k, v in checklist.items() if v == "NO CUMPLE / PENDIENTE"]

    lineas = [
        "# ACTA DE REVISIÓN TÉCNICA, JURÍDICA Y LIQUIDACIÓN DE TRÁMITE URBANÍSTICO",
        "**MUNICIPIO DE EL CARMEN DE VIBORAL – SECRETARÍA DE PLANEACIÓN Y DESARROLLO TERRITORIAL**",
        f"**Fecha de generación:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "---",
        "## 1. IDENTIFICACIÓN DEL EXPEDIENTE",
        f"- **Número de Radicado:** {exp.get('radicado')}",
        f"- **Fecha de Radicación:** {exp.get('fecha_radicacion')}",
        f"- **Tipo de Trámite:** {exp.get('tipo_tramite')}",
        f"- **Titular(es):** {exp.get('titular_nombre')} (ID: {exp.get('titular_documento')})",
        f"- **Matrícula Inmobiliaria:** {exp.get('matricula_inmobiliaria') or 'No registrada'}",
        f"- **Cédula Catastral:** {exp.get('cedula_catastral') or 'No registrada'}",
        f"- **Dirección / Ubicación:** {exp.get('direccion_predio') or 'No registrada'}",
        f"- **Clasificación del Suelo (Acuerdo 012/2017):** {exp.get('clasificacion_suelo')}",
        f"- **Área Lote / Predio:** {exp.get('area_lote_m2', 0):,.2f} m²",
        f"- **Área Construida / Intervenida:** {exp.get('area_construida_m2', 0):,.2f} m²",
        f"- **Estado Actual del Trámite:** **{exp.get('estado')}**",
        "",
        "## 2. MARCO NORMATIVO APLICADO",
        "- **Norma Nacional:** Ley 388 de 1997, Ley 400 de 1997 (NSR-10), Decreto Único Reglamentario 1077 de 2015, Resolución 1025 de 2021.",
        "- **Norma Municipal:** Acuerdo 012 de 2017 (PBOT), Decreto 152 de 2018 (Manual de Urbanismo y Espacio Público), Acuerdo 019 de 2020 y Decreto Tarifario 001 del 8 de enero de 2026 (UVT = $52.374).",
        "",
        "## 3. RESULTADO DE LISTA DE CHEQUEO DOCUMENTAL",
        f"- **Ítems verificados como CUMPLE:** {len(cumplidos)}",
        f"- **Ítems PENDIENTES / NO CUMPLE:** {len(pendientes)}",
    ]

    if pendientes:
        lineas.append("")
        lineas.append("### Documentos o requisitos faltantes (Acta de Observaciones):")
        for p in pendientes:
            lineas.append(f"- [ ] **{p}**")

    lineas.extend([
        "",
        "## 4. VERIFICACIÓN DE PARÁMETROS URBANÍSTICOS Y TÉCNICOS",
    ])
    hallazgos = verificacion.get("hallazgos", [])
    if hallazgos:
        for h in hallazgos:
            lineas.append(f"- **[{h['estado']}] {h['parametro']}:** {h['detalle']}")
    else:
        lineas.append("- Sin parámetros geométricos registrados en esta revisión.")

    lineas.extend([
        "",
        "## 5. LIQUIDACIÓN ESTIMADA DE IMPUESTO DE DELINEACIÓN / DERECHOS (VIGENCIA 2026)",
        f"- **Valor Liquidado (Decreto 001 de 2026):** **${exp.get('valor_liquidado', 0):,.0f} COP**",
        "",
        "## 6. EXPEDIENTE DIGITAL (ARCHIVOS CARGADOS EN REPOSITORIO)",
    ])
    if docs:
        for d in docs:
            lineas.append(f"- `{d['categoria']}` — **{d['nombre_archivo']}** (Cargado: {d['fecha_carga']})")
    else:
        lineas.append("- No hay archivos digitales cargados aún en este expediente.")

    lineas.extend([
        "",
        "## 7. CONCEPTO Y OBSERVACIONES DEL FUNCIONARIO REVISOR",
        exp.get("observaciones_tecnicas") or "Sin observaciones adicionales.",
        "",
        "---",
        "*Documento generado automáticamente por el Sistema de Gestión y Revisión Urbanística – El Carmen de Viboral.*"
    ])
    return "\n".join(lineas)

def generar_informe_tecnico_docx(exp: dict, docs: list) -> bytes:
    """
    Genera el informe técnico oficial en formato Word editable (.docx) con tipografía Arial 12 pt negro
    y estructura institucional para la Secretaría de Planeación y Desarrollo Territorial.
    """
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Configurar estilo Normal en Arial 12 pt negro
    style_normal = doc.styles["Normal"]
    style_normal.font.name = "Arial"
    style_normal.font.size = Pt(12)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)

    def _add_titulo(texto: str, nivel: int = 1):
        p = doc.add_paragraph()
        run = p.add_run(texto)
        run.bold = True
        run.font.name = "Arial"
        run.font.color.rgb = RGBColor(0, 0, 0)
        if nivel == 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run.font.size = Pt(13)
        elif nivel == 1:
            run.font.size = Pt(12)
        else:
            run.font.size = Pt(12)
        return p

    def _add_parrafo_clave(etiqueta: str, valor: str):
        p = doc.add_paragraph()
        r1 = p.add_run(etiqueta)
        r1.bold = True
        r1.font.name = "Arial"
        r1.font.size = Pt(12)
        r1.font.color.rgb = RGBColor(0, 0, 0)

        r2 = p.add_run(valor)
        r2.font.name = "Arial"
        r2.font.size = Pt(12)
        r2.font.color.rgb = RGBColor(0, 0, 0)
        return p

    _add_titulo("MUNICIPIO DE EL CARMEN DE VIBORAL", 0)
    _add_titulo("SECRETARÍA DE PLANEACIÓN Y DESARROLLO TERRITORIAL", 0)
    _add_titulo("ACTA DE REVISIÓN TÉCNICA, JURÍDICA Y LIQUIDACIÓN DE TRÁMITE URBANÍSTICO", 0)
    _add_parrafo_clave("Fecha de generación: ", datetime.now().strftime("%d/%m/%Y %H:%M"))

    _add_titulo("1. IDENTIFICACIÓN DEL EXPEDIENTE", 1)
    tabla_id = doc.add_table(rows=11, cols=2)
    tabla_id.style = "Table Grid"
    filas_id = [
        ("Número de Radicado", str(exp.get("radicado") or "")),
        ("Fecha de Radicación", str(exp.get("fecha_radicacion") or "")),
        ("Tipo de Trámite", str(exp.get("tipo_tramite") or "")),
        ("Titular(es) e Identificación", f"{exp.get('titular_nombre') or ''} (ID: {exp.get('titular_documento') or 'N/R'})"),
        ("Matrícula Inmobiliaria", str(exp.get("matricula_inmobiliaria") or "No registrada")),
        ("Cédula Catastral", str(exp.get("cedula_catastral") or "No registrada")),
        ("Dirección / Ubicación", str(exp.get("direccion_predio") or "No registrada")),
        ("Clasificación del Suelo (PBOT)", str(exp.get("clasificacion_suelo") or "")),
        ("Área del Predio / Lote", f"{exp.get('area_lote_m2', 0):,.2f} m²"),
        ("Área Construida / Intervenida", f"{exp.get('area_construida_m2', 0):,.2f} m²"),
        ("Estado Actual del Trámite", str(exp.get("estado") or "")),
    ]
    for idx, (k, v) in enumerate(filas_id):
        c0 = tabla_id.cell(idx, 0)
        c1 = tabla_id.cell(idx, 1)
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.name = "Arial"
        r0.font.size = Pt(11)
        r0.font.color.rgb = RGBColor(0, 0, 0)

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.name = "Arial"
        r1.font.size = Pt(11)
        r1.font.color.rgb = RGBColor(0, 0, 0)

    _add_titulo("2. MARCO NORMATIVO APLICADO", 1)
    p_norm1 = doc.add_paragraph(style="List Bullet")
    p_norm1.add_run("Norma Nacional: Ley 388 de 1997, Ley 400 de 1997 (NSR-10), Decreto Único Reglamentario 1077 de 2015, Resolución 1025 de 2021.")
    p_norm2 = doc.add_paragraph(style="List Bullet")
    p_norm2.add_run("Norma Municipal: Acuerdo 012 de 2017 (PBOT), Decreto 152 de 2018 (Manual de Urbanismo y Espacio Público), Acuerdo 019 de 2020 y Decreto Tarifario 001 del 8 de enero de 2026 (UVT = $52.374).")

    _add_titulo("3. RESULTADO DE LISTA DE CHEQUEO DOCUMENTAL", 1)
    checklist = json.loads(exp.get("checklist_json") or "{}")
    cumplidos = [k for k, v in checklist.items() if v == "CUMPLE"]
    pendientes = [k for k, v in checklist.items() if v == "NO CUMPLE / PENDIENTE"]

    _add_parrafo_clave("Ítems verificados como CUMPLE: ", str(len(cumplidos)))
    _add_parrafo_clave("Ítems PENDIENTES / NO CUMPLE: ", str(len(pendientes)))

    if pendientes:
        _add_titulo("Requisitos pendientes (Acta de Observaciones):", 2)
        for p_item in pendientes:
            p_b = doc.add_paragraph(style="List Bullet")
            rb = p_b.add_run(p_item)
            rb.font.name = "Arial"
            rb.font.size = Pt(11)
            rb.font.color.rgb = RGBColor(0, 0, 0)

    _add_titulo("4. VERIFICACIÓN DE PARÁMETROS URBANÍSTICOS Y TÉCNICOS", 1)
    verificacion = json.loads(exp.get("datos_verificacion_json") or "{}")
    hallazgos = verificacion.get("hallazgos", [])
    if hallazgos:
        for h in hallazgos:
            p_h = doc.add_paragraph(style="List Bullet")
            rh = p_h.add_run(f"[{h['estado']}] {h['parametro']}: {h['detalle']}")
            rh.font.name = "Arial"
            rh.font.size = Pt(11)
            rh.font.color.rgb = RGBColor(0, 0, 0)
    else:
        doc.add_paragraph("Sin parámetros geométricos registrados en esta revisión.")

    _add_titulo("5. LIQUIDACIÓN ESTIMADA DE IMPUESTO DE DELINEACIÓN / DERECHOS (VIGENCIA 2026)", 1)
    _add_parrafo_clave("Valor Liquidado (Decreto 001 de 2026): ", f"${exp.get('valor_liquidado', 0):,.0f} COP")

    _add_titulo("6. EXPEDIENTE DIGITAL (ARCHIVOS CARGADOS EN REPOSITORIO)", 1)
    if docs:
        for d in docs:
            p_d = doc.add_paragraph(style="List Bullet")
            rd = p_d.add_run(f"[{d['categoria']}] {d['nombre_archivo']} (Cargado: {d['fecha_carga']})")
            rd.font.name = "Arial"
            rd.font.size = Pt(11)
            rd.font.color.rgb = RGBColor(0, 0, 0)
    else:
        doc.add_paragraph("No hay archivos digitales cargados aún en este expediente.")

    _add_titulo("7. CONCEPTO Y OBSERVACIONES DEL FUNCIONARIO REVISOR", 1)
    doc.add_paragraph(exp.get("observaciones_tecnicas") or "Sin observaciones adicionales.")

    p_firma = doc.add_paragraph("\n_________________________________________\nProfesional Revisor / Secretaría de Planeación y Desarrollo Territorial\nMunicipio de El Carmen de Viboral")
    for r in p_firma.runs:
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0, 0, 0)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
