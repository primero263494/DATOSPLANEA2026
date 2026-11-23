# -*- coding: utf-8 -*-
"""
Módulo de Análisis Cartográfico: GeoJSON, Shapefile (.zip) y PDF
Municipio de El Carmen de Viboral - Secretaría de Planeación
"""

import io
import json
import math
import zipfile
import struct
from typing import List, Dict, Any, Tuple

def _proyectar_metros_locales(coords_lon_lat: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    if not coords_lon_lat:
        return []
    lat0 = math.radians(sum(c[1] for c in coords_lon_lat) / len(coords_lon_lat))
    metros_por_deg_lat = 111132.92 - 559.82 * math.cos(2 * lat0) + 1.175 * math.cos(4 * lat0)
    metros_por_deg_lon = 111412.84 * math.cos(lat0) - 93.5 * math.cos(3 * lat0)
    lon0, lat0_deg = coords_lon_lat[0][0], coords_lon_lat[0][1]
    return [
        ((lon - lon0) * metros_por_deg_lon, (lat - lat0_deg) * metros_por_deg_lat)
        for lon, lat in coords_lon_lat
    ]

def calcular_longitud_metros(coords_lon_lat: List[Tuple[float, float]]) -> float:
    pts = _proyectar_metros_locales(coords_lon_lat)
    total = 0.0
    for i in range(1, len(pts)):
        total += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
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

def _leer_shapefile_zip_a_features(zip_bytes: bytes) -> Tuple[List[Dict[str, Any]], str]:
    """
    Lee un archivo .zip que contenga un Shapefile (.shp y .dbf opcional) sin requerir
    dependencias externas pesadas (GDAL/geopandas). Soporta tipos Point (1), PolyLine (3) y Polygon (5).
    """
    prj_texto = ""
    shp_data = None
    dbf_data = None

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        for name in zf.namelist():
            low = name.lower()
            if low.endswith(".shp"):
                shp_data = zf.read(name)
            elif low.endswith(".dbf"):
                dbf_data = zf.read(name)
            elif low.endswith(".prj"):
                prj_texto = zf.read(name).decode("utf-8", errors="ignore")

    if not shp_data:
        raise ValueError("El archivo .zip no contiene un archivo .shp válido.")

    # Parsear atributos DBF si existen
    atributos_por_registro: List[Dict[str, Any]] = []
    if dbf_data and len(dbf_data) >= 32:
        num_recs = struct.unpack("<I", dbf_data[4:8])[0]
        header_len = struct.unpack("<H", dbf_data[8:10])[0]
        rec_len = struct.unpack("<H", dbf_data[10:12])[0]
        campos = []
        pos = 32
        while pos + 32 <= header_len and dbf_data[pos] != 0x0D:
            nombre_campo = dbf_data[pos:pos+11].split(b"\x00", 1)[0].decode("latin-1", errors="ignore").strip()
            tipo_campo = chr(dbf_data[pos+11])
            tam_campo = dbf_data[pos+16]
            campos.append((nombre_campo, tipo_campo, tam_campo))
            pos += 32

        offset = header_len
        for _ in range(num_recs):
            if offset + rec_len > len(dbf_data):
                break
            rec = dbf_data[offset:offset+rec_len]
            offset += rec_len
            if rec[0:1] == b"*":
                continue
            fila = {}
            c_pos = 1
            for c_name, c_type, c_len in campos:
                raw_val = rec[c_pos:c_pos+c_len].decode("latin-1", errors="ignore").strip()
                c_pos += c_len
                if c_type in ("N", "F") and raw_val:
                    try:
                        fila[c_name] = float(raw_val) if "." in raw_val else int(raw_val)
                    except ValueError:
                        fila[c_name] = raw_val
                else:
                    fila[c_name] = raw_val
            atributos_por_registro.append(fila)

    # Parsear geometrías SHP
    features = []
    pos = 100
    idx_reg = 0
    while pos + 8 <= len(shp_data):
        _, content_len_words = struct.unpack(">2i", shp_data[pos:pos+8])
        pos += 8
        content_len_bytes = content_len_words * 2
        if pos + content_len_bytes > len(shp_data):
            break
        rec_buf = shp_data[pos:pos+content_len_bytes]
        pos += content_len_bytes
        if len(rec_buf) < 4:
            continue

        shape_type = struct.unpack("<i", rec_buf[0:4])[0]
        props = atributos_por_registro[idx_reg] if idx_reg < len(atributos_por_registro) else {}
        idx_reg += 1

        if shape_type == 0:
            continue
        elif shape_type in (1, 11, 21) and len(rec_buf) >= 20:
            x, y = struct.unpack("<2d", rec_buf[4:20])
            features.append({
                "type": "Feature",
                "properties": props,
                "geometry": {"type": "Point", "coordinates": [x, y]}
            })
        elif shape_type in (3, 13, 23) and len(rec_buf) >= 44:
            num_parts, num_points = struct.unpack("<2i", rec_buf[36:44])
            parts_start = 44
            pts_start = parts_start + 4 * num_parts
            parts = list(struct.unpack(f"<{num_parts}i", rec_buf[parts_start:pts_start]))
            pts = []
            for p_i in range(num_points):
                p_off = pts_start + p_i * 16
                if p_off + 16 <= len(rec_buf):
                    px, py = struct.unpack("<2d", rec_buf[p_off:p_off+16])
                    pts.append([px, py])
            if num_parts <= 1:
                features.append({
                    "type": "Feature",
                    "properties": props,
                    "geometry": {"type": "LineString", "coordinates": pts}
                })
            else:
                lineas = []
                for i, st_i in enumerate(parts):
                    en_i = parts[i+1] if i+1 < len(parts) else len(pts)
                    lineas.append(pts[st_i:en_i])
                features.append({
                    "type": "Feature",
                    "properties": props,
                    "geometry": {"type": "MultiLineString", "coordinates": lineas}
                })
        elif shape_type in (5, 15, 25) and len(rec_buf) >= 44:
            num_parts, num_points = struct.unpack("<2i", rec_buf[36:44])
            parts_start = 44
            pts_start = parts_start + 4 * num_parts
            parts = list(struct.unpack(f"<{num_parts}i", rec_buf[parts_start:pts_start]))
            pts = []
            for p_i in range(num_points):
                p_off = pts_start + p_i * 16
                if p_off + 16 <= len(rec_buf):
                    px, py = struct.unpack("<2d", rec_buf[p_off:p_off+16])
                    pts.append([px, py])
            anillos = []
            for i, st_i in enumerate(parts):
                en_i = parts[i+1] if i+1 < len(parts) else len(pts)
                anillos.append([pts[st_i:en_i]])
            if len(anillos) == 1:
                features.append({
                    "type": "Feature",
                    "properties": props,
                    "geometry": {"type": "Polygon", "coordinates": anillos[0]}
                })
            else:
                features.append({
                    "type": "Feature",
                    "properties": props,
                    "geometry": {"type": "MultiPolygon", "coordinates": anillos}
                })

    return features, prj_texto

def _procesar_features_geojson(features: List[Dict[str, Any]], capas_referencia_bytes: bytes = None, meta_extra: Dict[str, Any] = None) -> Dict[str, Any]:
    resumen_elementos = []
    area_total_m2 = 0.0
    longitud_total_m = 0.0
    todos_vertices = []

    for idx, feat in enumerate(features, 1):
        geom = feat.get("geometry") or {}
        props = feat.get("properties") or {}
        gtype = geom.get("type", "Desconocido")
        coords = geom.get("coordinates")

        nombre_elem = props.get("name") or props.get("nombre") or props.get("NOMBRE") or props.get("codigo") or f"Elemento_{idx}"
        metrica_txt = ""
        vertices_elem = []

        if gtype == "Point" and coords:
            vertices_elem = [(coords[0], coords[1])]
            metrica_txt = f"Punto: lon={coords[0]:.6f}, lat={coords[1]:.6f}"
        elif gtype == "Polygon" and coords:
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

    reglas_aplicables = []
    if area_total_m2 >= 10000:
        reglas_aplicables.append({
            "nivel": "ALERTA",
            "regla": "Área >= 10.000 m² (1 ha): En licencias de urbanismo o parcelación exige radicado ante el ICANH (Programa de Arqueología Preventiva - Decreto-Ley 763 de 2009)."
        })
    if area_total_m2 >= 300:
        reglas_aplicables.append({
            "nivel": "INFO",
            "regla": "Área >= 300 m²: Verificar obligatoriedad de Estudio de Suelos NSR-10 Título H según tipología y ubicación."
        })

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

    # Verificar si las coordenadas están en grados geográficos (-180..180, -90..90) para st.map
    coords_mapa = []
    es_proyectada_metros = False
    for c in todos_vertices:
        if -180.0 <= c[0] <= 180.0 and -90.0 <= c[1] <= 90.0:
            coords_mapa.append({"lat": c[1], "lon": c[0]})
        else:
            es_proyectada_metros = True

    out = {
        "num_elementos": len(features),
        "area_total_m2": round(area_total_m2, 2),
        "longitud_total_m": round(longitud_total_m, 2),
        "elementos": resumen_elementos,
        "reglas_aplicables": reglas_aplicables,
        "intersecciones_capa_referencia": intersecciones,
        "coordenadas_mapa": coords_mapa,
        "es_proyectada_metros": es_proyectada_metros
    }
    if meta_extra:
        out.update(meta_extra)
    return out

def analizar_archivo_cartografico(nombre_archivo: str, contenido_bytes: bytes, capas_referencia_bytes: bytes = None) -> Dict[str, Any]:
    """
    Analiza archivos GeoJSON (.geojson, .json) o Shapefile comprimido (.zip con .shp/.dbf/.prj).
    """
    low = nombre_archivo.lower()
    if low.endswith(".zip"):
        feats, prj_txt = _leer_shapefile_zip_a_features(contenido_bytes)
        return _procesar_features_geojson(feats, capas_referencia_bytes, {"prj_info": prj_txt})
    else:
        data = json.loads(contenido_bytes.decode("utf-8"))
        feats = data.get("features") if data.get("type") == "FeatureCollection" else [data]
        return _procesar_features_geojson(feats, capas_referencia_bytes)

def analizar_pdf_plano(contenido_bytes: bytes) -> Dict[str, Any]:
    """
    Inspecciona un archivo PDF (plano urbanístico/arquitectónico o PDF georreferenciado):
    extrae páginas, dimensiones de página, texto detectado y marcas/metadatos geoespaciales (ISO 32000 / GeoPDF).
    """
    raw_txt = contenido_bytes.decode("latin-1", errors="ignore")
    num_paginas = raw_txt.count("/Type /Page")
    if num_paginas == 0:
        num_paginas = max(1, raw_txt.count("/Page"))

    es_geopdf = ("/Measure" in raw_txt) or ("/VP" in raw_txt) or ("GEOJSON" in raw_txt.upper()) or ("EPSG" in raw_txt.upper()) or ("MAGNA" in raw_txt.upper())

    # Intentar extraer texto legible básico de streams o cadenas entre paréntesis
    import re
    textos_encontrados = []
    for match in re.findall(r"\(([^\(\)]{3,80})\)", raw_txt):
        limpio = "".join(ch for ch in match if ch.isprintable()).strip()
        if len(limpio) >= 4 and not limpio.startswith("PDF-"):
            textos_encontrados.append(limpio)

    # Deduplicar manteniendo orden
    vistos = set()
    muestra_texto = []
    for t in textos_encontrados:
        if t not in vistos:
            vistos.add(t)
            muestra_texto.append(t)
        if len(muestra_texto) >= 25:
            break

    return {
        "tamano_kb": round(len(contenido_bytes) / 1024.0, 2),
        "num_paginas_estimadas": num_paginas,
        "tiene_marcas_geoespaciales_pdf": es_geopdf,
        "muestra_texto_detectado": muestra_texto
    }
