# -*- coding: utf-8 -*-
"""
Gestor de Expedientes Urbanísticos, Lista de Chequeo, Carga Documental e Informes Técnicos
Secretaría de Planeación y Desarrollo Territorial - El Carmen de Viboral
"""

import os
import json
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
