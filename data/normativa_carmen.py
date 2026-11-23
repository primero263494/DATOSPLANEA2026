# -*- coding: utf-8 -*-
"""
Base de Datos Normativa, Tarifaria y de Requisitos Urbanísticos
Municipio de El Carmen de Viboral (Antioquia)
Fuentes integradas:
- Acuerdo Municipal 012 de 2017 (PBOT)
- Decreto Municipal 152 de 2018 (Manual de Urbanismo y Espacio Público)
- Decreto Municipal 001 del 8 de enero de 2026 (Tarifas Vigencia Fiscal 2026 - UVT $52.374)
- Requisitos Secretaría de Planeación y Desarrollo Territorial (2024-2026)
- Normativa Nacional: Ley 388 de 1997, Ley 400 de 1997 (NSR-10), Decreto 1077 de 2015, Decreto 1203 de 2017, Resolución 1025 de 2021
"""

PARAMETROS_2026 = {
    "anio": 2026,
    "uvt": 52374,
    "resolucion_uvt": "Resolución DIAN N.° 000238 del 15 de diciembre de 2025",
    "decreto_tarifas": "Decreto Municipal 001 del 8 de enero de 2026",
    "smmlv": 1750905,
    "smldv": round(1750905 / 30, 2),
    "regla_redondeo": "Artículo Segundo Decreto 001/2026: Aproximación al millaje superior siguiente cuando hay fracción en centavos o pesos."
}

TARIFAS_DELINEACION_2026 = {
    "residencial_urbano_e1": {
        "nombre": "Uso Residencial Zona Urbana - Estrato 1",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 20.54,
        "valor_exacto": 21515,
        "valor_ajustado": 22000,
        "unidad": "m2 construido",
        "observacion": ""
    },
    "residencial_urbano_e2": {
        "nombre": "Uso Residencial Zona Urbana - Estrato 2",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 32.87,
        "valor_exacto": 34431,
        "valor_ajustado": 35000,
        "unidad": "m2 construido",
        "observacion": ""
    },
    "residencial_urbano_e3": {
        "nombre": "Uso Residencial Zona Urbana - Estrato 3",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 41.09,
        "valor_exacto": 43041,
        "valor_ajustado": 39000,
        "unidad": "m2 construido",
        "observacion": "Nota: En tabla oficial Decreto 001/2026 figura $39.000 (menor al cálculo UVT*2%)."
    },
    "residencial_urbano_e4": {
        "nombre": "Uso Residencial Zona Urbana - Estrato 4",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 53.41,
        "valor_exacto": 55946,
        "valor_ajustado": 56000,
        "unidad": "m2 construido",
        "observacion": ""
    },
    "residencial_urbano_e5": {
        "nombre": "Uso Residencial Zona Urbana - Estrato 5",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 61.63,
        "valor_exacto": 64556,
        "valor_ajustado": 65000,
        "unidad": "m2 construido",
        "observacion": ""
    },
    "residencial_urbano_e6": {
        "nombre": "Uso Residencial Zona Urbana - Estrato 6",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 73.96,
        "valor_exacto": 77472,
        "valor_ajustado": 70000,
        "unidad": "m2 construido",
        "observacion": "Nota: En tabla oficial Decreto 001/2026 figura $70.000 (menor al cálculo UVT*2%)."
    },
    "comercial_urbano": {
        "nombre": "Uso Comercial Urbano",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 82.18,
        "valor_exacto": 86082,
        "valor_ajustado": 87000,
        "unidad": "m2 construido",
        "observacion": ""
    },
    "comercial_rural": {
        "nombre": "Uso Comercial Rural y Suburbano",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 73.96,
        "valor_exacto": 77472,
        "valor_ajustado": 78000,
        "unidad": "m2 construido",
        "observacion": ""
    },
    "industrial_urbano": {
        "nombre": "Uso Industrial y Bodega Urbano",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 82.18,
        "valor_exacto": 86082,
        "valor_ajustado": 87000,
        "unidad": "m2 construido",
        "observacion": ""
    },
    "industrial_rural": {
        "nombre": "Uso Industrial y Bodega Rural y Suburbano",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 123.26,
        "valor_exacto": 129112,
        "valor_ajustado": 117000,
        "unidad": "m2 construido",
        "observacion": "Nota: En tabla oficial Decreto 001/2026 figura $117.000."
    },
    "institucional": {
        "nombre": "Uso Institucional",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 73.96,
        "valor_exacto": 77472,
        "valor_ajustado": 78000,
        "unidad": "m2 construido",
        "observacion": ""
    },
    "recreativo_turistico": {
        "nombre": "Uso Recreativo Turístico",
        "norma": "Art. 180 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 82.18,
        "valor_exacto": 86082,
        "valor_ajustado": 87000,
        "unidad": "m2 construido",
        "observacion": ""
    },
    "vivienda_campesina_tipo_1": {
        "nombre": "Vivienda Rural/Suburbana Dispersa - Habitacional Campesina Tipo 1",
        "norma": "Art. 180 Parágrafo 1 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 32.87,
        "valor_exacto": 34431,
        "valor_ajustado": 35000,
        "unidad": "m2 construido",
        "observacion": "Exige: Predio >= UAF, área construida <= 80 m2, habitación permanente (declaración extrajuicio)."
    },
    "vivienda_campesina_tipo_2": {
        "nombre": "Vivienda Rural/Suburbana Dispersa - Habitacional Campesina Tipo 2 / Mayordomos",
        "norma": "Art. 180 Parágrafos 1 y 2 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 53.41,
        "valor_exacto": 55946,
        "valor_ajustado": 56000,
        "unidad": "m2 construido",
        "observacion": "Exige: Predio <, = o > UAF, área <= 110 m2, habitación permanente, propietario nativo de El Carmen de Viboral y Sisbén A1-C18. Aplica también a vivienda de mayordomos/auxiliares."
    },
    "vivienda_campestre_parcelacion": {
        "nombre": "Vivienda Rural y Suburbana en Parcelaciones, Condominios y Campestre Dispersa",
        "norma": "Art. 180 Parágrafos 3 y 4 Acuerdo 019/2020 - Decreto 001/2026",
        "uvt": 102.72,
        "valor_exacto": 107597,
        "valor_ajustado": 108000,
        "unidad": "m2 construido",
        "observacion": "Aplica por defecto si la vivienda rural no cumple todos los requisitos de Campesina Tipo 1 o Tipo 2."
    }
}

FACTOR_MODALIDAD_CONSTRUCCION = {
    "obra_nueva": {"nombre": "Obra Nueva / Ampliación / Adición / Cambio de Uso (100%)", "factor": 1.00, "norma": "Art. 182 Parágrafo 4 Acuerdo 019/2020"},
    "reforma_general": {"nombre": "Reforma a Planos Aprobados sin subdivisión (25%)", "factor": 0.25, "norma": "Art. 182 Parágrafo 4 Acuerdo 019/2020"},
    "reforma_subdivision": {"nombre": "Reforma con subdivisión en 2 o más unidades (50%)", "factor": 0.50, "norma": "Art. 182 Parágrafo 4 Acuerdo 019/2020"},
    "cambio_techo_losa": {"nombre": "Cambio de techo por losa en construcción legalizada (50%)", "factor": 0.50, "norma": "Art. 182 Parágrafo 4 Acuerdo 019/2020"},
    "reconocimiento": {"nombre": "Reconocimiento de Edificación Existente (100%)", "factor": 1.00, "norma": "Decreto 1077/2015 - Acuerdo 019/2020"}
}

OTRAS_ACTUACIONES_2026 = {
    "alineamiento_hilos": {"nombre": "Informe de Alineamiento (Hilos)", "uvt": 0.8, "valor_ajustado": 42000},
    "concepto_norma": {"nombre": "Concepto de Norma Urbanística", "uvt": 0.8, "valor_ajustado": 42000},
    "concepto_uso_suelo": {"nombre": "Concepto de Uso de Suelo", "uvt": 0.8, "valor_ajustado": 42000},
    "certificado_riesgo": {"nombre": "Certificado de Riesgo de Predios", "uvt": 0.8, "valor_ajustado": 42000},
    "asignacion_nomenclatura": {"nombre": "Asignación de Nomenclatura", "uvt": 0.8, "valor_ajustado": 42000},
    "certificado_estratificacion": {"nombre": "Certificado de Estratificación Socioeconómica", "uvt": 0.5, "valor_ajustado": 27000},
    "propiedad_horizontal_hasta_250": {"nombre": "Aprobación Planos Propiedad Horizontal (Hasta 250 m2)", "uvt": 0.25, "valor_ajustado": 14000},
    "propiedad_horizontal_251_500": {"nombre": "Aprobación Planos Propiedad Horizontal (251 a 500 m2)", "uvt": 0.4, "valor_ajustado": 21000},
    "propiedad_horizontal_501_1000": {"nombre": "Aprobación Planos Propiedad Horizontal (501 a 1.000 m2)", "uvt": 0.8, "valor_ajustado": 42000},
    "propiedad_horizontal_1001_5000": {"nombre": "Aprobación Planos Propiedad Horizontal (1.001 a 5.000 m2)", "uvt": 1.8, "valor_ajustado": 95000},
    "propiedad_horizontal_5001_10000": {"nombre": "Aprobación Planos Propiedad Horizontal (5.001 a 10.000 m2)", "uvt": 2.7, "valor_ajustado": 142000},
    "propiedad_horizontal_10001_20000": {"nombre": "Aprobación Planos Propiedad Horizontal (10.001 a 20.000 m2)", "uvt": 3.6, "valor_ajustado": 189000},
    "propiedad_horizontal_mas_20000": {"nombre": "Aprobación Planos Propiedad Horizontal (Más de 20.000 m2)", "uvt": 4.5, "valor_ajustado": 236000},
    "ajuste_cotas_e1_e2": {"nombre": "Ajuste de Cotas de Áreas (Estratos 1 y 2)", "uvt": 3.6, "valor_ajustado": 189000},
    "ajuste_cotas_e3_e4": {"nombre": "Ajuste de Cotas de Áreas (Estratos 3 y 4)", "uvt": 7.2, "valor_ajustado": 378000},
    "ajuste_cotas_e5_e6": {"nombre": "Ajuste de Cotas de Áreas (Estratos 5 y 6)", "uvt": 10.8, "valor_ajustado": 566000},
}

REGLAS_URBANISTICAS_PBOT = [
    {
        "categoria": "Clasificación del Suelo y Planes Parciales",
        "norma": "Acuerdo 012 de 2017 (Arts. 65-75) / Ley 388 de 1997 / Decreto 1077 de 2015",
        "regla": "Suelo urbano (CG_003), expansión urbana (CG_004: polígonos S1-DE-1 a S1-DE-11, S2-DE-6, S3-DE-7 a S3-DE-10) y rural (CG_016). Suelo de expansión requiere Plan Parcial previo, salvo predios < 2 ha colindantes con perímetro urbano mediante UAU especial."
    },
    {
        "categoria": "Estructura Ecológica Principal (EEP) y Pendientes",
        "norma": "Acuerdo 012 de 2017 (Arts. 15-20) / Acuerdo Cornare 265 de 2011",
        "regla": "Pendientes > 75% son suelo de protección no edificable. Pendientes entre 25% y 60% en suelo urbano/expansión requieren Plan de Manejo Detallado de Suelos."
    },
    {
        "categoria": "Retiros Hídricos Urbanos",
        "norma": "Acuerdo 012 de 2017 (Art. 18) / Acuerdo Cornare 251 de 2011",
        "regla": "Quebrada La Cimarronas en zona urbana: mancha de inundación TR=100 años (mínimo 30 m si la mancha es menor) + 20 m adicionales de amortiguación/parque lineal. Quebrada La Madera en zona urbana: retiro constante de 40 m."
    },
    {
        "categoria": "Amenaza, Riesgo y Geotecnia",
        "norma": "Acuerdo 012 de 2017 (Arts. 56-63) / Decreto 1807 de 2014 / NSR-10 Título H",
        "regla": "Riesgo alto no mitigable es suelo de protección no edificable (planos CG_007 a CG_009, D_014, D_015). Amenaza/riesgo medio o estabilidad condicionada requieren estudios geotécnicos detallados."
    },
    {
        "categoria": "Patrimonio Cultural y Arqueología Preventiva",
        "norma": "Acuerdo 012 de 2017 (Arts. 38-51) / Decreto-Ley 763 de 2009 / Decreto 1080 de 2015",
        "regla": "BIC municipales/nacionales, damero fundacional (8 manzanas alrededor del parque principal) y sitio arqueológico El Pedrero tienen lineamientos estéticos/patrimoniales. Predios >= 10.000 m2 (1 ha) en urbanismo/parcelación exigen radicado ante ICANH."
    },
    {
        "categoria": "Redes de Servicios Públicos y RETIE",
        "norma": "Acuerdo 012 de 2017 (Arts. 22-25, 89-96) / Resolución RETIE",
        "regla": "Retiro mínimo de 2 m a redes primarias/secundarias de acueducto y alcantarillado; 200 m de PTAR Villa María a zonas residenciales; franjas de servidumbre eléctrica según tensión."
    },
    {
        "categoria": "Secciones Viales, Vías sin Salida e Intersecciones",
        "norma": "Decreto Municipal 152 de 2018 (Arts. 11-23) / Acuerdo 012 de 2017 (Art. 78)",
        "regla": "Vías sin salida: longitud máxima 80 m con retorno circular de 16 m de diámetro (punto fijo central) o rectangular de 9 m x 18 m. Ángulo de intersección: 60° a 90°. Distancia mínima entre ejes contiguos: 33 m."
    },
    {
        "categoria": "Ochavas en Predios Esquineros",
        "norma": "Decreto Municipal 152 de 2018 (Art. 23)",
        "regla": "En esquinas la edificación debe retroceder o redondear el paramento con radio mínimo de 2,00 m (sin reducir andén ni zona verde), conservándose en todos los pisos y actuando como paramento para voladizos."
    },
    {
        "categoria": "Andenes y Accesibilidad Universal",
        "norma": "Decreto Municipal 152 de 2018 (Arts. 20-21) / NTC 4143 / Decreto 1538 de 2005",
        "regla": "Andén obligatorio en todo el frente del lote como requisito para conexión de servicios públicos. Ancho libre mínimo: 1,20 m. Altura bordillo: 0,15 m a 0,20 m (0,20 m en vías arterias). Rampas en esquina con retiro de 3,00 m, ancho 1,20 m y loseta táctil. Gradas si pendiente > 16% (2c + h = 0,64 m; c máx 0,18 m; h mín 0,28 m)."
    },
    {
        "categoria": "Alturas, Sótanos y Semisótanos",
        "norma": "Decreto Municipal 152 de 2018 / Acuerdo 012 de 2017",
        "regla": "Semisótano no puede sobresalir más de 1,50 m sobre el nivel más bajo del terreno. Índices de ocupación y construcción se calculan sobre área neta/útil descontando retiros y vías obligadas."
    }
]

CHECKLIST_TRAMITES = {
    "construccion_urbana": {
        "nombre": "Licencia de Construcción - Zona Urbana",
        "norma_base": "Decreto 1077 de 2015 (Art. 2.2.6.1.2.1.7) / Resolución 1025 de 2021 / Requisitos Planeación El Carmen",
        "items": [
            {"id": "CU-01", "categoria": "Jurídico", "requisito": "Formulario Único Nacional (FUN) debidamente diligenciado y firmado por titulares", "obligatorio": True},
            {"id": "CU-02", "categoria": "Jurídico", "requisito": "Certificado de Tradición y Libertad vigente (expedición <= 30 días)", "obligatorio": True},
            {"id": "CU-03", "categoria": "Jurídico", "requisito": "Fotocopia de la Escritura Pública del predio", "obligatorio": True},
            {"id": "CU-04", "categoria": "Jurídico", "requisito": "Paz y Salvo Municipal de Impuesto Predial vigente (expedición <= 30 días)", "obligatorio": True},
            {"id": "CU-05", "categoria": "Jurídico", "requisito": "Fotocopia de cédula de cada propietario (y Certificado Cámara de Comercio <= 30 días si es persona jurídica)", "obligatorio": True},
            {"id": "CU-06", "categoria": "Jurídico", "requisito": "Poder con firma original (si no radica el titular) y autorización original de notificación electrónica", "obligatorio": True},
            {"id": "CU-07", "categoria": "Publicidad", "requisito": "Fotografía de la valla informativa instalada en el predio y relación de vecinos colindantes", "obligatorio": True},
            {"id": "CU-08", "categoria": "Urbanístico", "requisito": "Informe de Alineamiento (Hilos) y/o factibilidades de energía (EPM) y acueducto/alcantarillado (La Cimarrona ESP)", "obligatorio": True},
            {"id": "CU-09", "categoria": "Urbanístico", "requisito": "Autorización de la copropiedad / acta de asamblea (si el predio está sometido a Propiedad Horizontal)", "obligatorio": False},
            {"id": "CU-10", "categoria": "Técnico", "requisito": "3 copias físicas de diseños arquitectónicos firmados (plantas, cortes, fachadas, cubierta, cuadro de áreas, andén 1,20 m y ochava si es esquina)", "obligatorio": True},
            {"id": "CU-11", "categoria": "Técnico", "requisito": "3 copias físicas de diseños estructurales (NSR-10), memorias de cálculo, formato de memorias y formato de revisión estructural", "obligatorio": True},
            {"id": "CU-12", "categoria": "Técnico", "requisito": "Estudio de suelos NSR-10 Título H (obligatorio 3 a 6+ pisos) o informe de apique (edificaciones de 1 a 2 niveles)", "obligatorio": True},
            {"id": "CU-13", "categoria": "Técnico", "requisito": "Planos hidrosanitarios y de desagües pluviales/sanitarios", "obligatorio": True},
            {"id": "CU-14", "categoria": "Ambiental", "requisito": "Plan de Manejo Ambiental para movimiento de escombros (RCD) y movimiento de tierras", "obligatorio": True},
            {"id": "CU-15", "categoria": "Profesionales", "requisito": "Copia de matrícula profesional vigente, cédula y certificados de experiencia de los profesionales responsables + medio magnético (DWG/PDF) en bolsa resellable", "obligatorio": True},
        ]
    },
    "construccion_rural": {
        "nombre": "Licencia de Construcción - Zona Rural / Suburbana",
        "norma_base": "Decreto 1077 de 2015 / Acuerdo 012 de 2017 / Requisitos Planeación El Carmen",
        "items": [
            {"id": "CR-01", "categoria": "Jurídico", "requisito": "Formulario Único Nacional (FUN), Certificado de Tradición (<= 30 días), Escritura y Paz y Salvo Municipal (<= 30 días)", "obligatorio": True},
            {"id": "CR-02", "categoria": "Jurídico", "requisito": "Cédulas de propietarios, Cámara de Comercio (<= 30 días si aplica), poder original y autorización notificación electrónica original", "obligatorio": True},
            {"id": "CR-03", "categoria": "Publicidad", "requisito": "Fotografía de la valla informativa instalada en el predio", "obligatorio": True},
            {"id": "CR-04", "categoria": "Urbanístico", "requisito": "Informe de alineamiento y/o factibilidades de servicios públicos (EPM y acueducto veredal)", "obligatorio": True},
            {"id": "CR-05", "categoria": "Urbanístico", "requisito": "Si es parcelación: aprobación de diseños según Reglamento de Copropiedad expedida por administración (anexar copia planos aprobados en hoja oficio)", "obligatorio": False},
            {"id": "CR-06", "categoria": "Técnico", "requisito": "Estudio de suelos NSR-10 (obligatorio si área >= 300 m2, 2 pisos + mansarda, PH o parcelación; apique para 1-2 pisos sin mansarda)", "obligatorio": True},
            {"id": "CR-07", "categoria": "Técnico", "requisito": "3 copias de diseños arquitectónicos, 3 copias de diseños estructurales, memorias de cálculo y formatos de revisión", "obligatorio": True},
            {"id": "CR-08", "categoria": "Ambiental", "requisito": "Diseño estructural de Pozo Séptico (o ficha técnica si es prefabricado) y permiso de vertimientos expedido por CORNARE", "obligatorio": True},
            {"id": "CR-09", "categoria": "Técnico", "requisito": "Planos hidrosanitarios y desagües (verificando rótulo correcto del municipio), medio magnético y matrículas profesionales en bolsa resellable", "obligatorio": True},
            {"id": "CR-10", "categoria": "Tributario", "requisito": "Si solicita tarifa Vivienda Campesina Tipo 1 o 2: Declaración extrajuicio de habitación permanente, verificación UAF, Sisbén A1-C18 y certificado de nacimiento/nativo (Tipo 2)", "obligatorio": False},
        ]
    },
    "urbanismo_vias": {
        "nombre": "Licencia de Urbanización / Desarrollo Vial",
        "norma_base": "Decreto 1077 de 2015 / Acuerdo 012 de 2017 / Decreto 152 de 2018 / Requisitos Planeación El Carmen",
        "items": [
            {"id": "UR-01", "categoria": "Jurídico", "requisito": "FUN, Certificado de Tradición (<= 30 días), Escritura Pública y Paz y Salvo Predial vigente (<= 30 días)", "obligatorio": True},
            {"id": "UR-02", "categoria": "Jurídico", "requisito": "Cédulas propietarios, Cámara de Comercio (<= 30 días si aplica), poder original y autorización notificación electrónica original", "obligatorio": True},
            {"id": "UR-03", "categoria": "Urbanístico", "requisito": "Informe de Alineamiento (Hilos) y Concepto de Norma Urbanística verificando vías obligadas PBOT (CG_014) y clasificación de suelo (urbano vs expansión)", "obligatorio": True},
            {"id": "UR-04", "categoria": "Servicios", "requisito": "Factibilidades vigentes de acueducto/alcantarillado (La Cimarrona ESP) y energía/alumbrado (EPM)", "obligatorio": True},
            {"id": "UR-05", "categoria": "Técnico", "requisito": "3 copias de Levantamiento Topográfico amarrado a MAGNA-SIRGAS / Origen Nacional con curvas de nivel y redes existentes", "obligatorio": True},
            {"id": "UR-06", "categoria": "Técnico", "requisito": "3 copias de diseño urbanístico y geométrico vial (cuadro Área Bruta/Neta/Útil, secciones viales Decreto 152/2018, andenes 1,20 m, ochavas >= 2,00 m y rampas accesibilidad)", "obligatorio": True},
            {"id": "UR-07", "categoria": "Técnico", "requisito": "Estudio de suelos NSR-10 Título H (CBR subrasante, estructura de pavimento, estabilidad de taludes) y diseños hidrosanitarios/pluviales/eléctricos", "obligatorio": True},
            {"id": "UR-08", "categoria": "Ambiental", "requisito": "Plan de Manejo Ambiental (PMA) radicado ante CORNARE según términos de referencia", "obligatorio": True},
            {"id": "UR-09", "categoria": "Patrimonio", "requisito": "Radicado ante el ICANH del Programa de Arqueología Preventiva (obligatorio si el predio matriz >= 10.000 m2 - Decreto-Ley 763 de 2009)", "obligatorio": False},
            {"id": "UR-10", "categoria": "Profesionales", "requisito": "Matrículas profesionales vigentes, certificados de experiencia, valla informativa y medio magnético en bolsa resellable", "obligatorio": True},
        ]
    },
    "parcelacion": {
        "nombre": "Licencia de Parcelación (Suelo Rural / Suburbano)",
        "norma_base": "Decreto 1077 de 2015 / Acuerdo 012 de 2017 / Requisitos Planeación El Carmen",
        "items": [
            {"id": "PA-01", "categoria": "Jurídico", "requisito": "FUN, Certificado de Tradición (<= 30 días), Escritura Pública y Paz y Salvo Municipal (<= 30 días)", "obligatorio": True},
            {"id": "PA-02", "categoria": "Jurídico", "requisito": "Cédulas propietarios, Cámara de Comercio (<= 30 días si aplica), poder original y autorización notificación electrónica", "obligatorio": True},
            {"id": "PA-03", "categoria": "Urbanístico", "requisito": "Informe de alineamiento y factibilidades de servicios públicos / concesión de aguas", "obligatorio": True},
            {"id": "PA-04", "categoria": "Técnico", "requisito": "Estudio de suelos NSR-10 completo para todo el proyecto de parcelación", "obligatorio": True},
            {"id": "PA-05", "categoria": "Técnico", "requisito": "3 copias de Levantamiento Topográfico y 3 copias de diseño de parcelación (vías internas, loteo, secciones viales, cesiones y retiros hídricos)", "obligatorio": True},
            {"id": "PA-06", "categoria": "Ambiental", "requisito": "Plan de Manejo Ambiental según términos de referencia de CORNARE y Permiso de Vertimientos expedido por CORNARE", "obligatorio": True},
            {"id": "PA-07", "categoria": "Patrimonio", "requisito": "Radicado ante el ICANH del Programa de Arqueología Preventiva si el predio >= 10.000 m2", "obligatorio": False},
            {"id": "PA-08", "categoria": "Profesionales", "requisito": "Matrículas profesionales, valla informativa, medio magnético y bolsa plástica resellable", "obligatorio": True},
        ]
    },
    "subdivision_reloteo": {
        "nombre": "Licencia de Subdivisión Predial / Reloteo",
        "norma_base": "Decreto 1077 de 2015 / Acuerdo 012 de 2017 / Decreto 001 de 2026",
        "items": [
            {"id": "SU-01", "categoria": "Jurídico", "requisito": "FUN, Certificado de Tradición (<= 30 días), Escritura Pública y Paz y Salvo Municipal (<= 30 días)", "obligatorio": True},
            {"id": "SU-02", "categoria": "Jurídico", "requisito": "Cédulas propietarios, Cámara de Comercio (<= 30 días si aplica), poder original y autorización notificación electrónica", "obligatorio": True},
            {"id": "SU-03", "categoria": "Técnico", "requisito": "3 copias de Levantamiento Topográfico con cuadro de áreas de predio matriz y lotes resultantes (verificando lote mínimo normativo / UAF)", "obligatorio": True},
            {"id": "SU-04", "categoria": "Profesionales", "requisito": "Copia de matrícula profesional vigente, medio magnético en formato editable y bolsa resellable", "obligatorio": True},
        ]
    },
    "reconocimiento_legalizacion": {
        "nombre": "Reconocimiento de Edificaciones / Legalización",
        "norma_base": "Decreto 1077 de 2015 (Cap. 4) / Ley 1848 de 2017 / Requisitos Planeación El Carmen",
        "items": [
            {"id": "RE-01", "categoria": "Jurídico", "requisito": "FUN, Certificado de Tradición (<= 30 días), Escritura Pública y Paz y Salvo Municipal (<= 30 días)", "obligatorio": True},
            {"id": "RE-02", "categoria": "Jurídico", "requisito": "Declaración extrajuicio acreditando antigüedad de la construcción superior a cinco (5) años antes de la solicitud", "obligatorio": True},
            {"id": "RE-03", "categoria": "Técnico", "requisito": "3 copias de levantamiento arquitectónico de la edificación existente firmado por arquitecto", "obligatorio": True},
            {"id": "RE-04", "categoria": "Técnico", "requisito": "Peritaje técnico / Certificado estructural firmado por ingeniero civil verificando cumplimiento NSR-10 (o recomendaciones de reforzamiento)", "obligatorio": True},
            {"id": "RE-05", "categoria": "Servicios", "requisito": "Facturas o factibilidades de servicios públicos (acueducto y energía); en zona rural, ubicación/diseño de pozo séptico o permiso CORNARE", "obligatorio": True},
            {"id": "RE-06", "categoria": "Urbanístico", "requisito": "Autorización de copropiedad (en PH urbano) y matrículas profesionales vigentes en bolsa resellable", "obligatorio": False},
        ]
    },
    "recibo_urbanismo": {
        "nombre": "Recibo de Obras de Urbanismo",
        "norma_base": "Decreto 1077 de 2015 / Requisitos Planeación El Carmen",
        "items": [
            {"id": "RU-01", "categoria": "Servicios", "requisito": "Actas de recibo de las redes de acueducto, alcantarillado y energía por parte de las Empresas Públicas (La Cimarrona ESP / EPM)", "obligatorio": True},
            {"id": "RU-02", "categoria": "Garantías", "requisito": "Pólizas de estabilidad y calidad de las obras de urbanismo y espacio público", "obligatorio": True},
            {"id": "RU-03", "categoria": "Técnico", "requisito": "Planos Record del urbanismo ejecutado (físicos y medio magnético)", "obligatorio": True},
            {"id": "RU-04", "categoria": "Jurídico", "requisito": "FUN, Certificado de Tradición vigente, Certificado de Cámara de Comercio vigente y Paz y Salvo Municipal", "obligatorio": True},
        ]
    }
}
