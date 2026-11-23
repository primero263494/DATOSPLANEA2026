# -*- coding: utf-8 -*-
"""
SISTEMA INTEGRAL DE CONSULTA NORMATIVA, LIQUIDACIÓN, REVISIÓN Y EXPEDIENTES URBANÍSTICOS
Municipio de El Carmen de Viboral (Antioquia)
Ejecutar con: streamlit run app_planeacion.py
"""

import json
import streamlit as st
from data.normativa_carmen import (
    PARAMETROS_2026,
    TARIFAS_DELINEACION_2026,
    FACTOR_MODALIDAD_CONSTRUCCION,
    OTRAS_ACTUACIONES_2026,
    REGLAS_URBANISTICAS_PBOT,
    CHECKLIST_TRAMITES
)
from core.calculos import (
    calcular_delineacion_construccion,
    calcular_urbanizacion_o_parcelacion,
    calcular_subdivision_o_reloteo,
    verificar_parametros_urbanisticos
)
from core.gestor_expedientes import (
    inicializar_bd,
    crear_o_actualizar_expediente,
    listar_expedientes,
    guardar_documento_expediente,
    listar_documentos_expediente,
    generar_informe_tecnico_markdown
)

st.set_page_config(
    page_title="Planeación Urbanística - El Carmen de Viboral",
    page_icon="🏛️",
    layout="wide"
)

inicializar_bd()

st.title("🏛️ Sistema de Gestión Urbanística y Licenciamiento")
st.caption(
    f"Municipio de El Carmen de Viboral | Vigencia {PARAMETROS_2026['anio']} "
    f"(UVT: ${PARAMETROS_2026['uvt']:,.0f} | SMMLV: ${PARAMETROS_2026['smmlv']:,.0f})"
)

menu = st.sidebar.radio(
    "Módulos del Sistema",
    [
        "1. Consulta Normativa y Tarifaria",
        "2. Calculadora de Licencias y Tributos",
        "3. Verificación Técnica de Planos",
        "4. Gestión de Expedientes, Chequeo y Carga",
        "5. Generación de Informes Oficiales"
    ]
)

# -------------------------------------------------------------------------
# MÓDULO 1: CONSULTA NORMATIVA Y TARIFARIA
# -------------------------------------------------------------------------
if menu == "1. Consulta Normativa y Tarifaria":
    st.header("📚 Buscador de Norma Local (PBOT / Decreto 152/2018) y Nacional")
    termino = st.text_input("Buscar por palabra clave (ej. ochava, andén, Cimarronas, ICANH, pendiente, tarifa, rural):")

    tab1, tab2, tab3 = st.tabs(["Reglas Urbanísticas PBOT & Nacional", "Tarifas Delineación 2026", "Otras Actuaciones 2026"])

    with tab1:
        for r in REGLAS_URBANISTICAS_PBOT:
            texto_busqueda = f"{r['categoria']} {r['norma']} {r['regla']}".lower()
            if not termino or termino.lower() in texto_busqueda:
                with st.expander(f"📌 {r['categoria']} — ({r['norma']})", expanded=bool(termino)):
                    st.write(r["regla"])

    with tab2:
        filas_tarifas = []
        for k, v in TARIFAS_DELINEACION_2026.items():
            if not termino or termino.lower() in v["nombre"].lower() or termino.lower() in v["observacion"].lower():
                filas_tarifas.append({
                    "Uso / Clasificación": v["nombre"],
                    "UVT": v["uvt"],
                    "Valor Calculado": f"${v['valor_exacto']:,.0f}",
                    "Tarifa Ajustada 2026": f"${v['valor_ajustado']:,.0f}",
                    "Criterios / Notas": v["observacion"]
                })
        st.dataframe(filas_tarifas, use_container_width=True)

    with tab3:
        filas_otras = []
        for k, v in OTRAS_ACTUACIONES_2026.items():
            if not termino or termino.lower() in v["nombre"].lower():
                filas_otras.append({
                    "Actuación / Certificado": v["nombre"],
                    "UVT": v["uvt"],
                    "Valor Ajustado 2026": f"${v['valor_ajustado']:,.0f}"
                })
        st.dataframe(filas_otras, use_container_width=True)

# -------------------------------------------------------------------------
# MÓDULO 2: CALCULADORA DE LICENCIAS Y TRIBUTOS
# -------------------------------------------------------------------------
elif menu == "2. Calculadora de Licencias y Tributos":
    st.header("🧮 Liquidación de Impuesto de Delineación y Derechos Urbanísticos (2026)")

    tipo_calc = st.selectbox(
        "Seleccione el tipo de liquidación:",
        [
            "Licencia de Construcción / Reforma / Adición / Reconocimiento",
            "Licencia de Urbanización o Parcelación",
            "Licencia de Subdivisión Predial o Reloteo",
            "Otras Actuaciones (Alineamiento, Norma, Uso, PH, etc.)"
        ]
    )

    if tipo_calc == "Licencia de Construcción / Reforma / Adición / Reconocimiento":
        col1, col2 = st.columns(2)
        with col1:
            uso_sel = st.selectbox(
                "Uso y Clasificación:",
                list(TARIFAS_DELINEACION_2026.keys()),
                format_func=lambda x: TARIFAS_DELINEACION_2026[x]["nombre"]
            )
            mod_sel = st.selectbox(
                "Modalidad de Licencia:",
                list(FACTOR_MODALIDAD_CONSTRUCCION.keys()),
                format_func=lambda x: FACTOR_MODALIDAD_CONSTRUCCION[x]["nombre"]
            )
        with col2:
            area_m2 = st.number_input("Área del proyecto / intervención (m²):", min_value=1.0, value=120.0, step=1.0)
            usar_ajustado = st.checkbox("Aplicar columna 'V Ajustado' oficial del Decreto 001 de 2026", value=True)

        res = calcular_delineacion_construccion(uso_sel, area_m2, mod_sel, usar_ajustado)
        st.success(f"### Total a Liquidar: ${res['total_pagar']:,.0f} COP")
        st.json(res)

    elif tipo_calc == "Licencia de Urbanización o Parcelación":
        col1, col2 = st.columns(2)
        with col1:
            subtipo = st.radio("Tipo de Licencia:", ["urbanizacion", "parcelacion"], format_func=lambda x: "Urbanización (10% SMLDV)" if x == "urbanizacion" else "Parcelación (2,5% SMLDV)")
            area_bruta = st.number_input("Área Bruta del Predio (m²):", min_value=1.0, value=2730.82, step=10.0)
        with col2:
            descuentos = st.number_input("Descuento por Retiros Ambientales y Vías Obligadas PBOT (m²):", min_value=0.0, value=0.0, step=10.0)

        res = calcular_urbanizacion_o_parcelacion(subtipo, area_bruta, descuentos)
        st.success(f"### Total a Liquidar: ${res['total_pagar']:,.0f} COP")
        st.json(res)

    elif tipo_calc == "Licencia de Subdivisión Predial o Reloteo":
        mod_sub = st.selectbox("Modalidad:", ["subdivision_urbana", "subdivision_rural", "reloteo"])
        if mod_sub != "reloteo":
            unidades = st.number_input("Número de unidades resultantes:", min_value=2, value=2, step=1)
            res = calcular_subdivision_o_reloteo(mod_sub, num_unidades=unidades)
        else:
            area_u = st.number_input("Área útil urbanizable (m²):", min_value=1.0, value=850.0, step=10.0)
            res = calcular_subdivision_o_reloteo(mod_sub, area_util_m2=area_u)
        st.success(f"### Total a Liquidar: ${res['total_pagar']:,.0f} COP")
        st.json(res)

    else:
        actuaciones_sel = st.multiselect(
            "Seleccione las actuaciones requeridas:",
            list(OTRAS_ACTUACIONES_2026.keys()),
            default=["alineamiento_hilos", "concepto_norma"],
            format_func=lambda x: f"{OTRAS_ACTUACIONES_2026[x]['nombre']} (${OTRAS_ACTUACIONES_2026[x]['valor_ajustado']:,.0f})"
        )
        total_act = sum(OTRAS_ACTUACIONES_2026[a]["valor_ajustado"] for a in actuaciones_sel)
        st.success(f"### Total Actuaciones Seleccionadas: ${total_act:,.0f} COP")

# -------------------------------------------------------------------------
# MÓDULO 3: VERIFICACIÓN TÉCNICA DE PLANOS
# -------------------------------------------------------------------------
elif menu == "3. Verificación Técnica de Planos":
    st.header("📐 Chequeo Geométrico y Normativo de Planos (PBOT / Decreto 152 de 2018)")
    c1, c2, c3 = st.columns(3)
    with c1:
        area_neta = st.number_input("Área Neta / Útil del Lote (m²):", min_value=1.0, value=200.0)
        area_p1 = st.number_input("Área Ocupada 1er Piso (m²):", min_value=0.0, value=120.0)
        area_const = st.number_input("Área Total Construida (m²):", min_value=0.0, value=240.0)
    with c2:
        ancho_anden = st.number_input("Ancho libre de andén proyectado (m):", min_value=0.0, value=1.20, step=0.05)
        altura_bordillo = st.number_input("Altura de bordillo calzada (m):", min_value=0.0, value=0.18, step=0.01)
        es_esquina = st.checkbox("¿El predio está ubicado en esquina?", value=True)
        radio_ochava = st.number_input("Radio de ochava proyectado (m):", min_value=0.0, value=2.00, step=0.10)
    with c3:
        pendiente = st.number_input("Pendiente máxima del terreno (%):", min_value=0.0, value=12.0, step=1.0)
        tipo_q = st.selectbox("Fuente hídrica cercana:", ["otra", "la_cimarronas", "la_madera"])
        dist_q = st.number_input("Distancia al borde / cota inundación (m):", min_value=0.0, value=60.0, step=1.0)

    hallazgos = verificar_parametros_urbanisticos(
        area_neta, area_p1, area_const, ancho_anden, altura_bordillo,
        es_esquina, radio_ochava, pendiente, dist_q, tipo_q
    )

    st.subheader("Resultado de la Verificación Técnica:")
    for h in hallazgos:
        if h["estado"] == "NO CUMPLE":
            st.error(f"❌ **{h['parametro']}**: {h['detalle']}")
        elif h["estado"] == "ALERTA":
            st.warning(f"⚠️ **{h['parametro']}**: {h['detalle']}")
        elif h["estado"] == "CUMPLE":
            st.success(f"✅ **{h['parametro']}**: {h['detalle']}")
        else:
            st.info(f"ℹ️ **{h['parametro']}**: {h['detalle']}")

# -------------------------------------------------------------------------
# MÓDULO 4: GESTIÓN DE EXPEDIENTES, LISTA DE CHEQUEO Y CARGA DE DOCUMENTOS
# -------------------------------------------------------------------------
elif menu == "4. Gestión de Expedientes, Chequeo y Carga":
    st.header("🗂️ Radicación, Lista de Chequeo y Repositorio Digital del Trámite")

    col_a, col_b = st.columns(2)
    with col_a:
        radicado = st.text_input("Número de Radicado:", value="2026-URB-001")
        tipo_tramite_key = st.selectbox(
            "Tipo de Trámite:",
            list(CHECKLIST_TRAMITES.keys()),
            format_func=lambda x: CHECKLIST_TRAMITES[x]["nombre"]
        )
        titular_nombre = st.text_input("Nombre o Razón Social del Titular:", value="")
        titular_doc = st.text_input("Cédula / NIT del Titular:", value="")
        estado_exp = st.selectbox("Estado del Expediente:", ["EN REVISIÓN", "ACTA DE OBSERVACIONES", "VIABLE / APROBADO", "DESISTIDO / NEGADO"])

    with col_b:
        matricula = st.text_input("Matrícula Inmobiliaria (ORIP Rionegro):", value="020-")
        catastral = st.text_input("Cédula Catastral:", value="")
        direccion = st.text_input("Dirección / Vereda / Sector:", value="")
        suelo = st.selectbox("Clasificación del Suelo (PBOT):", ["Suelo Urbano", "Suelo de Expansión Urbana", "Suelo Rural", "Suelo Suburbano"])
        area_lote = st.number_input("Área del Predio (m²):", min_value=0.0, value=0.0)
        area_obra = st.number_input("Área Construida / Intervenida (m²):", min_value=0.0, value=0.0)
        valor_liq = st.number_input("Valor Liquidado (COP):", min_value=0.0, value=0.0, step=1000.0)

    st.subheader(f"✅ Lista de Chequeo Oficial — {CHECKLIST_TRAMITES[tipo_tramite_key]['nombre']}")
    st.caption(f"Base normativa: {CHECKLIST_TRAMITES[tipo_tramite_key]['norma_base']}")

    estado_checklist = {}
    for item in CHECKLIST_TRAMITES[tipo_tramite_key]["items"]:
        etiqueta = f"[{item['id']}] ({item['categoria']}) {item['requisito']}"
        estado_checklist[etiqueta] = st.selectbox(
            etiqueta,
            ["NO CUMPLE / PENDIENTE", "CUMPLE", "NO APLICA"],
            key=f"chk_{item['id']}"
        )

    obs_tecnicas = st.text_area("Observaciones Técnicas y Jurídicas del Funcionario Revisor:")

    if st.button("💾 Guardar / Actualizar Expediente en Base de Datos"):
        if not radicado or not titular_nombre:
            st.error("Debe ingresar al menos el número de radicado y el nombre del titular.")
        else:
            crear_o_actualizar_expediente({
                "radicado": radicado,
                "tipo_tramite": CHECKLIST_TRAMITES[tipo_tramite_key]["nombre"],
                "titular_nombre": titular_nombre,
                "titular_documento": titular_doc,
                "matricula_inmobiliaria": matricula,
                "cedula_catastral": catastral,
                "direccion_predio": direccion,
                "clasificacion_suelo": suelo,
                "area_lote_m2": area_lote,
                "area_construida_m2": area_obra,
                "valor_liquidado": valor_liq,
                "estado": estado_exp,
                "observaciones_tecnicas": obs_tecnicas,
                "checklist": estado_checklist
            })
            st.success(f"Expediente {radicado} guardado correctamente.")

    st.divider()
    st.subheader("📎 Cargar Documentos y Planos al Expediente Digital")
    cat_doc = st.selectbox(
        "Categoría del documento a cargar:",
        [
            "01_Juridico_FUN_Tradicion_Escritura",
            "02_Paz_y_Salvo_y_Notificacion",
            "03_Alineamiento_y_Factibilidades",
            "04_Planos_Arquitectonicos_Topografia",
            "05_Planos_Estructurales_Memorias_Suelos",
            "06_Ambiental_CORNARE_ICANH",
            "07_Liquidacion_y_Comprobante_Pago"
        ]
    )
    archivo_subido = st.file_uploader("Seleccione archivo (PDF, DWG, ZIP, JPG, PNG, DOC):", type=["pdf", "dwg", "zip", "jpg", "jpeg", "png", "doc", "docx"])
    nota_doc = st.text_input("Nota del documento (ej. Versión corregida tras acta de observaciones):")

    if st.button("📤 Subir Archivo al Expediente"):
        if archivo_subido is not None and radicado:
            guardar_documento_expediente(radicado, cat_doc, archivo_subido.name, archivo_subido.getvalue(), nota_doc)
            st.success(f"Archivo '{archivo_subido.name}' almacenado en el expediente {radicado}.")
        else:
            st.warning("Ingrese el número de radicado y seleccione un archivo.")

    if radicado:
        docs_actuales = listar_documentos_expediente(radicado)
        if docs_actuales:
            st.write("**Archivos cargados actualmente en este radicado:**")
            st.dataframe(docs_actuales, use_container_width=True)

# -------------------------------------------------------------------------
# MÓDULO 5: GENERACIÓN DE INFORMES OFICIALES
# -------------------------------------------------------------------------
elif menu == "5. Generación de Informes Oficiales":
    st.header("📄 Generación de Acta de Observaciones / Concepto Técnico Oficial")
    expedientes = listar_expedientes()
    if not expedientes:
        st.info("Aún no hay expedientes guardados. Cree uno en el Módulo 4.")
    else:
        opciones = {f"{e['radicado']} — {e['titular_nombre']} ({e['estado']})": e for e in expedientes}
        sel_label = st.selectbox("Seleccione el expediente:", list(opciones.keys()))
        exp_sel = opciones[sel_label]
        docs_sel = listar_documentos_expediente(exp_sel["radicado"])

        informe_md = generar_informe_tecnico_markdown(exp_sel, docs_sel)
        st.markdown(informe_md)

        st.download_button(
            label="⬇️ Descargar Informe Oficial (.md)",
            data=informe_md.encode("utf-8"),
            file_name=f"Informe_Tecnico_{exp_sel['radicado']}.md",
            mime="text/markdown"
        )
