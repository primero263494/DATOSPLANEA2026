# -*- coding: utf-8 -*-
"""
Motor de Cálculos Urbanísticos y Tributarios - Vigencia 2026
Municipio de El Carmen de Viboral (Decreto 001 de 2026 / Acuerdo 019 de 2020 / Decreto 152 de 2018)
"""

import math
from data.normativa_carmen import (
    PARAMETROS_2026,
    TARIFAS_DELINEACION_2026,
    FACTOR_MODALIDAD_CONSTRUCCION,
    OTRAS_ACTUACIONES_2026
)

def aproximar_milaje_superior(valor: float) -> int:
    """Artículo Segundo Decreto 001/2026: Aproximación al millaje superior siguiente."""
    if valor <= 0:
        return 0
    return int(math.ceil(valor / 1000.0) * 1000)

def calcular_delineacion_construccion(
    uso_clave: str,
    area_m2: float,
    modalidad_clave: str = "obra_nueva",
    usar_valor_ajustado_tabla: bool = True
) -> dict:
    """
    Calcula el Impuesto de Delineación Urbana/Rural para licencias de construcción,
    reformas, adiciones, cambio de techo por losa o reconocimientos.
    """
    tarifa_info = TARIFAS_DELINEACION_2026[uso_clave]
    modalidad_info = FACTOR_MODALIDAD_CONSTRUCCION[modalidad_clave]

    uvt = PARAMETROS_2026["uvt"]
    valor_calculado_m2 = round(tarifa_info["uvt"] * uvt * 0.02)
    tarifa_m2 = tarifa_info["valor_ajustado"] if usar_valor_ajustado_tabla else aproximar_milaje_superior(valor_calculado_m2)

    area_gravable = area_m2 * modalidad_info["factor"]
    total_exacto = area_gravable * tarifa_m2
    total_pagar = aproximar_milaje_superior(total_exacto)

    return {
        "concepto": tarifa_info["nombre"],
        "modalidad": modalidad_info["nombre"],
        "norma": f"{tarifa_info['norma']} | {modalidad_info['norma']}",
        "area_ingresada_m2": area_m2,
        "factor_modalidad": modalidad_info["factor"],
        "area_gravable_m2": round(area_gravable, 2),
        "uvt_base": tarifa_info["uvt"],
        "tarifa_m2_aplicada": tarifa_m2,
        "total_pagar": total_pagar,
        "observacion": tarifa_info["observacion"]
    }

def calcular_urbanizacion_o_parcelacion(tipo: str, area_bruta_m2: float, retiros_y_vias_obligadas_m2: float) -> dict:
    """
    Calcula derechos de Licencia de Urbanización (10% SMLDV * Área Neta)
    o Licencia de Parcelación (2.5% SMLDV * Área Neta).
    """
    area_neta = max(0.0, area_bruta_m2 - retiros_y_vias_obligadas_m2)
    smldv = PARAMETROS_2026["smldv"]

    if tipo == "urbanizacion":
        porcentaje = 0.10
        etiqueta = "Licencia de Urbanización (10% SMLDV x m2 Área Neta)"
    else:
        porcentaje = 0.025
        etiqueta = "Licencia de Parcelación (2,5% SMLDV x m2 Área Neta)"

    valor_m2 = smldv * porcentaje
    total_exacto = area_neta * valor_m2
    total_pagar = aproximar_milaje_superior(total_exacto)

    return {
        "concepto": etiqueta,
        "norma": "Decreto Municipal 001 de 2026 (Pág. 4) / Acuerdo 019 de 2020",
        "area_bruta_m2": area_bruta_m2,
        "descuentos_m2": retiros_y_vias_obligadas_m2,
        "area_neta_urbanizable_m2": round(area_neta, 2),
        "smldv_2026": smldv,
        "tarifa_m2": round(valor_m2, 2),
        "total_pagar": total_pagar
    }

def calcular_subdivision_o_reloteo(modalidad: str, num_unidades: int = 2, area_util_m2: float = 0.0) -> dict:
    """
    Calcula expensas de subdivisión rural/urbana (1 SMMLV por unidad resultante)
    o reloteo según rango de área útil en UVT (Decreto 001/2026).
    """
    if modalidad in ("subdivision_urbana", "subdivision_rural"):
        smmlv = PARAMETROS_2026["smmlv"]
        total = smmlv * num_unidades
        return {
            "concepto": f"Licencia de Subdivisión ({modalidad.replace('_', ' ').title()})",
            "norma": "Decreto Municipal 001 de 2026 / Decreto 1077 de 2015",
            "unidades_resultantes": num_unidades,
            "valor_unitario": smmlv,
            "total_pagar": aproximar_milaje_superior(total)
        }
    else:
        if area_util_m2 <= 1000:
            uvt_tarifa, ajustado = 1.8, 95000
        elif area_util_m2 <= 5000:
            uvt_tarifa, ajustado = 0.4, 21000
        elif area_util_m2 <= 10000:
            uvt_tarifa, ajustado = 0.8, 42000
        elif area_util_m2 <= 20000:
            uvt_tarifa, ajustado = 1.3, 69000
        else:
            uvt_tarifa, ajustado = 1.8, 95000

        return {
            "concepto": "Licencia de Subdivisión - Modalidad Reloteo",
            "norma": "Decreto Municipal 001 de 2026 / Decreto 1077 de 2015",
            "area_util_m2": area_util_m2,
            "uvt_tarifa": uvt_tarifa,
            "total_pagar": ajustado
        }

def verificar_parametros_urbanisticos(
    area_lote_neta_m2: float,
    area_ocupada_primer_piso_m2: float,
    area_total_construida_m2: float,
    ancho_anden_m: float,
    altura_bordillo_m: float,
    es_esquina: bool,
    radio_ochava_m: float,
    pendiente_terreno_pct: float,
    distancia_quebrada_m: float,
    tipo_quebrada: str = "otra"
) -> list:
    """
    Verifica cumplimiento técnico de planos arquitectónicos/urbanísticos frente a
    Acuerdo 012 de 2017 (PBOT) y Decreto 152 de 2018.
    """
    hallazgos = []

    if area_lote_neta_m2 > 0:
        io = area_ocupada_primer_piso_m2 / area_lote_neta_m2
        ic = area_total_construida_m2 / area_lote_neta_m2
        hallazgos.append({
            "estado": "INFO",
            "parametro": "Índices Calculados (IO / IC)",
            "detalle": f"Índice de Ocupación (IO) = {io:.2f} | Índice de Construcción (IC) = {ic:.2f}. Contrastar contra ficha normativa del polígono."
        })

    # Verificación de andén (Decreto 152/2018 Arts. 20-21)
    if ancho_anden_m < 1.20:
        hallazgos.append({
            "estado": "NO CUMPLE",
            "parametro": "Ancho libre de andén (Decreto 152/2018 Art. 20)",
            "detalle": f"Andén proyectado de {ancho_anden_m:.2f} m es inferior al mínimo obligatorio de 1,20 m."
        })
    else:
        hallazgos.append({
            "estado": "CUMPLE",
            "parametro": "Ancho libre de andén (Decreto 152/2018 Art. 20)",
            "detalle": f"Andén de {ancho_anden_m:.2f} m cumple con el mínimo de 1,20 m."
        })

    if not (0.15 <= altura_bordillo_m <= 0.20):
        hallazgos.append({
            "estado": "ALERTA",
            "parametro": "Altura de bordillo respecto a calzada (Decreto 152/2018)",
            "detalle": f"Altura ingresada {altura_bordillo_m:.2f} m está fuera del rango normativo (0,15 m a 0,20 m)."
        })

    # Verificación de ochava (Decreto 152/2018 Art. 23)
    if es_esquina:
        if radio_ochava_m < 2.00:
            hallazgos.append({
                "estado": "NO CUMPLE",
                "parametro": "Ochava en predio esquinero (Decreto 152/2018 Art. 23)",
                "detalle": f"Radio de ochava proyectado ({radio_ochava_m:.2f} m) es menor al mínimo reglamentario de 2,00 m en todos los niveles."
            })
        else:
            hallazgos.append({
                "estado": "CUMPLE",
                "parametro": "Ochava en predio esquinero (Decreto 152/2018 Art. 23)",
                "detalle": f"Radio de ochava de {radio_ochava_m:.2f} m cumple (>= 2,00 m)."
            })

    # Verificación de pendientes (Acuerdo 012/2017 / Acuerdo Cornare 265/2011)
    if pendiente_terreno_pct > 75:
        hallazgos.append({
            "estado": "NO CUMPLE",
            "parametro": "Pendiente del terreno (Acuerdo 012/2017 Art. 19)",
            "detalle": f"Pendiente del {pendiente_terreno_pct:.1f}% supera el 75%: Suelo de Protección No Edificable."
        })
    elif 25 <= pendiente_terreno_pct <= 60:
        hallazgos.append({
            "estado": "ALERTA",
            "parametro": "Pendiente del terreno (Acuerdo Cornare 265/2011)",
            "detalle": f"Pendiente del {pendiente_terreno_pct:.1f}% (rango 25%-60%): Exige Plan de Manejo Detallado de Suelos."
        })

    # Verificación retiros hídricos (Acuerdo 012/2017 Art. 18 / Acuerdo Cornare 251/2011)
    if tipo_quebrada == "la_cimarronas" and distancia_quebrada_m < 50:
        hallazgos.append({
            "estado": "ALERTA",
            "parametro": "Retiro Quebrada La Cimarronas (Acuerdo 012/2017 Art. 18)",
            "detalle": f"Distancia ingresada ({distancia_quebrada_m:.1f} m) menor a 50 m (30 m mínimos + 20 m parque lineal, o mancha TR=100 + 20 m)."
        })
    elif tipo_quebrada == "la_madera" and distancia_quebrada_m < 40:
        hallazgos.append({
            "estado": "NO CUMPLE",
            "parametro": "Retiro Quebrada La Madera (Acuerdo 012/2017 Art. 18)",
            "detalle": f"Distancia ingresada ({distancia_quebrada_m:.1f} m) es inferior al retiro constante urbano de 40,0 m."
        })

    return hallazgos


def calcular_cesiones_urbanisticas(
    area_bruta_m2: float,
    retiros_y_vias_obligadas_m2: float,
    pct_cesion_espacio_publico: float = 17.0,
    pct_cesion_equipamiento: float = 3.0,
    area_vias_locales_m2: float = 0.0,
    area_cesion_entregada_sitio_m2: float = None,
    valor_comercial_m2_urbanizado: float = 0.0
) -> dict:
    """
    Calcula las cesiones urbanísticas obligatorias conforme a Ley 388/1997,
    Acuerdo 012/2017 (PBOT) y Decreto 152/2018:
    - Área Neta Urbanizable (AN) = Área Bruta - Afectaciones (retiros hídricos, riesgo, vías obligadas PBOT)
    - Cesión Espacio Público (Tipo A Verde/Parques) = AN * (% / 100)
    - Cesión Equipamientos Colectivos = AN * (% / 100)
    - Área Útil Vendible = AN - Cesión Espacio Público - Cesión Equipamientos - Vías Locales
    - Compensación en dinero (si se entrega menos área en sitio)
    """
    area_neta = max(0.0, area_bruta_m2 - retiros_y_vias_obligadas_m2)
    cesion_ep_m2 = round(area_neta * (pct_cesion_espacio_publico / 100.0), 2)
    cesion_eq_m2 = round(area_neta * (pct_cesion_equipamiento / 100.0), 2)
    total_cesion_tipo_a_m2 = round(cesion_ep_m2 + cesion_eq_m2, 2)
    area_util_m2 = max(0.0, round(area_neta - total_cesion_tipo_a_m2 - area_vias_locales_m2, 2))

    globo_minimo_50_m2 = round(cesion_ep_m2 * 0.50, 2)

    if area_cesion_entregada_sitio_m2 is None:
        area_cesion_entregada_sitio_m2 = total_cesion_tipo_a_m2

    faltante_m2 = max(0.0, round(total_cesion_tipo_a_m2 - area_cesion_entregada_sitio_m2, 2))
    valor_compensacion = aproximar_milaje_superior(faltante_m2 * valor_comercial_m2_urbanizado) if faltante_m2 > 0 else 0

    return {
        "area_bruta_m2": round(area_bruta_m2, 2),
        "descuentos_afectaciones_m2": round(retiros_y_vias_obligadas_m2, 2),
        "area_neta_urbanizable_m2": round(area_neta, 2),
        "pct_espacio_publico": pct_cesion_espacio_publico,
        "cesion_espacio_publico_m2": cesion_ep_m2,
        "globo_minimo_concentrado_50pct_m2": globo_minimo_50_m2,
        "pct_equipamiento": pct_cesion_equipamiento,
        "cesion_equipamiento_m2": cesion_eq_m2,
        "total_cesion_tipo_a_obligatoria_m2": total_cesion_tipo_a_m2,
        "cesion_vias_locales_m2": round(area_vias_locales_m2, 2),
        "area_util_resultante_m2": area_util_m2,
        "area_entregada_en_sitio_m2": round(area_cesion_entregada_sitio_m2, 2),
        "area_faltante_a_compensar_m2": faltante_m2,
        "valor_compensacion_dinero": valor_compensacion
    }

def calcular_plusvalia_urbanistica(
    hecho_generador: str,
    area_neta_beneficiada_m2: float,
    valor_m2_antes_v1: float,
    valor_m2_despues_v2: float,
    pct_participacion_municipal: float = 30.0,
    pct_mayor_aprovechamiento: float = 0.0,
    indice_construccion_base: float = 1.0,
    indice_construccion_nuevo: float = 1.0,
    incidencia_suelo_pct: float = 20.0
) -> dict:
    """
    Calcula el Efecto Plusvalía y la Participación en Plusvalía (Ley 388 de 1997 Arts. 73-90,
    Decreto 1077 de 2015, Acuerdo 012 de 2017 PBOT y Acuerdo 019 de 2020):
    Soporta dos métodos complementarios según la información disponible:
    1) Diferencial directo de avalúo comercial (V2 - V1) por m² de suelo beneficiado.
    2) Cálculo por porcentaje de mayor aprovechamiento (%) o incremento en Índice de Construcción
       aplicado sobre el valor del suelo / incidencia de edificabilidad adicional.
    """
    delta_v_m2 = max(0.0, valor_m2_despues_v2 - valor_m2_antes_v1)

    # Si el usuario selecciona un porcentaje de mayor aprovechamiento adicional o incremento de IC
    m2_base_construibles = area_neta_beneficiada_m2 * indice_construccion_base
    m2_nuevos_construibles = area_neta_beneficiada_m2 * indice_construccion_nuevo
    delta_m2_ic = max(0.0, m2_nuevos_construibles - m2_base_construibles)

    # Factor adicional por porcentaje de mayor aprovechamiento seleccionado en menú desplegable
    efecto_por_avaluos = delta_v_m2 * area_neta_beneficiada_m2

    # Si V2 == V1 pero se ingresó un % de mayor aprovechamiento o incremento de IC, estimar mayor valor generado
    efecto_por_mayor_aprovechamiento = 0.0
    if pct_mayor_aprovechamiento > 0:
        efecto_por_mayor_aprovechamiento = (valor_m2_antes_v1 * (pct_mayor_aprovechamiento / 100.0)) * area_neta_beneficiada_m2
    elif delta_m2_ic > 0 and delta_v_m2 == 0:
        # Valorización por m² adicional edificable según incidencia del suelo
        efecto_por_mayor_aprovechamiento = delta_m2_ic * (valor_m2_antes_v1 / max(indice_construccion_base, 0.1))

    efecto_plusvalia_total = round(efecto_por_avaluos + efecto_por_mayor_aprovechamiento, 2)
    participacion_exacta = efecto_plusvalia_total * (pct_participacion_municipal / 100.0)
    participacion_pagar = aproximar_milaje_superior(participacion_exacta)

    return {
        "hecho_generador": hecho_generador,
        "norma_aplicable": "Ley 388 de 1997 (Arts. 73-90) / Decreto 1077 de 2015 / Acuerdo 012 de 2017 / Acuerdo 019 de 2020",
        "area_neta_beneficiada_m2": round(area_neta_beneficiada_m2, 2),
        "valor_comercial_antes_v1_m2": round(valor_m2_antes_v1, 2),
        "valor_comercial_despues_v2_m2": round(valor_m2_despues_v2, 2),
        "incremento_precio_suelo_delta_v_m2": round(delta_v_m2, 2),
        "pct_mayor_aprovechamiento_aplicado": pct_mayor_aprovechamiento,
        "ic_base": indice_construccion_base,
        "ic_nuevo": indice_construccion_nuevo,
        "m2_adicionales_por_ic": round(delta_m2_ic, 2),
        "efecto_plusvalia_total": efecto_plusvalia_total,
        "tarifa_participacion_municipal_pct": pct_participacion_municipal,
        "participacion_plusvalia_pagar": participacion_pagar
    }
