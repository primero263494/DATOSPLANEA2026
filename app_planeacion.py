# -*- coding: utf-8 -*-
"""
SISTEMA INTEGRAL DE CONSULTA NORMATIVA, LIQUIDACIÓN, REVISIÓN, CARTOGRAFÍA Y EXPEDIENTES URBANÍSTICOS
Municipio de El Carmen de Viboral (Antioquia)
"""

import os
import base64
import streamlit as st
from data.normativa_carmen import (
    PARAMETROS_2026,
    TARIFAS_DELINEACION_2026,
    FACTOR_MODALIDAD_CONSTRUCCION,
    OTRAS_ACTUACIONES_2026,
    REGLAS_URBANISTICAS_PBOT,
    CHECKLIST_TRAMITES,
    CESIONES_URBANISTICAS_PBOT,
    PLUSVALIA_Y_APROVECHAMIENTOS_NORMA
)
from core.calculos import (
    calcular_delineacion_construccion,
    calcular_urbanizacion_o_parcelacion,
    calcular_subdivision_o_reloteo,
    calcular_cesiones_urbanisticas,
    calcular_plusvalia_urbanistica,
    verificar_parametros_urbanisticos
)
from core.cartografia import analizar_archivo_cartografico, analizar_pdf_plano
from core.gestor_expedientes import (
    inicializar_bd,
    crear_o_actualizar_expediente,
    eliminar_expediente_completo,
    listar_expedientes,
    guardar_documento_expediente,
    eliminar_documento_expediente,
    listar_documentos_expediente,
    generar_informe_tecnico_markdown,
    generar_informe_tecnico_docx
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
        "1. Consulta Normativa, Cesiones y Tarifas",
        "2. Calculadora Integral (Licencias, Cesiones y Plusvalía)",
        "3. Verificación Técnica de Planos",
        "4. Gestión de Expedientes, Vista Previa y Eliminación",
        "5. Generación de Informes Oficiales (Word / MD)",
        "6. Análisis Cartográfico (GeoJSON / SHP / PDF)"
    ]
)

# -------------------------------------------------------------------------
# MÓDULO 1: CONSULTA NORMATIVA, CESIONES URBANÍSTICAS, PLUSVALÍA Y TARIFAS
# -------------------------------------------------------------------------
if menu == "1. Consulta Normativa, Cesiones y Tarifas":
    st.header("📚 Buscador de Norma Local (PBOT / Decreto 152/2018), Cesiones y Tarifas 2026")
    termino = st.text_input("Buscar por palabra clave (ej. cesión, tipo A, equipamiento, plusvalía, ochava, andén, Cimarronas, ICANH, rural):")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Reglas Urbanísticas PBOT",
        "Cesiones Urbanísticas (Tipos y %)",
        "Plusvalía y Aprovechamientos",
        "Tarifas Delineación 2026",
        "Otras Actuaciones 2026"
    ])

    with tab1:
        for r in REGLAS_URBANISTICAS_PBOT:
            texto_busqueda = f"{r['categoria']} {r['norma']} {r['regla']}".lower()
            if not termino or termino.lower() in texto_busqueda:
                with st.expander(f"📌 {r['categoria']} — ({r['norma']})", expanded=bool(termino)):
                    st.write(r["regla"])

    with tab2:
        st.subheader("🌳 Régimen de Cesiones Urbanísticas Obligatorias (PBOT / Decreto 152 de 2018 / Ley 388 de 1997)")
        st.caption("Detalle de tipos de cesión, porcentajes normativos, fórmulas de cálculo y reglas de entrega o compensación.")
        for c in CESIONES_URBANISTICAS_PBOT:
            txt_c = f"{c['tipo']} {c['ambito']} {c['norma']} {c['porcentaje_referencia']} {c['criterios_calculo']}".lower()
            if not termino or termino.lower() in txt_c:
                with st.expander(f"📐 {c['tipo']} | Porcentaje: {c['porcentaje_referencia']}", expanded=True):
                    st.markdown(f"**Ámbito de aplicación:** {c['ambito']}")
                    st.markdown(f"**Sustento normativo:** {c['norma']}")
                    st.markdown(f"**Porcentaje normativo de referencia:** `{c['porcentaje_referencia']}`")
                    st.info(f"**Fórmula de cálculo:** `{c['formula']}`")
                    st.markdown("**Procedimiento y criterios técnicos de cálculo:**")
                    st.text(c["criterios_calculo"])

    with tab3:
        st.subheader("📈 Participación en Plusvalía y Mayores Aprovechamientos Urbanísticos")
        st.markdown(f"**Marco legal:** {PLUSVALIA_Y_APROVECHAMIENTOS_NORMA['fundamento_legal']}")
        st.info(f"**Tarifa de Participación Municipal:** {PLUSVALIA_Y_APROVECHAMIENTOS_NORMA['tarifa_participacion_municipal']}")
        st.markdown("### Hechos Generadores de Plusvalía (Art. 74 Ley 388 de 1997)")
        for hg in PLUSVALIA_Y_APROVECHAMIENTOS_NORMA["hechos_generadores"]:
            st.markdown(f"- **[{hg['codigo']}] {hg['nombre']}:** {hg['descripcion']}")
        st.markdown("### Fórmulas de Liquidación")
        for fm in PLUSVALIA_Y_APROVECHAMIENTOS_NORMA["formulas"]:
            st.code(fm)

    with tab4:
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

    with tab5:
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
# MÓDULO 2: CALCULADORA INTEGRAL (LICENCIAS, CESIONES Y PLUSVALÍA)
# -------------------------------------------------------------------------
elif menu == "2. Calculadora Integral (Licencias, Cesiones y Plusvalía)":
    st.header("🧮 Calculadora Urbanística y Tributaria Integral (Vigencia 2026)")

    tipo_calc = st.selectbox(
        "Seleccione la función de cálculo:",
        [
            "1. Impuesto de Delineación (Construcción / Reforma / Adición / Reconocimiento)",
            "2. Derechos de Licencia de Urbanización o Parcelación",
            "3. Derechos de Licencia de Subdivisión Predial o Reloteo",
            "4. Cálculo de Cesiones Urbanísticas Obligatorias y Compensación (m² y $)",
            "5. Cálculo de Participación en Plusvalía y Mayores Aprovechamientos ($)",
            "6. Otras Actuaciones (Alineamiento, Norma, Uso, Propiedad Horizontal, etc.)"
        ]
    )

    if tipo_calc.startswith("1."):
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

    elif tipo_calc.startswith("2."):
        col1, col2 = st.columns(2)
        with col1:
            subtipo = st.radio("Tipo de Licencia:", ["urbanizacion", "parcelacion"], format_func=lambda x: "Urbanización (10% SMLDV)" if x == "urbanizacion" else "Parcelación (2,5% SMLDV)")
            area_bruta = st.number_input("Área Bruta del Predio (m²):", min_value=1.0, value=2730.82, step=10.0)
        with col2:
            descuentos = st.number_input("Descuento por Retiros Ambientales y Vías Obligadas PBOT (m²):", min_value=0.0, value=0.0, step=10.0)

        res = calcular_urbanizacion_o_parcelacion(subtipo, area_bruta, descuentos)
        st.success(f"### Total a Liquidar: ${res['total_pagar']:,.0f} COP")
        st.json(res)

    elif tipo_calc.startswith("3."):
        mod_sub = st.selectbox("Modalidad:", ["subdivision_urbana", "subdivision_rural", "reloteo"])
        if mod_sub != "reloteo":
            unidades = st.number_input("Número de unidades resultantes:", min_value=2, value=2, step=1)
            res = calcular_subdivision_o_reloteo(mod_sub, num_unidades=unidades)
        else:
            area_u = st.number_input("Área útil urbanizable (m²):", min_value=1.0, value=850.0, step=10.0)
            res = calcular_subdivision_o_reloteo(mod_sub, area_util_m2=area_u)
        st.success(f"### Total a Liquidar: ${res['total_pagar']:,.0f} COP")
        st.json(res)

    elif tipo_calc.startswith("4."):
        st.subheader("🌳 Calculadora de Cesiones Urbanísticas Obligatorias y Compensación")
        c_ces1, c_ces2 = st.columns(2)
        with c_ces1:
            ab_ces = st.number_input("Área Bruta del Predio (m²):", min_value=1.0, value=10000.0, step=50.0)
            desc_ces = st.number_input("Afectaciones no computables (Retiros hídricos, riesgo, vías obligadas PBOT) (m²):", min_value=0.0, value=1200.0, step=10.0)
            pct_ep = st.selectbox(
                "Porcentaje Cesión Espacio Público / Zonas Verdes (% del Área Neta):",
                [15.0, 17.0, 18.0, 20.0, 22.0, 25.0],
                index=1
            )
            pct_eq = st.selectbox(
                "Porcentaje Cesión Equipamientos Colectivos (% del Área Neta):",
                [0.0, 2.0, 3.0, 4.0, 5.0, 8.0],
                index=2
            )
        with c_ces2:
            vias_loc = st.number_input("Área de Cesión Vial Local proyectada (m²):", min_value=0.0, value=1100.0, step=10.0)
            an_preview = max(0.0, ab_ces - desc_ces)
            cesion_req_preview = round(an_preview * ((pct_ep + pct_eq) / 100.0), 2)
            entrega_sitio = st.number_input(
                "Área de Cesión Tipo A efectivamente entregada en sitio (m²):",
                min_value=0.0,
                value=cesion_req_preview,
                step=10.0
            )
            valor_m2_urb = st.number_input(
                "Avalúo comercial del m² urbanizado para compensación (COP/m²):",
                min_value=0.0,
                value=450000.0,
                step=10000.0
            )

        res_ces = calcular_cesiones_urbanisticas(
            ab_ces, desc_ces, pct_ep, pct_eq, vias_loc, entrega_sitio, valor_m2_urb
        )

        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        m_c1.metric("Área Neta Urbanizable", f"{res_ces['area_neta_urbanizable_m2']:,.2f} m²")
        m_c2.metric("Cesión Tipo A Total", f"{res_ces['total_cesion_tipo_a_obligatoria_m2']:,.2f} m²")
        m_c3.metric("Área Útil Resultante", f"{res_ces['area_util_resultante_m2']:,.2f} m²")
        m_c4.metric("Compensación Faltante", f"${res_ces['valor_compensacion_dinero']:,.0f}")

        st.json(res_ces)

    elif tipo_calc.startswith("5."):
        st.subheader("📈 Calculadora de Participación en Plusvalía y Mayores Aprovechamientos")
        st.caption("Liquidación conforme a Ley 388 de 1997 (Arts. 73-90), Acuerdo 012 de 2017 (PBOT) y Acuerdo 019 de 2020.")

        p_col1, p_col2 = st.columns(2)
        with p_col1:
            hecho_gen = st.selectbox(
                "Hecho Generador de Plusvalía:",
                [
                    "HG-1: Incorporación de suelo rural a expansión urbana o clasificación suburbana",
                    "HG-2: Modificación del régimen o zonificación de usos del suelo (uso más rentable)",
                    "HG-3: Autorización de mayor aprovechamiento del suelo en edificación (IC / IO / Altura)",
                    "HG-4: Ejecución de obras públicas previstas en el PBOT (sin contribución de valorización)"
                ]
            )
            area_benef = st.number_input("Área Neta Beneficiada del Predio (m²):", min_value=1.0, value=2500.0, step=50.0)
            v1_m2 = st.number_input("Valor Comercial del suelo ANTES de la acción urbanística V1 (COP/m²):", min_value=0.0, value=180000.0, step=10000.0)
            v2_m2 = st.number_input("Valor Comercial del suelo DESPUÉS de la acción urbanística V2 (COP/m²):", min_value=0.0, value=320000.0, step=10000.0)

        with p_col2:
            pct_mayor_aprov = st.selectbox(
                "Porcentaje de Mayor Aprovechamiento Urbanístico Adicional (%):",
                [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 75.0, 100.0],
                index=0,
                help="Seleccione el % de mayor aprovechamiento adicional autorizado cuando se liquide por incremento porcentual de aprovechamiento sobre el valor base."
            )
            pct_part_muni = st.selectbox(
                "Tarifa de Participación Municipal en Plusvalía (% Ley 388/97 Art. 79):",
                [30.0, 35.0, 40.0, 45.0, 50.0],
                index=0
            )
            ic_base = st.number_input("Índice de Construcción (IC) Base:", min_value=0.1, value=1.5, step=0.1)
            ic_nuevo = st.number_input("Índice de Construcción (IC) Nuevo / Aprobado:", min_value=0.1, value=2.2, step=0.1)

        res_plus = calcular_plusvalia_urbanistica(
            hecho_gen, area_benef, v1_m2, v2_m2, pct_part_muni, pct_mayor_aprov, ic_base, ic_nuevo
        )

        st.success(f"### Participación en Plusvalía a Pagar: ${res_plus['participacion_plusvalia_pagar']:,.0f} COP")
        mp1, mp2, mp3 = st.columns(3)
        mp1.metric("Incremento ΔV por m²", f"${res_plus['incremento_precio_suelo_delta_v_m2']:,.0f}/m²")
        mp2.metric("Efecto Plusvalía Total", f"${res_plus['efecto_plusvalia_total']:,.0f}")
        mp3.metric("m² Adicionales por IC", f"{res_plus['m2_adicionales_por_ic']:,.2f} m²")
        st.json(res_plus)

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
# MÓDULO 4: GESTIÓN DE EXPEDIENTES, VISTA PREVIA DOCUMENTAL Y ELIMINACIÓN
# -------------------------------------------------------------------------
elif menu == "4. Gestión de Expedientes, Vista Previa y Eliminación":
    st.header("🗂️ Radicación, Lista de Chequeo, Vista Previa y Administración de Expedientes")

    # Selector de expedientes existentes para cargar, modificar o eliminar trámites
    expedientes_existentes = listar_expedientes()
    with st.expander("📂 Expedientes Radicados (Cargar para Modificar o Eliminar Trámite)", expanded=bool(expedientes_existentes)):
        if expedientes_existentes:
            st.dataframe(
                [
                    {
                        "Radicado": e["radicado"],
                        "Fecha": e["fecha_radicacion"],
                        "Trámite": e["tipo_tramite"],
                        "Titular": e["titular_nombre"],
                        "Estado": e["estado"],
                        "Liquidado": f"${e['valor_liquidado']:,.0f}"
                    }
                    for e in expedientes_existentes
                ],
                use_container_width=True
            )
            col_del_exp1, col_del_exp2 = st.columns([3, 1])
            with col_del_exp1:
                rad_eliminar = st.selectbox(
                    "Seleccione un expediente/trámite si desea eliminarlo del sistema:",
                    [e["radicado"] for e in expedientes_existentes],
                    key="sel_del_exp"
                )
            with col_del_exp2:
                st.write("")
                st.write("")
                if st.button("🗑️ Eliminar Trámite Completo", type="primary"):
                    if eliminar_expediente_completo(rad_eliminar):
                        st.success(f"Trámite y documentos del radicado '{rad_eliminar}' eliminados correctamente.")
                        st.rerun()
        else:
            st.info("No hay expedientes radicados todavía.")

    st.divider()
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
    st.subheader("📎 Cargar, Previsualizar y Eliminar Documentos del Expediente Digital")
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
    archivo_subido = st.file_uploader("Seleccione archivo (PDF, DWG, GEOJSON, JSON, ZIP, JPG, PNG, DOC, DOCX, TXT):", type=["pdf", "dwg", "geojson", "json", "zip", "jpg", "jpeg", "png", "doc", "docx", "txt"])
    nota_doc = st.text_input("Nota del documento (ej. Versión corregida tras acta de observaciones):")

    if st.button("📤 Subir Archivo al Expediente"):
        if archivo_subido is not None and radicado:
            guardar_documento_expediente(radicado, cat_doc, archivo_subido.name, archivo_subido.getvalue(), nota_doc)
            st.success(f"Archivo '{archivo_subido.name}' almacenado en el expediente {radicado}.")
            st.rerun()
        else:
            st.warning("Ingrese el número de radicado y seleccione un archivo.")

    if radicado:
        docs_actuales = listar_documentos_expediente(radicado)
        if docs_actuales:
            st.markdown(f"### 👁️ Documentos Cargados en el Radicado `{radicado}` (Vista Previa y Eliminación)")
            st.dataframe(
                [
                    {
                        "ID": d["id"],
                        "Categoría": d["categoria"],
                        "Archivo": d["nombre_archivo"],
                        "Fecha Carga": d["fecha_carga"],
                        "Nota": d["observacion"]
                    }
                    for d in docs_actuales
                ],
                use_container_width=True
            )

            opciones_docs = {
                f"ID {d['id']} — {d['nombre_archivo']} ({d['categoria']})": d
                for d in docs_actuales
            }
            doc_sel_label = st.selectbox("Seleccione un documento cargado para Vista Previa o Eliminación:", list(opciones_docs.keys()))
            doc_sel = opciones_docs[doc_sel_label]

            c_doc_btn1, c_doc_btn2 = st.columns([1, 3])
            with c_doc_btn1:
                if st.button("🗑️ Eliminar Documento Seleccionado"):
                    if eliminar_documento_expediente(doc_sel["id"]):
                        st.success(f"Documento '{doc_sel['nombre_archivo']}' eliminado.")
                        st.rerun()

            ruta_archivo = doc_sel.get("ruta_guardada", "")
            if ruta_archivo and os.path.exists(ruta_archivo):
                with open(ruta_archivo, "rb") as f_prev:
                    bytes_doc = f_prev.read()

                with c_doc_btn2:
                    st.download_button(
                        label=f"⬇️ Descargar '{doc_sel['nombre_archivo']}'",
                        data=bytes_doc,
                        file_name=doc_sel["nombre_archivo"],
                        key=f"dl_doc_{doc_sel['id']}"
                    )

                st.markdown("#### Vista Previa del Documento")
                nombre_low = doc_sel["nombre_archivo"].lower()
                if nombre_low.endswith(".pdf"):
                    try:
                        st.pdf(bytes_doc)
                    except Exception:
                        b64_pdf = base64.b64encode(bytes_doc).decode("utf-8")
                        st.markdown(f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="550px"></iframe>', unsafe_allow_html=True)
                elif nombre_low.endswith((".png", ".jpg", ".jpeg")):
                    st.image(bytes_doc, caption=doc_sel["nombre_archivo"], use_container_width=True)
                elif nombre_low.endswith((".txt", ".json", ".geojson", ".md", ".csv")):
                    st.code(bytes_doc.decode("utf-8", errors="ignore"))
                elif nombre_low.endswith(".docx"):
                    try:
                        import io
                        from docx import Document
                        d_word = Document(io.BytesIO(bytes_doc))
                        parrafos = [p.text for p in d_word.paragraphs if p.text.strip()]
                        st.text_area("Contenido de vista previa (.docx):", "\n".join(parrafos), height=300)
                    except Exception as e_docx:
                        st.info(f"Archivo Word disponible para descarga ({e_docx}).")
                else:
                    st.info("Vista previa directa disponible para archivos PDF, imágenes (JPG/PNG), Word (.docx) y texto/GeoJSON. Para DWG/ZIP use el botón de descarga.")
            else:
                st.warning("El archivo físico no se encuentra en el servidor temporal; puede eliminarlo de la lista y volverlo a cargar.")

# -------------------------------------------------------------------------
# MÓDULO 5: GENERACIÓN DE INFORMES OFICIALES (WORD EDITABLE Y MARKDOWN)
# -------------------------------------------------------------------------
elif menu == "5. Generación de Informes Oficiales (Word / MD)":
    st.header("📄 Generación de Acta de Observaciones / Concepto Técnico Oficial")
    expedientes = listar_expedientes()
    if not expedientes:
        st.info("Aún no hay expedientes guardados. Cree uno en el Módulo 4.")
    else:
        opciones = {f"{e['radicado']} — {e['titular_nombre']} ({e['estado']})": e for e in expedientes}
        sel_label = st.selectbox("Seleccione el expediente:", list(opciones.keys()))
        exp_sel = opciones[sel_label]
        docs_sel = listar_documentos_expediente(exp_sel["radicado"])

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            try:
                docx_bytes = generar_informe_tecnico_docx(exp_sel, docs_sel)
                st.download_button(
                    label="📘 Descargar Informe Oficial en Word Editable (.docx)",
                    data=docx_bytes,
                    file_name=f"Informe_Tecnico_{exp_sel['radicado']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary"
                )
            except Exception as e_w:
                st.error(f"Error generando Word (.docx): {e_w}")

        with col_dl2:
            informe_md = generar_informe_tecnico_markdown(exp_sel, docs_sel)
            st.download_button(
                label="⬇️ Descargar Informe en Texto / Markdown (.md)",
                data=informe_md.encode("utf-8"),
                file_name=f"Informe_Tecnico_{exp_sel['radicado']}.md",
                mime="text/markdown"
            )

        st.divider()
        st.subheader("Vista Previa del Informe Técnico")
        st.markdown(informe_md)

# -------------------------------------------------------------------------
# MÓDULO 6: ANÁLISIS CARTOGRÁFICO (GEOJSON / SHP / PDF)
# -------------------------------------------------------------------------
elif menu == "6. Análisis Cartográfico (GeoJSON / SHP / PDF)":
    st.header("🗺️ Análisis y Visualización Cartográfica (GeoJSON, Shapefile .ZIP y PDF)")
    st.caption("Suba un archivo vectorial (.geojson, .json o .zip con Shapefile .shp/.dbf/.prj) para calcular áreas/longitudes, visualizar en mapa y cruzar con capas; o suba un .pdf de plano/cartografía para inspeccionarlo y visualizarlo.")

    modo_geo = st.radio(
        "Seleccione el tipo de archivo a analizar:",
        ["Capa Vectorial (GeoJSON o Shapefile .ZIP)", "Plano / Cartografía en PDF (.pdf)"]
    )

    if modo_geo == "Capa Vectorial (GeoJSON o Shapefile .ZIP)":
        c_up1, c_up2 = st.columns(2)
        with c_up1:
            geo_proyecto = st.file_uploader("1. Archivo del Proyecto (.geojson, .json o .zip con Shapefile):", type=["geojson", "json", "zip"])
        with c_up2:
            geo_referencia = st.file_uploader("2. Capa GeoJSON de Referencia / Restricción (opcional):", type=["geojson", "json"])

        if geo_proyecto is not None:
            try:
                resultado_geo = analizar_archivo_cartografico(
                    geo_proyecto.name,
                    geo_proyecto.getvalue(),
                    geo_referencia.getvalue() if geo_referencia is not None else None
                )

                m1, m2, m3 = st.columns(3)
                m1.metric("Elementos Cartográficos", resultado_geo["num_elementos"])
                m2.metric("Área Polígonos (m²)", f"{resultado_geo['area_total_m2']:,.2f}")
                m3.metric("Longitud Líneas (m)", f"{resultado_geo['longitud_total_m']:,.2f}")

                if resultado_geo.get("prj_info"):
                    st.info(f"**Sistema de referencia (.prj) detectado:** {resultado_geo['prj_info']}")

                if resultado_geo.get("es_proyectada_metros"):
                    st.warning("Las coordenadas del archivo parecen estar en metros proyectados (por ejemplo MAGNA-SIRGAS / CTM12) en vez de latitud/longitud grados; para verlas sobre el mapa base de Streamlit conviene exportarlas en EPSG:4326 (WGS84).")
                elif resultado_geo["coordenadas_mapa"]:
                    st.subheader("📍 Visualización en Mapa")
                    st.map(resultado_geo["coordenadas_mapa"])

                st.subheader("📐 Detalle por Elemento")
                st.dataframe(resultado_geo["elementos"], use_container_width=True)

                if resultado_geo["reglas_aplicables"]:
                    st.subheader("⚖️ Alertas Normativas por Área / Magnitud")
                    for rg in resultado_geo["reglas_aplicables"]:
                        if rg["nivel"] == "ALERTA":
                            st.warning(rg["regla"])
                        else:
                            st.info(rg["regla"])

                if geo_referencia is not None:
                    st.subheader("🔎 Resultado de Cruce con Capa de Referencia")
                    if resultado_geo["intersecciones_capa_referencia"]:
                        for inter in resultado_geo["intersecciones_capa_referencia"]:
                            st.error(f"⚠️ {inter['detalle']}")
                    else:
                        st.success("✅ Ningún vértice del proyecto cae dentro de los polígonos de la capa de referencia cargada.")

            except Exception as e:
                st.error(f"No se pudo procesar el archivo cartográfico: {e}")
        else:
            st.info("Sube un archivo `.geojson`, `.json` o `.zip` (con `.shp` y `.dbf`) para calcular áreas, longitudes, visualizar en mapa y cruzar con capas de referencia.")

    else:
        pdf_subido = st.file_uploader("Suba el archivo PDF (.pdf):", type=["pdf"])
        if pdf_subido is not None:
            pdf_bytes = pdf_subido.getvalue()
            info_pdf = analizar_pdf_plano(pdf_bytes)

            p1, p2, p3 = st.columns(3)
            p1.metric("Páginas Estimadas", info_pdf["num_paginas_estimadas"])
            p2.metric("Tamaño Archivo", f"{info_pdf['tamano_kb']:,.1f} KB")
            p3.metric("Marcas GeoPDF / CRS", "Detectadas" if info_pdf["tiene_marcas_geoespaciales_pdf"] else "No detectadas")

            if not info_pdf["tiene_marcas_geoespaciales_pdf"]:
                st.info("Nota: Un PDF estándar o plano en PDF no trae coordenadas vectoriales editables como GeoJSON/Shapefile, pero puedes visualizarlo aquí mismo y extraer su texto/rótulos. Si necesitas medir áreas exactas o cruzar capas en el mapa, exporta el polígono desde QGIS o Google Earth a GeoJSON o Shapefile (.zip).")

            st.subheader("📄 Vista del PDF")
            try:
                st.pdf(pdf_bytes)
            except Exception:
                b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
                st.markdown(f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="550px"></iframe>', unsafe_allow_html=True)

            if info_pdf["muestra_texto_detectado"]:
                st.subheader("📝 Texto / Rótulos Detectados en el PDF")
                st.write(info_pdf["muestra_texto_detectado"])
