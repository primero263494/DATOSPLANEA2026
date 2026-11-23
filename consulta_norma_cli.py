# -*- coding: utf-8 -*-
"""
Programa 1: Herramienta de Consulta Rápida Normativa y Tarifaria en Consola (CLI)
Municipio de El Carmen de Viboral (PBOT Acuerdo 012/2017, Decreto 152/2018, Decreto Tarifas 001/2026)
"""

from data.normativa_carmen import (
    PARAMETROS_2026,
    TARIFAS_DELINEACION_2026,
    OTRAS_ACTUACIONES_2026,
    REGLAS_URBANISTICAS_PBOT,
    CHECKLIST_TRAMITES
)

def menu_consulta():
    while True:
        print("\n" + "="*72)
        print(" CONSULTA NORMATIVA Y TARIFARIA - EL CARMEN DE VIBORAL (2026)")
        print(f" UVT 2026: ${PARAMETROS_2026['uvt']:,.0f} | SMMLV 2026: ${PARAMETROS_2026['smmlv']:,.0f}")
        print("="*72)
        print("1. Buscar palabra clave en normas urbanísticas y tarifas")
        print("2. Ver tabla completa de tarifas de delineación (2026)")
        print("3. Ver tabla de otras actuaciones (Alineamiento, Norma, Uso, PH)")
        print("4. Consultar lista de chequeo por tipo de trámite")
        print("0. Salir")

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            q = input("Ingrese palabra clave (ej. ochava, anden, rural, cimarronas, icanh): ").strip().lower()
            print(f"\n--- Resultados para '{q}' ---")
            for r in REGLAS_URBANISTICAS_PBOT:
                if q in r["categoria"].lower() or q in r["regla"].lower() or q in r["norma"].lower():
                    print(f"\n* [{r['categoria']}] ({r['norma']})\n  {r['regla']}")
            for v in TARIFAS_DELINEACION_2026.values():
                if q in v["nombre"].lower() or q in v["observacion"].lower():
                    print(f"\n* [Tarifa] {v['nombre']}: ${v['valor_ajustado']:,.0f}/m2 ({v['uvt']} UVT)")
                    if v["observacion"]:
                        print(f"  Nota: {v['observacion']}")

        elif opcion == "2":
            print("\n--- TARIFAS IMPUESTO DE DELINEACIÓN 2026 ---")
            for v in TARIFAS_DELINEACION_2026.values():
                print(f"- {v['nombre']}: ${v['valor_ajustado']:,.0f} / {v['unidad']} ({v['uvt']} UVT)")

        elif opcion == "3":
            print("\n--- OTRAS ACTUACIONES URBANÍSTICAS 2026 ---")
            for v in OTRAS_ACTUACIONES_2026.values():
                print(f"- {v['nombre']}: ${v['valor_ajustado']:,.0f} ({v['uvt']} UVT)")

        elif opcion == "4":
            claves = list(CHECKLIST_TRAMITES.keys())
            for idx, k in enumerate(claves, 1):
                print(f"{idx}. {CHECKLIST_TRAMITES[k]['nombre']}")
            sel = input("Seleccione número de trámite: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(claves):
                tramite = CHECKLIST_TRAMITES[claves[int(sel)-1]]
                print(f"\n=== {tramite['nombre']} ===")
                print(f"Norma: {tramite['norma_base']}\n")
                for it in tramite["items"]:
                    req_txt = "OBLIGATORIO" if it["obligatorio"] else "CONDICIONAL"
                    print(f"[{it['id']}] ({req_txt}) {it['requisito']}")

        elif opcion == "0":
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu_consulta()
