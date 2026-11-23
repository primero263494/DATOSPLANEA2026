# Sistema de Consulta Normativa, Liquidación y Gestión de Trámites Urbanísticos
**Municipio de El Carmen de Viboral (Antioquia)**

Este paquete contiene dos herramientas integradas en Python:
1. **`consulta_norma_cli.py`**: Programa ligero en consola para consultar de inmediato reglas del PBOT (Acuerdo 012 de 2017), Decreto 152 de 2018, tarifas 2026 (Decreto 001 de 2026) y listas de chequeo.
2. **`app_planeacion.py`**: Aplicación web completa para funcionarios (en Streamlit + SQLite) con 5 módulos:
   - Consulta normativa y tarifaria buscable.
   - Calculadora tributaria (delineación urbana/rural, reformas, urbanización, parcelación, subdivisión y actuaciones).
   - Verificador técnico de planos (ocupación, construcción, andenes 1,20 m, bordillos, ochavas >= 2,00 m, pendientes y retiros hídricos).
   - Gestor de expedientes digitales con lista de chequeo interactiva y carga/archivo de documentos por radicado.
   - Generador automático de Actas de Observaciones y Conceptos Técnicos descargables.

## Instalación y ejecución
```bash
pip install -r requirements.txt

# Programa 1: Consulta rápida en consola
python consulta_norma_cli.py

# Programa 2: Plataforma web para funcionarios
streamlit run app_planeacion.py
```
