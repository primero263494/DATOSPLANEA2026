# -*- coding: utf-8 -*-
"""
Módulo de Análisis Cartográfico Vectorial (GeoJSON, KML, GPX, CSV/WKT)
Municipio de El Carmen de Viboral - Secretaría de Planeación
"""

import json
import math
from typing import List, Dict, Any, Tuple

def _proyectar_metros_locales(coords_lon_lat: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Proyecta coordenadas geográficas (longitud, latitud) a un sistema plano local en metros
    centrado en el baricentro de la geometría para calcular áreas y longitudes con precisión.
    """
    if not coords_lon_lat:
        return []
    lat0 = math.radians(sum(c[1] for c in coords_lon_lat) / len(coords_lon_lat))
    metros_por_deg_lat = 111132.92 - 559.82 * math.cos(2 * lat0) + 1.175 * math.cos(4 * lat0)
    metros_por_deg_lon = 111412.84 * math.cos(lat0) - 93.5 * math.cos(3 * lat0)

    lon0 = coords_lon_lat[0][0]
    lat0_deg = coords_lon_lat[0][1]

    return [
        ((lon - lon0) * metros_por_deg_lon, (lat - lat0_deg) * metros_por_deg_lat)
        for lon, lat in coords_lon_lat
    ]

def calcular_longitud_metros(coords_lon_lat: List[Tuple[float, float]]) -> float:
    pts = _proyectar_metros_locales(coords_lon_lat)
    total = 0.0
    for i in range(1, len(pts)):
        dx = pts[i][0] - pts[i - 1][0]
        dy = pts[i][1] - pts[i - 1][1]
        total += math.hypot(dx, dy)
    return round(total, 2)

def calcular_area_poligono_m2(coords_lon_lat: List[Tuple[float, float]]) -> float:
    pts = _proyectar_metros_locales(coords_lon_lat)
    if len(pts) < 3:
        return 0.0
    area2 = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        area2 += (x1 * y2 - x2 * y1)
    return round(abs(area2) / 2.0, 2)

def calcular_perimetro_poligono_m(coords_lon_lat: List[Tuple[float, float]]) -> float:
    if len(coords_lon_lat) < 2:
        return 0.0
    cerrado = list(coords_lon_lat)
    if cerrado[0] != cerrado[-1]:
        cerrado.append(cerrado[0])
    return calcular_longitud_metros(cerrado)

def _punto_en_poligono(lon: float, lat: float, anillo: List[Tuple[float, float]]) -> bool:
    dentro = False
    n = len(anillo)
    for i in range(n):
        x1, y1 = anillo[i]
        x2, y2 = anillo[(i + 1) % n]
        if ((y1 > lat) != (y2 > lat)):
            x_inter = (x2 - x1) * (lat - y1) / ((y2 - y1) if (y2 - y1) != 0 else 1e-12) + x1
            if lon < x_inter:
                dentro = not dentro
    return dentro

def analizar_geojson_proyecto(contenido_bytes: bytes, capas_referencia_bytes: bytes = None) -> Dict[str, Any]:
    """
    Analiza un archivo GeoJSON del proyecto (predio, vía, loteo o zona de intervención)
    y opcionalmente cruza contra una capa GeoJSON de referencia/restricción (retiros, vías PBOT,
    zonas de amenaza, suelos de protección o polígonos normativos).
    """
    data = json.loads(contenido_bytes.decode("utf-8"))
    features = data.get("features") if data.get("type") == "FeatureCollection" else [data]

    resumen_elementos = []
    area_total_m2 = 0.0
    longitud_total_m = 0.0
    todos_vertices = []

    for idx, feat in enumerate(features, 1):
        geom = feat.get("geometry") or {}
        props = feat.get("properties") or {}
        gtype = geom.get("type", "Desconocido")
        coords = geom.get("coordinates")

        nombre_elem = props.get("name") or props.get("nombre") or props.get("codigo") or f"Elemento_{idx}"
        metrica_txt = ""
        vertices_elem = []

        if gtype == "Polygon" and coords:
            anillo = [(pt[0], pt[1]) for pt in coords[0]]
            vertices_elem = anillo
            area = calcular_area_poligono_m2(anillo)
            perim = calcular_perimetro_poligono_m(anillo)
            area_total_m2 += area
            metrica_txt = f"Área: {area:,.2f} m² | Perímetro: {perim:,.2f} m"
        elif gtype == "LineString" and coords:
            linea = [(pt[0], pt[1]) for pt in coords]
            vertices_elem = linea
            lon_m = calcular_longitud_metros(linea)
            longitud_total_m += lon_m
            metrica_txt = f"Longitud: {lon_m:,.2f} m"
        elif gtype == "MultiPolygon" and coords:
            area_mp = 0.0
            for poly in coords:
                anillo = [(pt[0], pt[1]) for pt in poly[0]]
                vertices_elem.extend(anillo)
                area_mp += calcular_area_poligono_m2(anillo)
            area_total_m2 += area_mp
            metrica_txt = f"Área total MultiPolygon: {area_mp:,.2f} m²"
        elif gtype == "MultiLineString" and coords:
            lon_ml = 0.0
            for ln in coords:
                linea = [(pt[0], pt[1]) for pt in ln]
                vertices_elem.extend(linea)
                lon_ml += calcular_longitud_metros(linea)
            longitud_total_m += lon_ml
            metrica_txt = f"Longitud total MultiLineString: {lon_ml:,.2f} m"

        todos_vertices.extend(vertices_elem)
        resumen_elementos.append({
            "elemento": nombre_elem,
            "geometria": gtype,
            "medidas": metrica_txt,
            "propiedades": props
        })

    # Reglas automáticas derivadas del área y normativa de El Carmen de Viboral
    reglas_aplicables = []
    if area_total_m2 >= 10000:
        reglas_aplicables.append({
            "nivel": "ALERTA",
            "regla": "Área >= 10.000 m² (1 ha): En licencias de urbanismo o parcelación exige radicado ante el ICANH (Programa de Arqueología Preventiva - Decreto-Ley 763 de 2009 / Requisitos Planeación)."
        })
    if area_total_m2 >= 300:
        reglas_aplicables.append({
            "nivel": "INFO",
            "regla": "Área >= 300 m²: En proyectos de construcción rural/suburbana o edificaciones de altura/densidad, verificar obligatoriedad de Estudio de Suelos NSR-10 Título H."
        })

    # Cruce espacial opcional contra capa de referencia/restricción (GeoJSON)
    intersecciones = []
    if capas_referencia_bytes:
        ref_data = json.loads(capas_referencia_bytes.decode("utf-8"))
        ref_feats = ref_data.get("features") if ref_data.get("type") == "FeatureCollection" else [ref_data]
        for r_idx, r_feat in enumerate(ref_feats, 1):
            r_geom = r_feat.get("geometry") or {}
            r_props = r_feat.get("properties") or {}
            r_nombre = r_props.get("name") or r_props.get("nombre") or r_props.get("categoria") or f"Capa_Ref_{r_idx}"
            if r_geom.get("type") == "Polygon" and r_geom.get("coordinates"):
                anillo_ref = [(pt[0], pt[1]) for pt in r_geom["coordinates"][0]]
                pts_dentro = sum(1 for (vx, vy) in todos_vertices if _punto_en_poligono(vx, vy, anillo_ref))
                if pts_dentro > 0:
                    intersecciones.append({
                        "capa_referencia": r_nombre,
                        "vertices_dentro": pts_dentro,
                        "total_vertices_evaluados": len(todos_vertices),
                        "detalle": f"{pts_dentro} de {len(todos_vertices)} vértices del proyecto caen dentro de '{r_nombre}'."
                    })

    return {
        "num_elementos": len(features),
        "area_total_m2": round(area_total_m2, 2),
        "longitud_total_m": round(longitud_total_m, 2),
        "elementos": resumen_elementos,
        "reglas_aplicables": reglas_aplicables,
        "intersecciones_capa_referencia": intersecciones,
        "coordenadas_mapa": [{"lat": c[1], "lon": c[0]} for c in todos_vertices]
    }
