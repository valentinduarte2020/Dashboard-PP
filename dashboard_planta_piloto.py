# -*- coding: utf-8 -*-
"""
PLANTA PILOTO — DASHBOARD OPERACIONAL
=====================================
Aplicación en Python (Streamlit + Plotly).

Pestañas:
  ⚙️ Parámetros            -> Editor central de TODOS los datos (fuente única).
  🟠 WP1 Oxidación/Reducción
  🟢 WP2 Separación metalúrgica
  🔴 WP3 Fijación de arsénico
       Cada WP mantiene: avance experimental, niveles de experimentación,
       riesgos/alertas, su detalle, estado de análisis químico y mineralogía.
  🛡️ Seguridad             -> Incidentes, seguimiento, estado MIPER e indicadores HSE.

Cómo ejecutar (en la carpeta del archivo):
    py -m streamlit run dashboard_planta_piloto.py
"""

import json
import time
import streamlit as st
import plotly.graph_objects as go

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
st.set_page_config(page_title="Planta Piloto — Dashboard Operacional",
                   page_icon="🏭", layout="wide")

# ---- Paleta (contrastes cuidados) --------------------------
NAVY   = "#0E2438"
WP1    = "#F5A623"
WP2    = "#2BAE66"
WP3    = "#E0443A"
GRAY   = "#A7B0BA"
YELLOW = "#F2C200"
TEXT   = "#243B53"
MUTED  = "#627D98"
REDTXT = "#D64545"
CARD   = "#FFFFFF"
CELESTE = "#E6EFF8"   # fondo unificado de ventanas
CELL    = "#F4F9FE"   # fondo de celdas/datos (celeste muy claro)
BG     = "#EDF1F5"
BLUE   = "#3B82C4"
PURPLE = "#8E6FC0"
PASTEL_OPTS = ["Azul", "Naranja", "Verde", "Morado", "Gris"]
PASTEL_HEX = {"Azul": "#D6E6F7", "Naranja": "#FCE3CC", "Verde": "#D8F0DC",
              "Morado": "#E7DEF6", "Gris": "#E6E9ED"}

STATUS_COLOR = {"VERDE": WP2, "AMARILLO": YELLOW, "ROJO": WP3}
LEVEL_DOT = {"Planificado": BLUE, "Completado": WP2, "En curso": WP1,
             "Pendiente": GRAY, "En riesgo": WP3}
RISK_STYLE = {"Alta": (WP3, "#FFFFFF"), "Media": (YELLOW, NAVY), "Baja": (WP2, "#FFFFFF")}
SEV_MAP   = {"Bajo": WP2, "Medio": YELLOW, "Alto": WP3, "Crítico": WP3}
INCEST_MAP = {"Cerrado": WP2, "En seguimiento": YELLOW, "Abierto": WP3}
INCPIE = [("No iniciado", "s_est_noini", GRAY), ("En desarrollo", "s_est_des", WP1),
          ("En revisión", "s_est_rev", BLUE), ("Aprobado", "s_est_apr", WP2)]
CAP_MAP = {"Realizada": WP2, "Programada": BLUE, "Pendiente": YELLOW, "Cancelada": GRAY}
QEST_MAP  = {"En tiempo": WP2, "Atrasado": YELLOW, "Crítico": WP3}
MEST_MAP  = {"Completo": WP2, "En proceso": YELLOW, "Pendiente": GRAY}
MIPER_MAP = {"Vigente": WP2, "Por vencer": YELLOW, "Vencido": WP3}
SEM_MAP   = {"Verde": WP2, "Amarillo": YELLOW, "Rojo": WP3}
DONUT_PAL = [WP2, WP1, WP3, BLUE, PURPLE, "#16A085", "#E67E22", GRAY]

NIV_OPTS   = ["Planificado", "Completado", "En curso", "Pendiente", "En riesgo"]
RISK_OPTS  = ["—", "Alta", "Media", "Baja"]
QEST_OPTS  = ["En tiempo", "Atrasado", "Crítico"]
MEST_OPTS  = ["Completo", "En proceso", "Pendiente"]
MIPER_OPTS = ["Vigente", "Por vencer", "Vencido"]
SEM_OPTS   = ["Verde", "Amarillo", "Rojo"]
W2_PROCS = ["Separación magnética", "Flotación", "Fusión neutra",
            "Lixiviación de calcina sulfatada", "Cristalización de sulfatos de cobre",
            "Extracción por solventes",
            "Deshidratación de sulfatos de cobre", "Descomposición de óxidos de cobre"]
W3_PROCS = ["Sulfidización de polvos de arsénico", "Volatilización de polvos sulfidizados",
            "Fijación de arsénico"]
PROCS = {
    "1": ["Desarsenificación", "Desulfuración", "Sulfatación",
          "Reducción de Calcinas Oxidadas", "Reducción de Óxidos de cobre", "Fusión reductora"],
    "2": W2_PROCS,
    "3": W3_PROCS,
}
NIV_LEVELS = ["Laboratorio", "Banco", "Semipiloto"]
WP_LEVELS = {
    "1": ["Laboratorio", "Banco", "Semipiloto", "Semipiloto Cont."],
    "2": ["Laboratorio", "Banco", "Semipiloto"],
    "3": ["Laboratorio", "Banco", "Semipiloto"],
}
OX_PROCS = ["Desarsenificación", "Desulfuración", "Sulfatación"]
RD_PROCS = ["Reducción de Calcinas Oxidadas", "Reducción de Óxidos de cobre", "Fusión reductora"]
FEED_LABELS = ["Alim. 1", "Alim. 2", "Alim. 3", "Alim. 4", "Alim. 5"]
FEED_COLORS = ["#1D4ED8", "#7C3AED", "#DB2777", "#0E7C86", "#D9831F"]
N_FEEDS = len(FEED_COLORS)
_EXTRA_M = [("x7", 0), ("x8", 1), ("x9", 0), ("x10", 0), ("x11", 0), ("x12", 0),
            ("x13", 0), ("x14", 1), ("x15", 0)] + [(f"x{_n}", 0) for _n in range(16, 31)]
OX_METRICS = [("conv", 0), ("remAs", 0), ("ph", 1), ("eh", 0), ("temp", 0), ("cons", 0)] + _EXTRA_M
RD_METRICS = [("red", 0), ("rec", 0), ("ph", 1), ("eh", 0), ("temp", 0), ("cons", 0)] + _EXTRA_M
W2_METRICS = [("b1", 0), ("b2", 0), ("b3", 1), ("b4", 0), ("b5", 0), ("b6", 0),
              ("b7", 0), ("b8", 1), ("b9", 0), ("b10", 0), ("b11", 0), ("b12", 0),
              ("b13", 0), ("b14", 1), ("b15", 0)] + [(f"b{_n}", 0) for _n in range(16, 31)]
W3_METRICS = [("c1", 0), ("c2", 0), ("c3", 1), ("c4", 0), ("c5", 0), ("c6", 0),
              ("c7", 0), ("c8", 1), ("c9", 0), ("c10", 0), ("c11", 0), ("c12", 0),
              ("c13", 0), ("c14", 1), ("c15", 0)] + [(f"c{_n}", 0) for _n in range(16, 31)]
METRIC_NAME = {"conv": "Conversión", "remAs": "Remoción As", "ph": "pH", "eh": "Eh",
               "temp": "Temperatura", "cons": "Consumo", "red": "Reducción", "rec": "Recuperación",
               "x7": "Densidad pulpa", "x8": "T. retención", "x9": "Agitación", "x10": "P80",
               "x11": "Dosis reactivo", "x12": "Sólidos", "x13": "Flujo", "x14": "Presión", "x15": "Rendimiento",
               "b1": "Recuperación", "b2": "Ley producto", "b3": "pH", "b4": "Temperatura",
               "b5": "Consumo reactivo", "b6": "Rechazo impurezas", "b7": "Densidad pulpa",
               "b8": "T. retención", "b9": "Flujo", "b10": "P80", "b11": "Dosis colector",
               "b12": "Sólidos", "b13": "Agitación", "b14": "Presión", "b15": "Rendimiento",
               "c1": "Remoción As", "c2": "As volatilizado", "c3": "pH", "c4": "Temperatura",
               "c5": "Consumo reactivo", "c6": "As fijado", "c7": "As lixiviable", "c8": "T. retención",
               "c9": "Eh", "c10": "Generación residuo", "c11": "Dosis estabilizante", "c12": "Sólidos",
               "c13": "Flujo", "c14": "Presión", "c15": "Rendimiento"}
for _pref in ("x", "b", "c"):
    for _n in range(16, 31):
        METRIC_NAME.setdefault(f"{_pref}{_n}", f"Variable {_n}")
LVL_TAGS = ["L", "B", "S", "SC"]   # Laboratorio, Banco, Semipiloto, Semipiloto continuo



# ============================================================
# VALORES POR DEFECTO
# ============================================================
DEFAULTS = {
    # ---- Encabezado ----
    "hdr_title": "PLANTA PILOTO — DASHBOARD OPERACIONAL",
    "hdr_updated": "14-05-2026 10:30", "hdr_status": "AMARILLO",

    # ---- Resúmenes WP ----
    "wp1_name": "Oxidación / Reducción", "wp1_level": "Banco",
    "wp1_progress": 65,
    "wp1_kpi1_op": "Oxidación", "wp1_kpi1_name": "Conversión global",
    "wp1_kpi1_desc": "Conversión de sulfuros a forma soluble",
    "wp1_kpi1_ref": "≥ 90%", "wp1_kpi1_meta2": "≥ 95%", "wp1_kpi1_val": "88%", "wp1_kpi1_sem": "Amarillo",
    "wp1_kpi2_op": "Oxidación", "wp1_kpi2_name": "Remoción de As (solución)",
    "wp1_kpi2_desc": "Arsénico removido desde la solución",
    "wp1_kpi2_ref": "≥ 95%", "wp1_kpi2_meta2": "≥ 98%", "wp1_kpi2_val": "96%", "wp1_kpi2_sem": "Verde",
    "wp1_kpi3_op": "Oxidación", "wp1_kpi3_name": "Sulfatación (SO₄²⁻)",
    "wp1_kpi3_desc": "Grado de sulfatación alcanzado",
    "wp1_kpi3_ref": "≥ 70%", "wp1_kpi3_meta2": "≥ 80%", "wp1_kpi3_val": "72%", "wp1_kpi3_sem": "Verde",
    "wp1_kpi4_op": "Reducción Calcinas", "wp1_kpi4_name": "Reducción Fe³⁺→Fe²⁺",
    "wp1_kpi4_desc": "Conversión de hierro férrico a ferroso",
    "wp1_kpi4_ref": "≥ 85%", "wp1_kpi4_meta2": "≥ 90%", "wp1_kpi4_val": "82%", "wp1_kpi4_sem": "Amarillo",
    "wp1_kpi5_op": "Reducción CuO", "wp1_kpi5_name": "Reducción CuO→Cu⁰",
    "wp1_kpi5_desc": "Reducción de óxido de cobre a cobre metálico",
    "wp1_kpi5_ref": "≥ 90%", "wp1_kpi5_meta2": "≥ 95%", "wp1_kpi5_val": "93%", "wp1_kpi5_sem": "Verde",
    "wp2_name": "Separación metalúrgica", "wp2_level": "Lab",
    "wp2_progress": 80,
    "wp2_kpi1_op": "Flotación Rougher", "wp2_kpi1_name": "Recuperación global",
    "wp2_kpi1_desc": "Recuperación metalúrgica total",
    "wp2_kpi1_ref": "≥ 85%", "wp2_kpi1_meta2": "≥ 90%", "wp2_kpi1_val": "86%", "wp2_kpi1_sem": "Verde",
    "wp2_kpi2_op": "Flotación Cleaner", "wp2_kpi2_name": "Ley de producto",
    "wp2_kpi2_desc": "Ley del concentrado final",
    "wp2_kpi2_ref": "≥ 28%", "wp2_kpi2_meta2": "≥ 32%", "wp2_kpi2_val": "32%", "wp2_kpi2_sem": "Verde",
    "wp2_kpi3_op": "Flotación", "wp2_kpi3_name": "Rechazo de impurezas",
    "wp2_kpi3_desc": "Impurezas enviadas a relave",
    "wp2_kpi3_ref": "≥ 70%", "wp2_kpi3_meta2": "≥ 80%", "wp2_kpi3_val": "74%", "wp2_kpi3_sem": "Amarillo",
    "wp2_kpi4_op": "Espesamiento", "wp2_kpi4_name": "Cierre de balance",
    "wp2_kpi4_desc": "Cierre del balance metalúrgico",
    "wp2_kpi4_ref": "≥ 95%", "wp2_kpi4_meta2": "≥ 98%", "wp2_kpi4_val": "96%", "wp2_kpi4_sem": "Verde",
    "wp2_kpi5_op": "Separación", "wp2_kpi5_name": "Factor de separación",
    "wp2_kpi5_desc": "Selectividad del proceso",
    "wp2_kpi5_ref": "≥ 4,0", "wp2_kpi5_meta2": "≥ 5,0", "wp2_kpi5_val": "4,2", "wp2_kpi5_sem": "Amarillo",
    "wp3_name": "Fijación de arsénico", "wp3_level": "Semipiloto",
    "wp3_progress": 40,
    "wp3_kpi1_op": "Precipitación", "wp3_kpi1_name": "Remoción de As",
    "wp3_kpi1_desc": "Arsénico removido del efluente",
    "wp3_kpi1_ref": "≥ 95%", "wp3_kpi1_meta2": "≥ 98%", "wp3_kpi1_val": "98%", "wp3_kpi1_sem": "Verde",
    "wp3_kpi2_op": "Precipitación", "wp3_kpi2_name": "As residual (efluente)",
    "wp3_kpi2_desc": "As soluble en el efluente tratado",
    "wp3_kpi2_ref": "≤ 1,0 mg/L", "wp3_kpi2_meta2": "≤ 0,5 mg/L", "wp3_kpi2_val": "0,8 mg/L", "wp3_kpi2_sem": "Amarillo",
    "wp3_kpi3_op": "Estabilización", "wp3_kpi3_name": "As lixiviable (residuo)",
    "wp3_kpi3_desc": "As lixiviable del residuo sólido",
    "wp3_kpi3_ref": "≤ 1,0 mg/L", "wp3_kpi3_meta2": "≤ 0,5 mg/L", "wp3_kpi3_val": "1,5 mg/L", "wp3_kpi3_sem": "Rojo",
    "wp3_kpi4_op": "Estabilización", "wp3_kpi4_name": "Generación de residuo",
    "wp3_kpi4_desc": "Residuo por kg de As fijado",
    "wp3_kpi4_ref": "≤ 15 kg/kg", "wp3_kpi4_meta2": "≤ 10 kg/kg", "wp3_kpi4_val": "12 kg/kg", "wp3_kpi4_sem": "Amarillo",
    "wp3_kpi5_op": "Encapsulamiento", "wp3_kpi5_name": "Estabilidad química (pH)",
    "wp3_kpi5_desc": "Rango de pH del residuo estabilizado",
    "wp3_kpi5_ref": "8 – 11", "wp3_kpi5_meta2": "9 – 10", "wp3_kpi5_val": "10,2", "wp3_kpi5_sem": "Verde",

    # ---- Avance experimental por WP ----
    "av1_planif": 18, "av1_ejec": 12, "av1_valid": 10, "av1_pend": 3,
    "av2_planif": 15, "av2_ejec": 10, "av2_valid": 9,  "av2_pend": 1,
    "av3_planif": 12, "av3_ejec": 6,  "av3_valid": 5,  "av3_pend": 2,

    # ---- Niveles de experimentación ----
    "niv_wp1_lab": "Completado", "niv_wp1_banco": "En curso",   "niv_wp1_semi": "Pendiente",
    "niv_wp2_lab": "Completado", "niv_wp2_banco": "Pendiente",  "niv_wp2_semi": "Pendiente",
    "niv_wp3_lab": "Completado", "niv_wp3_banco": "Completado", "niv_wp3_semi": "En riesgo",

    # ---- Riesgos por WP (— = sin alerta) ----
    "wp1_r1_level": "Media", "wp1_r1_desc": "Consumo reactivo sobre meta",
    "wp1_r2_level": "—", "wp1_r2_desc": "", "wp1_r3_level": "—", "wp1_r3_desc": "",
    "wp2_r1_level": "Baja", "wp2_r1_desc": "Resultado analítico pendiente",
    "wp2_r2_level": "—", "wp2_r2_desc": "", "wp2_r3_level": "—", "wp2_r3_desc": "",
    "wp3_r1_level": "Alta", "wp3_r1_desc": "As lixiviable sobre criterio interno",
    "wp3_r2_level": "Media", "wp3_r2_desc": "Estabilidad del residuo en seguimiento",
    "wp3_r3_level": "—", "wp3_r3_desc": "",

    # ---- WP1 detalle ----
    "d1_ox_conv": 88, "d1_ox_remAs": 96, "d1_ox_sulf": 72,
    "d1_ox_ph": 1.8, "d1_ox_eh": 680, "d1_ox_temp": 65, "d1_ox_cons": 38,
    "d1_ox_trend": "620,660,700,640,690,720,650,680,700,640,660,690,650",
    "d1_rc_red": 82, "d1_rc_recFe": 78,
    "d1_rc_ph": 2.0, "d1_rc_eh": -120, "d1_rc_temp": 70, "d1_rc_cons": 25,
    "d1_rc_trend": "360,400,380,420,390,450,410,380,430,400,420,390,410",
    "d1_cu_red": 93, "d1_cu_recCu": 91,
    "d1_cu_ph": 1.6, "d1_cu_eh": -250, "d1_cu_temp": 60, "d1_cu_cons": 25,
    "d1_cu_trend": "330,360,340,370,350,380,330,360,350,340,370,350,360",
    "wp1_action": "Optimizar dosis de oxidante y reductor para reducir consumo y mejorar estabilidad de Eh.",
    "wp1_act_0": "Optimizar dosis de oxidante y reductor para reducir consumo y mejorar estabilidad de Eh.",
    "wp1_act_1": "Validar repetibilidad de la remoción de As en banco.",
    "wp1_act_2": "Ajustar temperatura de sulfatación para mejorar selectividad.",
    "wp1_act_3": "", "wp1_act_4": "",
    "wp1_actvac_0": False, "wp1_actvac_1": False, "wp1_actvac_2": False,
    "wp1_actvac_3": True, "wp1_actvac_4": True,

    # ---- WP2 detalle ----
    "d2_recup": 86, "d2_ley": 32, "d2_rechazo": 74,
    "d2_perdidas": 8, "d2_cierre": 96, "d2_factor": 4.2,
    "dist_metal_p": 86, "dist_metal_i": 6,  "dist_metal_r": 8,
    "dist_cu_p": 88,    "dist_cu_i": 5,     "dist_cu_r": 7,
    "dist_fe_p": 10,    "dist_fe_i": 20,    "dist_fe_r": 70,
    "dist_imp_p": 5,    "dist_imp_i": 15,   "dist_imp_r": 80,
    "wp2_action": "Escalar condición a banco para validar estabilidad.",
    "wp2_act_0": "Escalar condición a banco para validar estabilidad.",
    "wp2_act_1": "Optimizar dosis de colector para mejorar recuperación.",
    "wp2_act_2": "", "wp2_act_3": "", "wp2_act_4": "",
    "wp2_actvac_0": False, "wp2_actvac_1": False, "wp2_actvac_2": True,
    "wp2_actvac_3": True, "wp2_actvac_4": True,

    # ---- WP3 detalle ----
    "d3_remocion": 98, "d3_residual": 0.8, "d3_lixiviable": 1.5,
    "d3_residuo": 12, "d3_ph": 10.2, "d3_eh": 210,
    "as_v": 78, "as_iii": 18, "as_otros": 4,
    "d3_trend": "1.5,1.4,1.3,1.45,1.2,1.25,1.1,1.3,1.15,1.05,1.2,1.1,1.0",
    "wp3_action": "Revisar condición de estabilización del residuo.",
    "wp3_act_0": "Revisar condición de estabilización del residuo.",
    "wp3_act_1": "Monitorear As lixiviable según criterio interno.",
    "wp3_act_2": "", "wp3_act_3": "", "wp3_act_4": "",
    "wp3_actvac_0": False, "wp3_actvac_1": False, "wp3_actvac_2": True,
    "wp3_actvac_3": True, "wp3_actvac_4": True,

    # ---- Análisis químico por WP ----
    "q1_lab": "Lab. Geometalurgia", "q1_tecnica": "ICP-OES / AAS",
    "q1_enviadas": 42, "q1_analizadas": 38, "q1_pend": 4, "q1_dias": 3,
    "q1_estado": "En tiempo", "q1_fecha": "13-05-2026",
    "q1_tabla": "Cu;0,8;%\nFe;12,4;%\nAs;1500;ppm\nS;8,2;%\nAu;0,4;g/t",
    "q2_lab": "Lab. Concentración", "q2_tecnica": "ICP-OES",
    "q2_enviadas": 30, "q2_analizadas": 27, "q2_pend": 3, "q2_dias": 4,
    "q2_estado": "En tiempo", "q2_fecha": "13-05-2026",
    "q2_tabla": "Cu;28,5;%\nFe;9,1;%\nAs;320;ppm\nMo;0,12;%\nInsol;14;%",
    "q3_lab": "Lab. Medio Ambiente", "q3_tecnica": "ICP-MS / HG-AAS",
    "q3_enviadas": 24, "q3_analizadas": 20, "q3_pend": 4, "q3_dias": 5,
    "q3_estado": "Atrasado", "q3_fecha": "12-05-2026",
    "q3_tabla": "As total;1,5;mg/L\nAs(V);1,17;mg/L\nAs(III);0,27;mg/L\nFe;5,2;mg/L\npH;10,2;-",

    # ---- Caracterización mineralógica por WP ----
    "m1_tecnica": "QEMSCAN + DRX", "m1_p80": 150, "m1_lib": 82, "m1_estado": "Completo",
    "m1_tabla": "Pirita;34\nCalcopirita;9\nArsenopirita;6\nCuarzo;30\nÓxidos Fe;12\nOtros;9",
    "m2_tecnica": "QEMSCAN", "m2_p80": 120, "m2_lib": 88, "m2_estado": "Completo",
    "m2_tabla": "Calcopirita;41\nPirita;22\nGanga silícea;28\nMolibdenita;3\nOtros;6",
    "m3_tecnica": "DRX + Microscopía", "m3_p80": 180, "m3_lib": 75, "m3_estado": "En proceso",
    "m3_tabla": "Escorodita;38\nYeso;26\nFerrihidrita;18\nCuarzo;10\nOtros;8",

    # ---- Seguridad / HSE ----
    "s_dias_sin": 42, "s_inc_camp": 1, "s_inc_mes": 0, "s_near": 5,
    "s_acc_dias_sin": 128, "s_acc_camp": 0, "s_acc_ctp": 0, "s_acc_reg": 1, "s_dias_perd": 0,
    "s_if": 1.8, "s_ig": 12.0, "s_capacit": 94, "s_epp": 97,
    "s_inc_log": ("02-05-2026;Cuasi accidente;WP3;Bajo;Cerrado\n"
                  "28-04-2026;Derrame menor de reactivo;WP2;Medio;En seguimiento\n"
                  "15-04-2026;Contacto con reactivo;WP1;Bajo;Cerrado\n"
                  "10-04-2026;Resbalón sin lesión;Planta;Bajo;Cerrado"),
    "s_acc_log": ("18-03-2026;Accidente registrable;Esguince de tobillo;WP1;Cerrado\n"
                  "—;Sin accidentes con tiempo perdido en la campaña;—;—;—"),
    "s_acc_total": 12, "s_acc_cerradas": 9, "s_acc_abiertas": 3, "s_acc_vencidas": 1,
    "s_est_noini": 1, "s_est_des": 2, "s_est_rev": 1, "s_est_apr": 4,
    "s_cap_log": ("05-05-2026;Uso de EPP;Planta;18;Realizada\n"
                  "22-04-2026;Manejo de reactivos;WP2;12;Realizada\n"
                  "10-04-2026;Respuesta a derrames;WP3;9;Programada\n"
                  "02-04-2026;Trabajo en caliente;Planta;15;Pendiente"),
    "miper_actualiz": 88, "miper_peligros": 64, "miper_criticos": 7,
    "miper_bajos": 39, "miper_medios": 18, "miper_altos": 0,
    "miper_revision": "30-04-2026", "miper_proxima": "31-07-2026", "miper_estado": "Vigente",
    "s_next_cap": "Bloqueo y etiquetado (LOTO)", "s_next_cap_date": "15-06-2026",
    "s_alert1_level": "Alta", "s_alert1_desc": "Cerrar acción correctiva vencida en WP3.",
    "s_alert2_level": "Media", "s_alert2_desc": "Reprogramar capacitación pendiente de trabajo en caliente.",
    "s_alert3_level": "Baja", "s_alert3_desc": "Actualizar matriz MIPER antes de la próxima revisión.",
    "s_dias_sin_vac": False, "s_inc_vac": False, "s_near_vac": False, "s_acc_dias_sin_vac": False,
    "s_acc_vac": False, "s_acc_ctp_vac": False, "s_if_vac": False, "s_ig_vac": False,
    "s_capacit_vac": False, "s_epp_vac": False,
}

# ---- Avance y niveles detallados por WP (proceso unitario × nivel) ----
# Valores por defecto por nivel: (planificados, ejecutados, válidos, pendientes)
_AV_DEFAULT = {0: (5, 5, 5, 0), 1: (5, 4, 3, 1), 2: (4, 2, 1, 2), 3: (3, 1, 0, 2)}
_NIV_DEFAULT = {0: "Completado", 1: "En curso", 2: "Pendiente", 3: "Pendiente"}
for _wp in ("1", "2", "3"):
    for _pi in range(len(PROCS[_wp])):
        for _li in range(len(WP_LEVELS[_wp])):
            _p, _e, _v, _pe = _AV_DEFAULT[_li]
            DEFAULTS[f"w{_wp}av_{_pi}_{_li}_planif"] = _p
            DEFAULTS[f"w{_wp}av_{_pi}_{_li}_ejec"] = _e
            DEFAULTS[f"w{_wp}av_{_pi}_{_li}_valid"] = _v
            DEFAULTS[f"w{_wp}av_{_pi}_{_li}_pend"] = _pe
            DEFAULTS[f"w{_wp}niv_{_pi}_{_li}"] = _NIV_DEFAULT[_li]
            DEFAULTS[f"w{_wp}_req_{_pi}_{_li}"] = True
            DEFAULTS[f"w{_wp}_nivreq_{_pi}_{_li}"] = True
        DEFAULTS[f"wp{_wp}_proc{_pi}_ord"] = _pi + 1   # orden de visualización (editable)

# ---- Indicadores operacionales por WP ----
LEVEL_ABBR = ["Lab.", "Banco", "Semipiloto"]
_LVL_KEYS = ["lab", "ban", "spb"]
_MP_DEFAULT = [
    ("Concentrado 1", 1200), ("Concentrado 2", 800), ("Concentrado 3", 500), ("Concentrado 4", 300),
    ("Calcina oxidada 1", 600), ("Calcina oxidada 2", 400), ("Calcina oxidada 3", 200),
    ("Calcina reducida 1", 500), ("Calcina reducida 2", 300), ("Calcina reducida 3", 150),
    ("Calcina sulfatada", 250)]
_MP_COLOR_DEF = (["Azul"] * 4) + (["Naranja"] * 3) + (["Verde"] * 3) + ["Morado"] + (["Gris"] * 4)
for _wp in ("1", "2", "3"):
    DEFAULTS[f"ind{_wp}_disp"] = 85
    DEFAULTS[f"ind{_wp}_top"] = 135
    DEFAULTS[f"ind{_wp}_mant"] = 5
    DEFAULTS[f"ind{_wp}_agua"] = 4.2
    DEFAULTS[f"ind{_wp}_energia"] = 210
    DEFAULTS[f"ind{_wp}_seg"] = 1
    for _n in range(15):
        _nm, _vl = _MP_DEFAULT[_n] if _n < len(_MP_DEFAULT) else ("", 0)
        DEFAULTS[f"ind{_wp}_mp{_n}_name"] = _nm
        DEFAULTS[f"ind{_wp}_mp{_n}_val"] = _vl
        DEFAULTS[f"ind{_wp}_mp{_n}_on"] = (_n < len(_MP_DEFAULT))
        DEFAULTS[f"ind{_wp}_mp{_n}_color"] = _MP_COLOR_DEF[_n]

# ---- Pestaña AMPLIACIÓN (servicios/contratos) ----
DEFAULTS["amp_avance"] = 35          # avance general de la etapa de ampliación (%)
_AMP_DEFAULT = [
    ("Ingeniería de detalle", 80, "Desarrollo de planos y especificaciones técnicas."),
    ("Obras civiles", 45, "Fundaciones y montaje de estructuras."),
    ("Suministro de equipos", 30, "Adquisición e importación de equipos principales."),
    ("Montaje electromecánico", 10, "Instalación de equipos y conexionado."),
]
AMP_ESTADOS = ["Licitación", "Adjudicado", "En ejecución", "Recepción", "Cerrado"]
AMP_CRIT = ["Alta", "Media", "Baja"]
for _i in range(15):
    _nm, _pr, _ds = _AMP_DEFAULT[_i] if _i < len(_AMP_DEFAULT) else ("", 0, "")
    DEFAULTS[f"amp_serv{_i}_name"] = _nm
    DEFAULTS[f"amp_serv{_i}_prog"] = _pr
    DEFAULTS[f"amp_serv{_i}_desc"] = _ds
    DEFAULTS[f"amp_serv{_i}_resp"] = ""        # responsable / empresa contratista
    DEFAULTS[f"amp_serv{_i}_fecha"] = ""       # fecha objetivo / término
    DEFAULTS[f"amp_serv{_i}_estado"] = "En ejecución"   # estado contractual
    DEFAULTS[f"amp_serv{_i}_crit"] = "Media"            # criticidad
    DEFAULTS[f"amp_serv{_i}_vac"] = (_i >= len(_AMP_DEFAULT))   # vacíos los no usados

# ---- Pestaña GENERAL (parámetros operacionales + insumos) ----
_GEN_OP_DEFAULT = [
    ("Horas operadas", "132", "h"), ("Disponibilidad equipos", "87", "%"),
    ("Tiempo de mantención", "12", "d"), ("Paradas no programadas", "3", ""),
    ("Consumo de agua", "4.2", "m³/h"), ("Consumo de energía", "210", "kWh/h"),
]
for _i in range(12):
    _nm, _vl, _un = _GEN_OP_DEFAULT[_i] if _i < len(_GEN_OP_DEFAULT) else ("", "", "")
    DEFAULTS[f"gen_op{_i}_name"] = _nm
    DEFAULTS[f"gen_op{_i}_val"] = _vl
    DEFAULTS[f"gen_op{_i}_unit"] = _un
    DEFAULTS[f"gen_op{_i}_vac"] = (_i >= len(_GEN_OP_DEFAULT))
# Esquemas / logos (imágenes por URL) en la sección de parámetros operacionales
for _i in range(4):
    DEFAULTS[f"gen_logo{_i}_url"] = ""
    DEFAULTS[f"gen_logo{_i}_caption"] = ""
    DEFAULTS[f"gen_logo{_i}_vac"] = True
# Categorías sugeridas (para autocompletar) — el tipo es texto libre y editable por insumo
_INS_TYPES = ["Mineral / Concentrado", "Reactivo", "Combustible / Reductor",
              "Agua / Fluido", "Insumo de planta", "Otro"]
_GEN_INS_DEFAULT = [
    ("Concentrado de cobre", "1200", "Alimentación a oxidación", "Mineral / Concentrado"),
    ("Cal", "300", "Control de pH", "Reactivo"),
    ("Ácido sulfúrico", "450", "Lixiviación de calcina", "Reactivo"),
    ("Carbón reductor", "180", "Reducción de óxidos", "Combustible / Reductor"),
    ("Agua de proceso", "5000", "Pulpa y lavado", "Agua / Fluido"),
]
for _i in range(15):
    _nm, _ms, _us, _tp = _GEN_INS_DEFAULT[_i] if _i < len(_GEN_INS_DEFAULT) else ("", "", "", "Otro")
    DEFAULTS[f"gen_ins{_i}_name"] = _nm
    DEFAULTS[f"gen_ins{_i}_mass"] = _ms
    DEFAULTS[f"gen_ins{_i}_use"] = _us
    DEFAULTS[f"gen_ins{_i}_type"] = _tp     # tipo/categoría: nombre editable
    DEFAULTS[f"gen_ins{_i}_vac"] = (_i >= len(_GEN_INS_DEFAULT))

# ---- Detalle WP1: Oxidación y Reducción (cada proceso con 3 alimentaciones) ----
DEFAULTS["feed0_name"] = "Alim. 1"
DEFAULTS["feed1_name"] = "Alim. 2"
DEFAULTS["feed2_name"] = "Alim. 3"
DEFAULTS["quim_pie"] = True
DEFAULTS["min_pie"] = True
_EXTRA_LBL = ["Densidad pulpa (%)", "Tiempo retención (h)", "Agitación (rpm)", "P80 (µm)",
              "Dosis reactivo (g/t)", "Sólidos (%)", "Flujo (m³/h)", "Presión (bar)", "Rendimiento (%)"]
_OX_FEED = {0: (88, 96, 1.8, 680, 65, 38, 35, 4.0, 300, 75, 120, 40, 3.0, 1.2, 92),
            1: (85, 94, 1.9, 660, 63, 40, 33, 3.5, 290, 78, 110, 38, 2.8, 1.1, 90),
            2: (90, 97, 1.7, 700, 67, 36, 36, 4.5, 310, 72, 130, 41, 3.2, 1.3, 94)}
_RD_FEED = {0: (82, 78, 2.0, -120, 70, 25, 30, 3.0, 250, 80, 100, 38, 2.5, 1.0, 80),
            1: (80, 75, 2.1, -110, 68, 27, 28, 2.5, 240, 82, 90, 36, 2.3, 0.9, 78),
            2: (85, 80, 1.9, -130, 72, 24, 32, 3.5, 260, 78, 110, 40, 2.7, 1.1, 83)}
_OXLBL = ["Conversión global (%)", "Remoción As (%)", "pH", "Eh (mV)", "Temp. (°C)", "Consumo (kg/t)"] + _EXTRA_LBL
_RDLBL = ["Reducción (%)", "Recuperación (%)", "pH", "Eh (mV)", "Temp. (°C)", "Consumo (kg/t)"] + _EXTRA_LBL
_W2LBL = ["Recuperación (%)", "Ley de producto (%)", "pH", "Temp. (°C)",
          "Consumo reactivo (g/t)", "Rechazo impurezas (%)", "Densidad pulpa (%)",
          "Tiempo retención (h)", "Flujo (m³/h)", "P80 (µm)", "Dosis colector (g/t)", "Sólidos (%)",
          "Agitación (rpm)", "Presión (bar)", "Rendimiento (%)"]
_W2_FEED = {0: (86, 32, 2.0, 60, 120, 74, 35, 4.0, 3, 75, 100, 40, 250, 1.0, 90),
            1: (84, 30, 2.1, 58, 110, 72, 33, 3.5, 3, 78, 90, 38, 240, 0.9, 88),
            2: (88, 34, 1.9, 62, 130, 76, 36, 4.5, 3, 72, 110, 41, 260, 1.1, 92)}
_W3LBL = ["Remoción As (%)", "As volatilizado (%)", "pH", "Temp. (°C)",
          "Consumo reactivo (g/t)", "As fijado (%)", "As lixiviable (mg/L)",
          "Tiempo retención (h)", "Eh (mV)", "Generación residuo (kg/kg As)",
          "Dosis estabilizante (g/t)", "Sólidos (%)", "Flujo (m³/h)", "Presión (bar)", "Rendimiento (%)"]
_W3_FEED = {0: (98, 92, 10, 600, 120, 96, 1.5, 4.0, 210, 12, 100, 40, 3.0, 1.0, 90),
            1: (97, 90, 10, 580, 110, 95, 1.6, 3.5, 200, 13, 90, 38, 2.8, 0.9, 88),
            2: (99, 94, 10, 620, 130, 97, 1.4, 4.5, 220, 11, 110, 41, 3.2, 1.1, 92)}
_DET_GROUPS = [("ox", OX_PROCS, OX_METRICS, _OXLBL, _OX_FEED),
               ("rd", RD_PROCS, RD_METRICS, _RDLBL, _RD_FEED),
               ("s2", W2_PROCS, W2_METRICS, _W2LBL, _W2_FEED),
               ("s3", W3_PROCS, W3_METRICS, _W3LBL, _W3_FEED)]
for _grp, _procs, _metrics, _lbls, _feed in _DET_GROUPS:
    for _idx in range(len(_procs)):
        DEFAULTS[f"{_grp}{_idx}_avop"] = 60        # avance operacional (%)
        DEFAULTS[f"{_grp}{_idx}_cq"] = 82          # caract. química real (%)
        DEFAULTS[f"{_grp}{_idx}_cq_plan"] = 90     # caract. química planificada (%)
        DEFAULTS[f"{_grp}{_idx}_bd"] = 70
        DEFAULTS[f"{_grp}{_idx}_cm"] = 68          # caract. mineralógica real (%)
        DEFAULTS[f"{_grp}{_idx}_cm_plan"] = 85     # caract. mineralógica planificada (%)
        for _f in range(N_FEEDS):
            _vals = _feed[_f % 3]
            DEFAULTS[f"{_grp}{_idx}_f{_f}_active"] = (_f < 2)
            for _mi, (_m, _d) in enumerate(_metrics):
                DEFAULTS[f"{_grp}{_idx}_f{_f}_{_m}"] = _vals[_mi] if _mi < len(_vals) else 0
            DEFAULTS[f"{_grp}{_idx}_feed{_f}_name"] = FEED_LABELS[_f]
        for _i in range(len(_metrics)):
            DEFAULTS[f"{_grp}lbl_{_idx}_{_i}"] = _lbls[_i] if _i < len(_lbls) else f"Variable {_i + 1}"
            DEFAULTS[f"{_grp}vac_{_idx}_{_i}"] = (_i >= 15)   # variables 16-30 vacías por defecto
            DEFAULTS[f"{_grp}lvl_{_idx}_{_i}"] = "L"          # nomenclatura: L/B/S/SC
            DEFAULTS[f"{_grp}bold_{_idx}_{_i}"] = False        # negrita del nombre de variable
        # Estado de muestras — caracterización química (en análisis / completadas / pendientes)
        DEFAULTS[f"{_grp}{_idx}_q_proc"] = 2
        DEFAULTS[f"{_grp}{_idx}_q_comp"] = 7
        DEFAULTS[f"{_grp}{_idx}_q_pend"] = 3
        DEFAULTS[f"{_grp}{_idx}_q_tr"] = 4
        # Estado de muestras — caracterización mineralógica (DRX y QEMSCAN)
        for _t, _vals in (("drx", (2, 5, 1, 6)), ("qem", (1, 4, 1, 8))):
            _a, _c, _p, _tr = _vals
            DEFAULTS[f"{_grp}{_idx}_{_t}_ana"] = _a
            DEFAULTS[f"{_grp}{_idx}_{_t}_comp"] = _c
            DEFAULTS[f"{_grp}{_idx}_{_t}_pend"] = _p
            DEFAULTS[f"{_grp}{_idx}_{_t}_tr"] = _tr


# ---- KPIs por WP: completar a 18, agregar Meta 3/4 y casillas de vacío ----
for _wp in ("1", "2", "3"):
    for _i in range(1, 19):
        _b = f"wp{_wp}_kpi{_i}"
        for _f in ("op", "name", "desc", "ref", "meta2", "meta3", "meta4", "val"):
            DEFAULTS.setdefault(f"{_b}_{_f}", "")
        DEFAULTS.setdefault(f"{_b}_sem", "Verde")
        DEFAULTS[f"{_b}_vac"] = (_i > 5)          # KPI 1-5 visibles, 6-18 vacíos por defecto
        DEFAULTS[f"{_b}_m1vac"] = False
        DEFAULTS[f"{_b}_m2vac"] = False
        DEFAULTS[f"{_b}_m3vac"] = True            # Meta 3/4 ocultas hasta que se completen
        DEFAULTS[f"{_b}_m4vac"] = True
        DEFAULTS.setdefault(f"{_b}_ord", _i)       # posición de visualización (editable)


def _key_section(k):
    """Asigna cada parámetro a su pestaña: '1','2','3','seg' o None (global)."""
    if k.startswith("s_") or k.startswith("miper_"):
        return "seg"
    if k.startswith("hdr_"):
        return None
    if k.startswith("ox") or k.startswith("rd") or k.startswith("feed") or k in ("quim_pie", "min_pie"):
        return "1"
    if k.startswith("s2"):
        return "2"
    if k.startswith("s3"):
        return "3"
    for wp in ("1", "2", "3"):
        if (k.startswith(f"wp{wp}_") or k.startswith(f"w{wp}") or k.startswith(f"av{wp}_")
                or k.startswith(f"niv_wp{wp}") or k.startswith(f"ind{wp}_")
                or k.startswith(f"d{wp}_") or k.startswith(f"q{wp}_") or k.startswith(f"m{wp}_")):
            return wp
    if k.startswith("dist_"):
        return "2"
    if k in ("as_v", "as_iii", "as_otros"):
        return "3"
    return None


SECTION_KEYS = {sec: [k for k in DEFAULTS if _key_section(k) == sec]
                for sec in ("1", "2", "3", "seg")}
SECTION_META = [("1", "WP1 — Oxidación / Reducción", "🟠", "wp1"),
                ("2", "WP2 — Separación metalúrgica", "🟢", "wp2"),
                ("3", "WP3 — Arsénico", "🔴", "wp3"),
                ("seg", "Seguridad", "🛡️", "seguridad")]


def _coerce_to_default(k, v):
    """Ajusta el valor cargado al tipo del valor por defecto (evita None/str donde se espera número)."""
    d = DEFAULTS.get(k)
    if d is None:
        return v
    if isinstance(d, bool):
        if isinstance(v, str):
            return v.strip().lower() in ("true", "1", "sí", "si", "yes")
        return bool(v)
    if isinstance(d, int):
        try:
            return int(round(float(v)))
        except Exception:
            return d
    if isinstance(d, float):
        try:
            return float(v)
        except Exception:
            return d
    if isinstance(d, str):
        return "" if v is None else str(v)
    return v


def init_state():
    """Inicializa session_state y CONSERVA los valores al cambiar de página.

    Con navegación por páginas, Streamlit descarta el estado de los widgets que no se
    renderizan en una ejecución. Re-asignar cada clave de datos a sí misma la 'fija' como
    valor normal de sesión, evitando que vuelva a los valores por defecto al cambiar de
    pestaña. Solo se re-fijan las claves de DEFAULTS (no los file_uploader ni otros widgets,
    que no admiten asignación vía session_state).
    """
    for k in DEFAULTS:
        if k in st.session_state:
            st.session_state[k] = st.session_state[k]
        else:
            st.session_state[k] = DEFAULTS[k]


def reset_defaults():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.session_state["_msg"] = "Valores restablecidos por defecto."


def apply_upload_section(sec):
    up = st.session_state.get(f"up_{sec}")
    lbl = next((m[1] for m in SECTION_META if m[0] == sec), sec)
    if up is None:
        st.session_state["_msg"] = f"Primero selecciona un archivo JSON para {lbl}."
        return
    try:
        data = json.load(up)
        n = 0
        for k in SECTION_KEYS[sec]:
            if k in data:
                st.session_state[k] = _coerce_to_default(k, data[k]); n += 1
        st.session_state["_msg"] = f"Configuración de {lbl} cargada ({n} parámetros aplicados)."
    except Exception as e:
        st.session_state["_msg"] = f"Error al leer el JSON de {lbl}: {e}"


def apply_upload():
    up = st.session_state.get("uploader")
    if up is None:
        st.session_state["_msg"] = "Primero selecciona un archivo JSON."
        return
    try:
        data = json.load(up)
        n = 0
        for k in DEFAULTS:
            if k in data:
                st.session_state[k] = _coerce_to_default(k, data[k]); n += 1
        st.session_state["_msg"] = f"Configuración cargada ({n} parámetros aplicados)."
    except Exception as e:
        st.session_state["_msg"] = f"Error al leer el JSON: {e}"


init_state()

# ============================================================
# ESTILOS
# ============================================================
st.markdown(
    f"""
    <style>
      html, body, .stApp {{ font-size:16.8px; }}
      .stApp {{ background:{BG}; }}
      .block-container {{ padding-top:3rem; padding-bottom:2rem; max-width:100%;
                          padding-left:1.4rem; padding-right:1.4rem; }}
      .stApp {{ background:{BG} !important; }}
      [data-testid="stMain"], [data-testid="stMainBlockContainer"],
      [data-testid="stAppViewContainer"] {{ background:{BG} !important; }}
      [data-testid="stVerticalBlock"] {{ gap:0.55rem; }}
      [data-testid="stHorizontalBlock"] {{ gap:0.5rem; }}
      /* Tarjetas con esquinas rectas y borde igual a las pp-card */
      [data-testid="stVerticalBlockBorderWrapper"] {{ border:1px solid #9FACBB !important;
        border-radius:0 !important; background:{CELESTE} !important; }}

      .pp-header {{ background:{NAVY}; color:#fff; border-radius:0; padding:5px 16px;
        display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; }}
      .pp-header h1 {{ font-size:16px; margin:0; font-weight:800; color:#fff; line-height:1.3; }}
      .pp-header .meta {{ font-size:13px; color:#CBD6E2; }}
      .pp-badge {{ font-weight:800; font-size:13px; padding:3px 11px; border-radius:6px; }}

      .pp-card {{ background:{CELESTE}; border:1px solid #9FACBB; border-radius:0;
        padding:14px 16px; height:100%; }}
      .pp-card-title {{ font-weight:800; color:{NAVY}; font-size:16px; margin:0 0 4px 0; }}
      .pp-sub {{ color:{MUTED}; font-size:13px; }}

      /* Fondo unificado celeste de la ventana WP1 detalle (y sus cajas) + bordes */
      [class*="st-key-wp1_detail"],
      [class*="st-key-wp1_detail"] [data-testid="stVerticalBlockBorderWrapper"] {{ background:{CELESTE} !important; }}
      [class*="st-key-wp1_detail"], [class*="st-key-ox_box"], [class*="st-key-rd_box"],
      [class*="st-key-wp1_acc"], [class*="st-key-wp1_ind"], [class*="st-key-wp2_ind"],
      [class*="st-key-wp3_ind"], [class*="st-key-wp2_detail"], [class*="st-key-wp2_acc"],
      [class*="st-key-w2box_"], [class*="st-key-wp3_detail"], [class*="st-key-wp3_acc"],
      [class*="st-key-w3box_"] {{ border:1px solid #9FACBB !important; border-radius:0 !important;
        background:{CELESTE} !important; }}
      /* Sin espacio entre WP1 detalle, Acciones e Indicadores */
      [class*="st-key-wp1_acc"], [class*="st-key-wp1_ind"], [class*="st-key-wp2_acc"],
      [class*="st-key-wp2_ind"], [class*="st-key-wp3_acc"], [class*="st-key-wp3_ind"] {{
        margin-top:-0.55rem !important; }}
      /* Línea divisoria entre subventanas de procesos unitarios */
      [class*="st-key-ox_box"] [data-testid="stColumn"]:not(:first-child),
      [class*="st-key-rd_box"] [data-testid="stColumn"]:not(:first-child) {{
        border-left:1px solid #B9C4D0; padding-left:10px; }}
      .grp-title {{ color:#fff; font-weight:800; font-size:15px; text-align:center;
        padding:6px 8px; margin:0 0 6px 0; border-radius:0; letter-spacing:.5px; }}
      .grp-feed {{ font-size:11px; color:{MUTED}; text-align:center; margin-bottom:6px; }}
      .det-hd {{ background:{NAVY}; color:#fff; font-weight:800; font-size:16px;
        padding:7px 12px; margin:0 0 10px 0; letter-spacing:.5px; }}

      .kpi-label {{ color:{MUTED}; font-size:12px; line-height:1.2; }}
      .kpi-value {{ color:{TEXT}; font-weight:800; font-size:19px; }}
      .kpi-box {{ background:#F7F9FB; border:1px solid #E6ECF2; border-radius:8px; padding:8px 10px; }}

      .kpi-row {{ display:flex; align-items:center; gap:12px; padding:8px 10px;
        border:1px solid #E6ECF2; border-radius:8px; background:#F7F9FB; margin-bottom:6px; }}
      .kpi-row .op {{ font-size:11px; color:#fff; background:{NAVY}; padding:1px 8px;
        border-radius:10px; display:inline-block; margin-bottom:3px; font-weight:700; }}
      .kpi-row .knm {{ font-weight:800; color:{TEXT}; font-size:14px; }}
      .kpi-row .kds {{ color:{MUTED}; font-size:12px; }}
      .kpi-row .kcell {{ text-align:center; min-width:74px; }}
      .kpi-row .kcell b {{ color:{TEXT}; font-size:15px; }}
      .kpi-sem {{ width:18px; height:18px; border-radius:50%; display:inline-block; flex:none; }}

      .kpi-tbl {{ width:100%; border-collapse:collapse; font-size:14px; margin-top:12px;
        table-layout:auto; }}
      .kpi-tbl th {{ text-align:left; color:{MUTED}; font-weight:700; font-size:13px;
        padding:6px 8px; border-bottom:2px solid #E6ECF2; }}
      .kpi-tbl td {{ padding:7px 8px; border-bottom:1px solid #EEF2F6; color:{TEXT};
        vertical-align:middle; word-break:break-word; }}
      .kpi-tbl td:nth-child(n+4):nth-child(-n+9),
      .kpi-tbl th:nth-child(n+4):nth-child(-n+9) {{ white-space:nowrap; width:1%; }}
      .kpi-tbl .op {{ font-size:11px; color:#fff; background:{NAVY}; padding:2px 8px;
        border-radius:10px; display:inline-block; font-weight:700; white-space:nowrap; }}

      .pbar {{ background:#E6ECF2; border-radius:8px; height:14px; width:100%; overflow:hidden; }}
      .pfill {{ height:100%; border-radius:8px; }}

      .row {{ display:flex; justify-content:space-between; padding:3px 0;
        border-bottom:1px dashed #EAEFF4; font-size:14px; }}
      .row .lbl {{ color:{TEXT}; }} .row .val {{ font-weight:700; }}
      .tag {{ font-weight:800; font-size:13px; }}
      .dot {{ display:inline-block; width:14px; height:14px; border-radius:50%; }}

      .det-strip {{ color:#fff; font-weight:800; padding:8px 12px; border-radius:0;
        margin-bottom:10px; display:flex; justify-content:space-between; font-size:15px; }}
      .action {{ border-radius:0; padding:9px 12px; font-size:13.5px; margin-top:10px; }}

      .tbl {{ width:100%; border-collapse:collapse; font-size:14px; margin-top:6px; }}
      .tbl th {{ text-align:left; color:{MUTED}; font-weight:700; padding:5px 6px;
        border-bottom:2px solid #E6ECF2; }}
      .tbl td {{ padding:5px 6px; border-bottom:1px solid #EEF2F6; color:{TEXT}; }}
      .badge-sm {{ padding:2px 9px; border-radius:6px; font-size:12px; font-weight:700;
        display:inline-block; }}

      .ind-item {{ text-align:center; min-width:96px; padding:2px 4px; }}
      .ind-val {{ font-weight:800; font-size:18px; color:{NAVY}; }}
      .ind-lbl {{ font-size:12px; color:{MUTED}; line-height:1.2; }}
      .ind-tbl {{ border-collapse:collapse; font-size:13px; }}
      .ind-tbl th {{ color:#fff; background:{NAVY}; font-weight:700; font-size:11px;
        padding:3px 12px; text-align:center; }}
      .ind-tbl td {{ padding:3px 12px; text-align:center; border:1px solid #DCE3EB;
        color:{TEXT}; font-weight:800; background:{CELL}; }}
      .ind-tbl td.rlbl {{ text-align:left; color:{MUTED}; font-weight:700; }}
      .lvl-card {{ border:1px solid #C7D0DA; background:{CELL}; min-width:104px; }}
      .lvl-hd {{ background:{NAVY}; color:#fff; font-weight:800; font-size:12px;
        text-align:center; padding:3px 6px; }}
      .lvl-row {{ display:flex; justify-content:space-between; padding:3px 8px; font-size:12px;
        color:{TEXT}; border-top:1px solid #E3E9F0; }}
      .lvl-row span.k {{ color:{MUTED}; }}
      .lvl-row b {{ color:{NAVY}; }}

      /* ---- Legibilidad independiente del tema ---- */
      [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, label {{ color:{TEXT} !important; }}
      [data-testid="stExpander"] details {{ background:#FFFFFF; border:1px solid #DCE3EB; border-radius:8px; }}
      [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {{ color:{TEXT} !important; font-weight:700; }}
      [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {{ color:{TEXT} !important; }}
      .stTextInput input, .stNumberInput input, .stTextArea textarea,
      [data-baseweb="input"] input, [data-baseweb="base-input"] input {{ color:{TEXT} !important; background:#FFFFFF !important; }}
      [data-baseweb="select"] > div {{ color:{TEXT} !important; background:#FFFFFF !important; }}
      [data-testid="stFileUploaderDropzone"] {{ background:#FFFFFF !important; }}
      [data-testid="stFileUploaderDropzone"] * {{ color:{TEXT} !important; }}
      /* Pestañas superiores (estilo píldora, alto contraste) */
      .stTabs [data-baseweb="tab-list"] {{ gap:6px; background:#FFFFFF; padding:6px;
        border:1px solid #DCE3EB; border-radius:10px; flex-wrap:wrap; }}
      .stTabs [data-baseweb="tab"] {{ background:#F4F7FA; border-radius:8px;
        padding:6px 14px; min-height:42px; display:flex; align-items:center;
        white-space:nowrap; color:{TEXT} !important; }}
      .stTabs [data-baseweb="tab"] p {{ color:{TEXT} !important; font-weight:700; font-size:15px; }}
      .stTabs [aria-selected="true"] {{ background:{NAVY} !important; }}
      .stTabs [aria-selected="true"] p {{ color:#FFFFFF !important; }}
      .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ background:transparent !important; }}
      /* Navegación por páginas (radio estilizado como pestañas) */
      div[role="radiogroup"] {{ gap:6px; background:#FFFFFF; padding:6px; border:1px solid #DCE3EB;
        border-radius:10px; flex-wrap:wrap; justify-content:center; }}
      div[role="radiogroup"] > label {{ background:#F4F7FA; border-radius:8px; padding:8px 16px;
        min-height:42px; display:flex; align-items:center; cursor:pointer; margin:0 !important; }}
      div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p {{
        color:{TEXT} !important; font-weight:700; font-size:15px; margin:0; white-space:nowrap; }}
      div[role="radiogroup"] > label > div:first-child {{ display:none !important; }}
      div[role="radiogroup"] > label:has(input:checked) {{ background:{NAVY}; }}
      div[role="radiogroup"] > label:has(input:checked) div[data-testid="stMarkdownContainer"] p {{
        color:#FFFFFF !important; }}

      /* --- Nitidez: fuente nativa (Segoe UI en Windows) + render alineado a píxel --- */
      html, body, [class*="css"], .pp-card, .tbl, .kpi-tbl, .stMarkdown,
      [data-testid="stMarkdownContainer"], .stDataFrame, table, th, td {{
        font-family:"Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif !important;
        -webkit-font-smoothing:auto; -moz-osx-font-smoothing:auto;
        text-rendering:auto; }}

      /* --- Impresión / PDF: colores exactos, vectorial y sin cortes --- */
      @media print {{
        * {{ -webkit-print-color-adjust:exact !important; print-color-adjust:exact !important;
             color-adjust:exact !important; }}
        header, [data-testid="stToolbar"], [data-testid="stDecoration"],
        [data-testid="stStatusWidget"], #MainMenu, footer {{ display:none !important; }}
        .block-container {{ max-width:100% !important; padding:0.4rem 0.6rem !important; }}
        .pp-card, [data-testid="stVerticalBlockBorderWrapper"], .stPlotlyChart,
        table, tr {{ break-inside:avoid !important; page-break-inside:avoid !important; }}
        .stPlotlyChart, .js-plotly-plot, .plot-container, .svg-container {{
          width:100% !important; }}
      }}
      @page {{ size:A4 landscape; margin:8mm; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Configuración de gráficos: barra oculta y exportación en alta resolución / vectorial
CHART_CFG = {
    "displayModeBar": False,
    "responsive": True,
    "toImageButtonOptions": {"format": "svg", "scale": 3},
}

# ============================================================
# UTILIDADES
# ============================================================
def nf(v, dec=0):
    try:
        return f"{float(v):.{dec}f}"
    except (TypeError, ValueError):
        return str(v)


def pct1(v):
    """Formatea como porcentaje con máximo 1 decimal (sin .0 innecesario)."""
    try:
        f = round(float(v), 1)
        s = f"{f:.1f}".rstrip("0").rstrip(".")
        return f"{s}%"
    except (TypeError, ValueError):
        return f"{v}%"


def parse_series(text, fallback):
    try:
        vals = [float(x.strip().replace(",", ".")) for x in str(text).split(",") if x.strip()]
        return vals if len(vals) >= 2 else fallback
    except Exception:
        return fallback


def parse_table(text):
    out = []
    for line in str(text).splitlines():
        line = line.strip()
        if line:
            out.append([c.strip() for c in line.split(";")])
    return out


def line_chart(values, color, ymax, yticks, height=150, key=None):
    n = len(values)
    xs = [i * 24 / (n - 1) for i in range(n)] if n > 1 else [0]
    fig = go.Figure(go.Scatter(x=xs, y=values, mode="lines+markers",
        line=dict(color=color, width=2), marker=dict(color=color, size=5),
        hovertemplate="%{y}<extra></extra>"))
    fig.update_layout(height=height, margin=dict(l=34, r=8, t=6, b=22),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, font=dict(size=10, color=MUTED))
    fig.update_xaxes(range=[0, 24], tickvals=[0, 6, 12, 18, 24],
        ticktext=["00:00", "06:00", "12:00", "18:00", "24:00"],
        showgrid=False, zeroline=False, linecolor="#D7DEE6")
    fig.update_yaxes(range=[0, ymax], tickvals=yticks, gridcolor="#EDF1F5",
        zeroline=False, linecolor="#D7DEE6")
    return fig


def donut_chart(values, labels, colors, height=190, key=None):
    txt = [f"{labels[i]}  {nf(values[i])}%" for i in range(len(values))]
    fig = go.Figure(go.Pie(values=values, labels=txt, hole=0.62,
        marker=dict(colors=colors, line=dict(color="#fff", width=2)),
        textinfo="none", sort=False, direction="clockwise",
        hovertemplate="%{label}<extra></extra>"))
    fig.update_layout(height=height, margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=11, color=TEXT)))
    return fig


def stacked_dist(rows, height=210, key=None):
    names = [r[0] for r in rows][::-1]
    prod = [r[1] for r in rows][::-1]
    inter = [r[2] for r in rows][::-1]
    rel = [r[3] for r in rows][::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=names, x=prod, orientation="h", name="Producto / Concentrado",
        marker_color=WP2, text=[nf(v) for v in prod], textposition="inside",
        insidetextanchor="middle", textfont=dict(color="#fff", size=11)))
    fig.add_trace(go.Bar(y=names, x=inter, orientation="h", name="Intermedio",
        marker_color=GRAY, text=[nf(v) for v in inter], textposition="inside",
        insidetextanchor="middle", textfont=dict(color="#fff", size=11)))
    fig.add_trace(go.Bar(y=names, x=rel, orientation="h", name="Relave / Descarte",
        marker_color=WP3, text=[nf(v) for v in rel], textposition="inside",
        insidetextanchor="middle", textfont=dict(color="#fff", size=11)))
    fig.update_layout(barmode="stack", height=height, margin=dict(l=8, r=8, t=28, b=6),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", x=0, y=1.18, font=dict(size=10, color=TEXT)),
        font=dict(color=TEXT, size=11))
    fig.update_xaxes(visible=False, range=[0, 100]); fig.update_yaxes(showgrid=False)
    return fig


def kv(label, value, color=None, dec=0, unit=""):
    c = color or TEXT
    val = f"{nf(value, dec)} {unit}".strip() if unit else nf(value, dec)
    return (f"<div class='row'><span class='lbl'>{label}</span>"
            f"<span class='val' style='color:{c}'>{val}</span></div>")


def badge(text, cmap):
    color = cmap.get(text, GRAY)
    fg = NAVY if color == YELLOW else "#fff"
    return f"<span class='badge-sm' style='background:{color};color:{fg}'>{text}</span>"


def row_mini(label, value_html):
    return (f"<div class='row'><span class='lbl' style='font-size:12px'>{label}</span>"
            f"<span class='val' style='font-size:12px;white-space:nowrap;text-align:right;"
            f"font-variant-numeric:tabular-nums'>{value_html}</span></div>")


def char_block(title, items):
    """Bloque de caracterización: un título y varias barras con etiqueta a la izquierda."""
    rows = ""
    for lbl, val, col in items:
        try:
            p = max(0, min(100, float(val)))
        except (TypeError, ValueError):
            p = 0
        rows += (
            f"<div style='display:flex;align-items:center;gap:6px;margin-top:3px'>"
            f"<span style='width:68px;font-size:11px;color:{TEXT};font-weight:700'>{lbl}</span>"
            f"<div class='pbar' style='flex:1;height:9px'>"
            f"<div class='pfill' style='width:{p}%;background:{col};height:100%'></div></div>"
            f"<b style='font-size:12px;color:{TEXT};width:36px;text-align:right'>{nf(p)}%</b></div>")
    return (f"<div style='margin-top:8px'>"
            f"<div style='font-size:11px;color:{TEXT};font-weight:700;margin-bottom:1px'>{title}</div>"
            f"{rows}</div>")


def status_bar(label, pct, color):
    try:
        p = max(0, min(100, float(pct)))
    except (TypeError, ValueError):
        p = 0
    return (f"<div style='margin-top:6px'>"
            f"<div style='font-size:11px;color:{TEXT};font-weight:700;margin-bottom:2px'>{label}</div>"
            f"<div style='display:flex;align-items:center;gap:6px'>"
            f"<div class='pbar' style='flex:1;height:9px'>"
            f"<div class='pfill' style='width:{p}%;background:{color};height:100%'></div></div>"
            f"<b style='font-size:12px;color:{TEXT}'>{nf(p)}%</b></div></div>")


def _feed_vals(grp, idx, metric, dec=0):
    g = st.session_state
    parts = []
    for f in range(N_FEEDS):
        if g.get(f'{grp}{idx}_f{f}_active', False):
            v = g[f'{grp}{idx}_f{f}_{metric}']
            col = FEED_COLORS[f]
            if metric == "eh":
                try:
                    if float(v) < 0:
                        col = REDTXT
                except (TypeError, ValueError):
                    pass
            parts.append(f"<b style='color:{col}'>{nf(v, dec)}</b>")
    return " / ".join(parts) if parts else "—"


_LIGHTBLUE = "#7CB3E8"   # En análisis
_REDPIE = "#E0443A"      # Pendientes
_GREENP = "#2BAE66"      # Completada(s)
_PIE_LABELS = ["En análisis", "Completada", "Pendientes"]
_PIE_COLS = [_LIGHTBLUE, _GREENP, _REDPIE]


def _pie_legend():
    items = [("En análisis", _LIGHTBLUE), ("Completada", _GREENP), ("Pendientes", _REDPIE)]
    inner = " &nbsp;|&nbsp; ".join(
        f"<span style='display:inline-block;width:9px;height:9px;background:{c};"
        f"margin-right:3px;vertical-align:middle'></span>"
        f"<span style='vertical-align:middle'>{l}</span>" for l, c in items)
    return f"<div style='font-size:10px;color:{TEXT};text-align:center;margin-top:1px'>{inner}</div>"


def _quim_samples(grp, idx):
    g = st.session_state
    proc = g[f'{grp}{idx}_q_proc']; comp = g[f'{grp}{idx}_q_comp']
    pend = g[f'{grp}{idx}_q_pend']; tr = g[f'{grp}{idx}_q_tr']
    total = proc + comp + pend
    if g.get('quim_pie', False):
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        fig = go.Figure(go.Pie(
            values=[proc, comp, pend], labels=_PIE_LABELS,
            domain={'x': [0.22, 0.78]}, hole=0.5, sort=False,
            marker=dict(colors=_PIE_COLS, line=dict(color="#fff", width=1)),
            textinfo="percent", texttemplate="<b>%{percent:.0%}</b>",
            insidetextorientation="horizontal", textposition="inside",
            textfont=dict(size=11, color="#000")))
        fig.update_layout(height=94, margin=dict(l=2, r=2, t=2, b=2),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, width='stretch', config=CHART_CFG, key=f"qpie_{grp}{idx}")
        st.markdown(_pie_legend(), unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:10px;color:{MUTED};text-align:center;margin-top:7px'>"
            f"Total de muestras: {nf(total)} / Tiempo de respuesta: {nf(tr)} días</div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div style='font-size:10.5px;color:{TEXT};margin-top:2px;line-height:1.5'>"
            f"<b>Muestras</b> — En anál.: <b style='color:{BLUE}'>{nf(proc)}</b> · "
            f"Compl.: <b style='color:{WP2}'>{nf(comp)}</b> · "
            f"Pend.: <b style='color:{REDTXT}'>{nf(pend)}</b><br>"
            f"Total de muestras: <b>{nf(total)}</b> / Tiempo de respuesta: <b>{nf(tr)} días</b></div>",
            unsafe_allow_html=True)


def _min_samples(grp, idx):
    g = st.session_state
    d = {t: {k: g[f'{grp}{idx}_{t}_{k}'] for k in ('ana', 'comp', 'pend', 'tr')}
         for t in ('drx', 'qem')}
    if g.get('min_pie', False):
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        fig = go.Figure()
        for dom, t, lbl in (([0.0, 0.46], 'drx', 'DRX'), ([0.54, 1.0], 'qem', 'QEMSCAN')):
            fig.add_trace(go.Pie(
                values=[d[t]['ana'], d[t]['comp'], d[t]['pend']], labels=_PIE_LABELS,
                domain={'x': dom}, hole=0.5, sort=False,
                title=dict(text=f"<b>{lbl}</b>", font=dict(size=11, color=NAVY), position="top center"),
                marker=dict(colors=_PIE_COLS, line=dict(color="#fff", width=1)),
                textinfo="percent", texttemplate="<b>%{percent:.0%}</b>",
                insidetextorientation="horizontal", textposition="inside",
                textfont=dict(size=10, color="#000")))
        fig.update_layout(height=112, margin=dict(l=2, r=2, t=22, b=2),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, width='stretch', config=CHART_CFG, key=f"minpie_{grp}{idx}")
        st.markdown(_pie_legend(), unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:10px;color:{MUTED};text-align:center;margin-top:7px;line-height:1.5'>"
            f"DRX — Total: {nf(d['drx']['ana']+d['drx']['comp']+d['drx']['pend'])} / "
            f"T. resp.: {nf(d['drx']['tr'])} días<br>"
            f"QEMSCAN — Total: {nf(d['qem']['ana']+d['qem']['comp']+d['qem']['pend'])} / "
            f"T. resp.: {nf(d['qem']['tr'])} días</div>", unsafe_allow_html=True)
    else:
        for t, lbl in (('drx', 'DRX'), ('qem', 'QEMSCAN')):
            x = d[t]; tot = x['ana'] + x['comp'] + x['pend']
            st.markdown(
                f"<div style='font-size:10.5px;color:{TEXT};line-height:1.5'>"
                f"<b>{lbl}</b> — En anál.: <b style='color:{BLUE}'>{nf(x['ana'])}</b> · "
                f"Compl.: <b style='color:{WP2}'>{nf(x['comp'])}</b> · "
                f"Pend.: <b style='color:{REDTXT}'>{nf(x['pend'])}</b> · "
                f"Total: <b>{nf(tot)}</b> · T. resp.: <b>{nf(x['tr'])} días</b></div>",
                unsafe_allow_html=True)


def _feed_nonzero(grp, idx, metric):
    """True si alguna alimentación activa tiene un valor distinto de cero (o texto)."""
    g = st.session_state
    for f in range(N_FEEDS):
        if g.get(f'{grp}{idx}_f{f}_active', False):
            v = g.get(f'{grp}{idx}_f{f}_{metric}', 0)
            try:
                if float(v) != 0:
                    return True
            except (TypeError, ValueError):
                if str(v).strip():
                    return True
    return False


def render_subproc(grp, idx, procname, metrics, per_op_feeds=False):
    g = st.session_state
    head = f"<div style='font-weight:800;color:{NAVY};font-size:13px;margin-bottom:2px'>{procname}</div>"
    if per_op_feeds:
        active = [f for f in range(N_FEEDS) if g.get(f'{grp}{idx}_f{f}_active', False)]
        leg = " · ".join(
            f"<b style='color:{FEED_COLORS[f]}'>{g.get(f'{grp}{idx}_feed{f}_name', FEED_LABELS[f])}</b>"
            for f in active) or "—"
        head += (f"<div style='font-size:10px;color:{MUTED};margin-bottom:4px'>"
                 f"Alim.: {leg}</div>")
    rows = ""
    for i, (metric, dec) in enumerate(metrics):
        if g.get(f'{grp}vac_{idx}_{i}', False):
            continue
        if not _feed_nonzero(grp, idx, metric):   # ocultar variable con valor cero
            continue
        lvl = g.get(f'{grp}lvl_{idx}_{i}', 'L')
        nm = g[f'{grp}lbl_{idx}_{i}']
        if g.get(f'{grp}bold_{idx}_{i}', False):
            nm = f"<b>{nm}</b>"
        label = (f"<b style='color:{BLUE}'>[{lvl}]</b> {nm}")
        rows += row_mini(label, _feed_vals(grp, idx, metric, dec))
    st.markdown(head + rows, unsafe_allow_html=True)
    # Avance operacional (tras las variables, antes de caracterización química)
    st.markdown(
        "<div style='height:6px'></div>"
        + status_bar("Avance operacional", g.get(f'{grp}{idx}_avop', 0), WP1),
        unsafe_allow_html=True)
    # Caracterización química: Real + Planificada (un título, dos barras etiquetadas)
    st.markdown(
        char_block("Caracterización química",
                   [("Real", g[f'{grp}{idx}_cq'], BLUE),
                    ("Planificada", g.get(f'{grp}{idx}_cq_plan', 0), "#9DBEE0")]),
        unsafe_allow_html=True)
    _quim_samples(grp, idx)
    # Caracterización mineralógica: Real + Planificada
    st.markdown(
        "<div style='height:6px'></div>"
        + char_block("Caracterización mineralógica",
                     [("Real", g[f'{grp}{idx}_cm'], PURPLE),
                      ("Planificada", g.get(f'{grp}{idx}_cm_plan', 0), "#C3B0E0")]),
        unsafe_allow_html=True)
    _min_samples(grp, idx)


def subproc_editor(grp, idx, pn, metrics):
    """Editor de un subproceso/operación unitaria (variables, alimentaciones, barras y muestras)."""
    st.markdown(f"**{pn}** — operación unitaria")
    st.caption("Tipos de alimentación de esta operación (hasta 5, independientes)")
    for r0 in range(0, N_FEEDS, 3):
        fc = st.columns(3)
        for j in range(3):
            f = r0 + j
            if f >= N_FEEDS:
                continue
            fc[j].text_input(f"Alimentación {f + 1}", key=f"{grp}{idx}_feed{f}_name")
    st.caption("Nombre de cada variable · Nivel L/B/S/SC · «Negrita» resalta el nombre · «Vacío» oculta la fila.")
    for i, (m, d) in enumerate(metrics):
        vc = st.columns([4, 1, 1, 1])
        vc[0].text_input(f"Variable {i + 1}", key=f"{grp}lbl_{idx}_{i}",
                         label_visibility="collapsed", placeholder=METRIC_NAME.get(m, m))
        vc[1].selectbox("Nivel", LVL_TAGS, key=f"{grp}lvl_{idx}_{i}", label_visibility="collapsed")
        vc[2].checkbox("Negrita", key=f"{grp}bold_{idx}_{i}")
        vc[3].checkbox("Vacío", key=f"{grp}vac_{idx}_{i}", help="Ocultar esta fila")
    st.caption("Valores por tipo de alimentación (marca «presentar» las que apliquen; el resto queda vacío)")
    for f in range(N_FEEDS):
        fn = st.session_state.get(f'{grp}{idx}_feed{f}_name', FEED_LABELS[f])
        st.checkbox(f"{fn} — presentar", key=f"{grp}{idx}_f{f}_active")
        for r0 in range(0, len(metrics), 5):
            vc = st.columns(5)
            for j in range(5):
                mi = r0 + j
                if mi >= len(metrics):
                    continue
                m, d = metrics[mi]
                vlbl = st.session_state.get(f'{grp}lbl_{idx}_{mi}', METRIC_NAME.get(m, m))
                vc[j].number_input(
                    f"{vlbl} ({fn})", step=(0.1 if d == 1 else 1),
                    format=("%.1f" if d == 1 else None), key=f"{grp}{idx}_f{f}_{m}")
    st.caption("Barras de avance del subproceso")
    bc = st.columns(3)
    bc[0].number_input("Avance operacional (%)", step=1, key=f"{grp}{idx}_avop")
    bc[1].number_input("Caract. química — real (%)", step=1, key=f"{grp}{idx}_cq")
    bc[2].number_input("Caract. química — planificada (%)", step=1, key=f"{grp}{idx}_cq_plan")
    bc = st.columns(2)
    bc[0].number_input("Caract. mineralógica — real (%)", step=1, key=f"{grp}{idx}_cm")
    bc[1].number_input("Caract. mineralógica — planificada (%)", step=1, key=f"{grp}{idx}_cm_plan")
    st.caption("Estado de muestras — Caracterización química")
    qc = st.columns(4)
    qc[0].number_input("Química · En análisis", step=1, key=f"{grp}{idx}_q_proc")
    qc[1].number_input("Química · Completadas", step=1, key=f"{grp}{idx}_q_comp")
    qc[2].number_input("Química · Pendientes", step=1, key=f"{grp}{idx}_q_pend")
    qc[3].number_input("Química · T. resp. (días)", step=1, key=f"{grp}{idx}_q_tr")
    for tech, tl in (("drx", "DRX"), ("qem", "QEMSCAN")):
        st.caption(f"Estado de muestras — Caracterización mineralógica · {tl}")
        mc = st.columns(4)
        mc[0].number_input(f"{tl} · En análisis", step=1, key=f"{grp}{idx}_{tech}_ana")
        mc[1].number_input(f"{tl} · Completada", step=1, key=f"{grp}{idx}_{tech}_comp")
        mc[2].number_input(f"{tl} · Pendientes", step=1, key=f"{grp}{idx}_{tech}_pend")
        mc[3].number_input(f"{tl} · T. resp. (días)", step=1, key=f"{grp}{idx}_{tech}_tr")
    st.divider()


# ============================================================
# COMPONENTES DEL DASHBOARD
# ============================================================
def render_header():
    g = st.session_state
    st.markdown(
        f"""<div class="pp-header">
          <h1>{g['hdr_title']}</h1>
          <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap;">
            <span class="meta">Actualizado: {g['hdr_updated']}</span>
            <span class="pp-badge" style="background:{STATUS_COLOR[g['hdr_status']]};
              color:{'#fff' if g['hdr_status'] != 'AMARILLO' else NAVY};">
              ESTADO GLOBAL: {g['hdr_status']}</span>
          </div></div>""",
        unsafe_allow_html=True)


def render_summary(wp, color, bar_color=None):
    g = st.session_state
    bar = bar_color or color
    name, level, prog = g[f'wp{wp}_name'], g[f'wp{wp}_level'], g[f'wp{wp}_progress']

    # KPIs visibles, ordenados por su campo «Orden» (luego por número de casilla)
    def _ord(i):
        try:
            return float(g.get(f'wp{wp}_kpi{i}_ord', i))
        except (TypeError, ValueError):
            return float(i)
    vis = sorted((i for i in range(1, 19) if not g.get(f'wp{wp}_kpi{i}_vac', False)),
                 key=lambda i: (_ord(i), i))

    META_DEFS = [("Meta 1", "ref", "m1vac", False), ("Meta 2", "meta2", "m2vac", False),
                 ("Meta 3", "meta3", "m3vac", True), ("Meta 4", "meta4", "m4vac", True)]

    def _metaval(i, fld, vack, vdef):
        return "" if g.get(f'wp{wp}_kpi{i}_{vack}', vdef) else str(g[f'wp{wp}_kpi{i}_{fld}'])

    # Solo se muestran las columnas de meta que tengan algún valor en los KPIs visibles
    shown = [k for k, (lbl, fld, vack, vdef) in enumerate(META_DEFS)
             if any(_metaval(i, fld, vack, vdef).strip() for i in vis)]

    body = ""
    for i in vis:
        op = g[f'wp{wp}_kpi{i}_op']; nm = g[f'wp{wp}_kpi{i}_name']; ds = g[f'wp{wp}_kpi{i}_desc']
        vl = g[f'wp{wp}_kpi{i}_val']; sm = g[f'wp{wp}_kpi{i}_sem']
        scol = SEM_MAP.get(sm, GRAY)
        metacells = "".join(
            f"<td style='text-align:center'>{_metaval(i, *META_DEFS[k][1:])}</td>" for k in shown)
        body += (
            f"<tr><td><span class='op'>{op}</span></td>"
            f"<td style='font-weight:700'>{nm}</td>"
            f"<td style='color:{MUTED}'>{ds}</td>"
            f"{metacells}"
            f"<td style='text-align:center;font-weight:800'>{vl}</td>"
            f"<td style='text-align:center'><span class='kpi-sem' style='background:{scol}' title='{sm}'></span></td></tr>")
    metahead = "".join(f"<th style='text-align:center'>{META_DEFS[k][0]}</th>" for k in shown)
    content = (
        "<table class='kpi-tbl'><tr>"
        "<th>Operación unitaria</th><th>Descripción objetivo</th><th>Descripción KPI</th>"
        f"{metahead}"
        "<th style='text-align:center'>Resultado</th><th style='text-align:center'></th>"
        f"</tr>{body}</table>")
    st.markdown(
        f"""<div class="pp-card">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <span class="dot" style="background:{bar}"></span>
            <span class="pp-card-title" style="flex:1;color:#000;font-weight:800">WP{wp} &nbsp; {name}</span>
            <span class="tag" style="color:{color}">{level}</span></div>
          {content}</div>""",
        unsafe_allow_html=True)


def proc_order(wp):
    """Índices de operaciones unitarias ordenados por su campo «Orden» (luego por posición)."""
    g = st.session_state
    n = len(PROCS[wp])
    def _o(pi):
        try:
            return float(g.get(f'wp{wp}_proc{pi}_ord', pi + 1))
        except (TypeError, ValueError):
            return float(pi + 1)
    return sorted(range(n), key=lambda pi: (_o(pi), pi))


def render_avance(wp):
    g = st.session_state
    procs = PROCS[wp]
    levels = WP_LEVELS[wp]
    P_COL, E_COL, V_COL, PE_COL = NAVY, BLUE, PURPLE, "#C0497E"
    head = "<tr><th>Proceso unitario</th>" + "".join(
        f"<th style='text-align:center'>{l}</th>" for l in levels) + "</tr>"
    body = ""
    for pi in proc_order(wp):
        proc = procs[pi]
        cells = ""
        for li in range(len(levels)):
            if not g.get(f'w{wp}_req_{pi}_{li}', True):
                cells += "<td></td>"
                continue
            p = g[f'w{wp}av_{pi}_{li}_planif']; e = g[f'w{wp}av_{pi}_{li}_ejec']
            v = g[f'w{wp}av_{pi}_{li}_valid']; pe = g[f'w{wp}av_{pi}_{li}_pend']

            def _rel(x, base):
                try:
                    b = float(base)
                    return pct1(100 * float(x) / b) if b else "—"
                except (TypeError, ValueError, ZeroDivisionError):
                    return "—"
            cells += (
                f"<td style='text-align:center;white-space:nowrap'>"
                f"<b style='color:{P_COL}'>{p}</b> / <b style='color:{E_COL}'>{_rel(e, p)}</b> / "
                f"<b style='color:{V_COL}'>{_rel(v, e)}</b> / <b style='color:{PE_COL}'>{_rel(pe, p)}</b></td>")
        body += f"<tr><td>{proc}</td>{cells}</tr>"
    legend = (
        f"<span style='font-size:12px;color:{TEXT}'>Formato "
        f"<b style='color:{P_COL}'>P</b> / <b style='color:{E_COL}'>E</b> / "
        f"<b style='color:{V_COL}'>V</b> / <b style='color:{PE_COL}'>Pend</b> &nbsp;=&nbsp; "
        f"<b style='color:{P_COL}'>Planificados</b> (valor) · <b style='color:{E_COL}'>Ejecutados</b> "
        f"(% de planificados) · <b style='color:{V_COL}'>Válidos</b> (% de ejecutados) · "
        f"<b style='color:{PE_COL}'>Pendientes</b> (% de planificados)</span>")
    st.markdown(
        "<div class='pp-card'><div class='pp-card-title'>AVANCE EXPERIMENTAL</div>"
        f"<table class='tbl'>{head}{body}</table>"
        f"<div style='margin-top:8px'>{legend}</div></div>", unsafe_allow_html=True)


def render_niveles(wp):
    g = st.session_state
    procs = PROCS[wp]
    levels = WP_LEVELS[wp]
    def dot(state):
        return f"<span class='dot' style='background:{LEVEL_DOT[state]}' title='{state}'></span>"
    head = "<tr><th>Proceso unitario</th>" + "".join(
        f"<th style='text-align:center'>{l}</th>" for l in levels) + "</tr>"
    body = ""
    for pi in proc_order(wp):
        proc = procs[pi]
        cells = ""
        for li in range(len(levels)):
            if not g.get(f'w{wp}_nivreq_{pi}_{li}', True):
                cells += "<td></td>"
                continue
            cells += f"<td style='text-align:center'>{dot(g[f'w{wp}niv_{pi}_{li}'])}</td>"
        body += f"<tr><td>{proc}</td>{cells}</tr>"
    legend = "".join(
        f"<span style='margin-right:14px;font-size:12px;color:{TEXT}'>"
        f"<span class='dot' style='width:10px;height:10px;background:{cc};vertical-align:middle'></span> {s}</span>"
        for s, cc in LEVEL_DOT.items())
    st.markdown(
        "<div class='pp-card'><div class='pp-card-title'>NIVELES DE EXPERIMENTACIÓN</div>"
        f"<table class='tbl'>{head}{body}</table>"
        f"<div style='margin-top:10px'>{legend}</div></div>", unsafe_allow_html=True)


def _old_render_avance(wp):
    g = st.session_state
    p, e, v, c = g[f'av{wp}_planif'], g[f'av{wp}_ejec'], g[f'av{wp}_valid'], g[f'av{wp}_pend']
    prog = g[f'wp{wp}_progress']
    color = {"1": WP1, "2": WP2, "3": WP3}[wp]
    st.markdown(
        f"""<div class="pp-card">
          <div class="pp-card-title">AVANCE EXPERIMENTAL</div>
          <div style="display:flex;gap:6px;margin:10px 0 12px 0;">
            <div style="flex:1"><div class="kpi-value">📅 {p}</div><div class="kpi-label">Planificados</div></div>
            <div style="flex:1"><div class="kpi-value">⚗️ {e}</div><div class="kpi-label">Ejecutados</div></div>
            <div style="flex:1"><div class="kpi-value">✅ {v}</div><div class="kpi-label">Válidos</div></div>
            <div style="flex:1"><div class="kpi-value" style="color:{REDTXT}">⚠️ {c}</div><div class="kpi-label">Pendientes</div></div>
          </div></div>""",
        unsafe_allow_html=True)


def _old_render_niveles(wp):
    g = st.session_state
    def dot(state):
        return f"<span class='dot' style='background:{LEVEL_DOT[state]}' title='{state}'></span>"
    st.markdown(f"<div class='pp-card'>{dot(g[f'niv_wp{wp}_lab'])}</div>", unsafe_allow_html=True)


def render_riesgos(wp):
    g = st.session_state
    icon = {"Alta": "❗", "Media": "⚠️", "Baja": "ℹ️"}
    rows = ""
    for i in (1, 2, 3):
        lvl = g[f'wp{wp}_r{i}_level']; desc = g[f'wp{wp}_r{i}_desc']
        if lvl == "—" or not desc.strip():
            continue
        bg, fg = RISK_STYLE[lvl]
        rows += (f"<div style='display:flex;align-items:center;gap:8px;margin:9px 0'>"
                 f"<span class='pp-badge' style='background:{bg};color:{fg};font-size:12px;padding:4px 10px'>{lvl}</span>"
                 f"<span style='flex:1;font-size:13.5px;color:{TEXT}'>{desc}</span>"
                 f"<span>{icon[lvl]}</span></div>")
    if not rows:
        rows = f"<div style='color:{WP2};font-size:14px;margin-top:8px'>✅ Sin alertas activas</div>"
    st.markdown(f"""<div class="pp-card"><div class="pp-card-title">RIESGOS / ALERTAS</div>
                    <div style="margin-top:8px">{rows}</div></div>""", unsafe_allow_html=True)


def render_quimico(wp):
    g = st.session_state
    lab, tec = g[f'q{wp}_lab'], g[f'q{wp}_tecnica']
    env, ana, pen, dias = g[f'q{wp}_enviadas'], g[f'q{wp}_analizadas'], g[f'q{wp}_pend'], g[f'q{wp}_dias']
    est, fecha = g[f'q{wp}_estado'], g[f'q{wp}_fecha']
    compl = round(100 * ana / env) if env else 0
    rows = parse_table(g[f'q{wp}_tabla'])
    body = "".join(
        f"<tr><td>{(r+['',''])[0]}</td><td style='text-align:right;font-weight:700'>{(r+['',''])[1]}</td>"
        f"<td style='color:{MUTED}'>{(r+['','',''])[2]}</td></tr>" for r in rows)
    with st.container(border=True):
        st.markdown(
            f"""<div class="pp-card-title">🧪 ESTADO DE ANÁLISIS QUÍMICO</div>
              <div class="pp-sub">{lab} &nbsp;·&nbsp; {tec} &nbsp;·&nbsp; Últ. resultado: {fecha}
                &nbsp; {badge(est, QEST_MAP)}</div>
              <div style="display:flex;gap:8px;margin-top:10px">
                <div class='kpi-box' style='flex:1'><div class='kpi-label'>Enviadas</div><div class='kpi-value'>{env}</div></div>
                <div class='kpi-box' style='flex:1'><div class='kpi-label'>Analizadas</div><div class='kpi-value'>{ana}</div></div>
                <div class='kpi-box' style='flex:1'><div class='kpi-label'>Pendientes</div><div class='kpi-value' style='color:{REDTXT}'>{pen}</div></div>
                <div class='kpi-box' style='flex:1'><div class='kpi-label'>Completitud</div><div class='kpi-value'>{compl}%</div></div>
                <div class='kpi-box' style='flex:1'><div class='kpi-label'>T. respuesta</div><div class='kpi-value'>{nf(dias)} d</div></div>
              </div>
              <table class='tbl'><tr><th>Elemento / Parámetro</th><th style='text-align:right'>Ley / Valor</th><th>Unidad</th></tr>{body}</table>""",
            unsafe_allow_html=True)


def render_mineralogia(wp):
    g = st.session_state
    tec, p80, lib, est = g[f'm{wp}_tecnica'], g[f'm{wp}_p80'], g[f'm{wp}_lib'], g[f'm{wp}_estado']
    rows = parse_table(g[f'm{wp}_tabla'])
    labels = [r[0] for r in rows if len(r) >= 2]
    vals = []
    for r in rows:
        if len(r) >= 2:
            try:
                vals.append(float(str(r[1]).replace(",", ".")))
            except Exception:
                vals.append(0)
    with st.container(border=True):
        st.markdown(
            f"""<div class="pp-card-title">🔬 CARACTERIZACIÓN MINERALÓGICA</div>
              <div class="pp-sub">{tec} &nbsp; {badge(est, MEST_MAP)}</div>
              <div style="display:flex;gap:8px;margin-top:10px">
                <div class='kpi-box' style='flex:1'><div class='kpi-label'>Técnica</div><div class='kpi-value' style='font-size:15px'>{tec}</div></div>
                <div class='kpi-box' style='flex:1'><div class='kpi-label'>P80</div><div class='kpi-value'>{nf(p80)} µm</div></div>
                <div class='kpi-box' style='flex:1'><div class='kpi-label'>Grado liberación</div><div class='kpi-value'>{nf(lib)}%</div></div>
              </div>
              <div class="pp-sub" style="font-weight:700;margin-top:10px">MINERALOGÍA MODAL (%)</div>""",
            unsafe_allow_html=True)
        if vals:
            cols = (DONUT_PAL * 3)[:len(vals)]
            st.plotly_chart(donut_chart(vals, labels, cols, 200),
                            width='stretch', config=CHART_CFG, key=f"min_{wp}")


def _ind_one(icon, label, val):
    return (f"<div class='ind-item' style='flex:1'><div style='font-size:19px'>{icon}</div>"
            f"<div class='ind-val'>{val}</div><div class='ind-lbl'>{label}</div></div>")


def _mp_cell(wp, n):
    g = st.session_state
    if not g.get(f'ind{wp}_mp{n}_on', False):
        return ""
    name = g[f'ind{wp}_mp{n}_name']; val = g[f'ind{wp}_mp{n}_val']
    bg = PASTEL_HEX.get(g.get(f'ind{wp}_mp{n}_color', "Gris"), "#E6E9ED")
    return (f"<div style='flex:1 1 90px;min-width:90px;box-sizing:border-box;"
            f"border:1px solid #C7D0DA;background:{bg};padding:5px 4px;text-align:center'>"
            f"<div style='font-size:12px;font-weight:800;color:{NAVY};line-height:1.15'>{name}</div>"
            f"<div style='font-weight:800;color:{TEXT};font-size:14px'>{nf(val)} kg</div></div>")


def render_indicadores(wp):
    g = st.session_state
    kpis = (_ind_one("⚙️", "Disponibilidad equipos", f"{nf(g[f'ind{wp}_disp'])}%")
            + _ind_one("⏱️", "Tiempo total operación", f"{nf(g[f'ind{wp}_top'])} d")
            + _ind_one("🔧", "Mantención (días)", nf(g[f'ind{wp}_mant']))
            + _ind_one("💧", "Consumo agua", f"{nf(g[f'ind{wp}_agua'],1)} m³/h")
            + _ind_one("⚡", "Consumo energía", f"{nf(g[f'ind{wp}_energia'])} kWh/h")
            + _ind_one("🛡️", "Seguridad: incidentes", nf(g[f'ind{wp}_seg'])))
    cells = [c for c in (_mp_cell(wp, n) for n in range(15)) if c]
    mp = "".join(cells) or f"<div style='color:{MUTED};font-size:13px'>Sin materias primas activas.</div>"
    with st.container(border=True, key=f"wp{wp}_ind"):
        st.markdown(
            f"""<div class="det-hd">INDICADORES OPERACIONALES (WP{wp})</div>
            <div style="display:flex;gap:10px;flex-wrap:wrap">{kpis}</div>
            <div style="font-weight:700;color:{NAVY};font-size:13px;margin:12px 0 4px">Inventario de materias primas (kg)</div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;box-sizing:border-box">{mp}</div>""",
            unsafe_allow_html=True)


# ---------- Detalles específicos por WP ----------
def wp1_ops():
    """Operaciones de WP1 por posición: 3 de oxidación (0-2) + 2 de reducción (3-4)."""
    return ([("ox", i, OX_PROCS[i], OX_METRICS) for i in range(len(OX_PROCS))]
            + [("rd", i, RD_PROCS[i], RD_METRICS) for i in range(len(RD_PROCS))])


def detail_wp1():
    g = st.session_state
    with st.container(border=True, key="wp1_detail"):
        st.markdown(
            f"<div class='det-hd'>WP1 — OXIDACIÓN / REDUCCIÓN (DETALLE)</div>",
            unsafe_allow_html=True)
        ops = wp1_ops()
        order = proc_order("1")
        for r0 in range(0, len(order), 3):
            cols = st.columns(3, gap="medium")
            for j in range(3):
                if r0 + j >= len(order):
                    continue
                pos = order[r0 + j]
                grp, idx, nm, mets = ops[pos]
                with cols[j]:
                    with st.container(border=True, key=f"w1box_{pos}"):
                        render_subproc(grp, idx, nm, mets, per_op_feeds=True)
    with st.container(border=True, key="wp1_acc"):
        acts = [g[f'wp1_act_{i}'] for i in range(5)
                if not g.get(f'wp1_actvac_{i}', False) and str(g[f'wp1_act_{i}']).strip()]
        items = "".join(f"<li style='margin-bottom:3px'>{a}</li>" for a in acts) or \
            "<li style='color:#888'>—</li>"
        st.markdown(
            f"<div class='det-hd'>ACCIONES RECOMENDADAS</div>"
            f"<ul style='margin:0 0 0 2px;padding-left:18px;font-size:14px;color:{TEXT}'>{items}</ul>",
            unsafe_allow_html=True)


def detail_wp2():
    g = st.session_state
    with st.container(border=True, key="wp2_detail"):
        st.markdown(
            f"<div class='det-hd'>WP2 — SEPARACIÓN METALÚRGICA (DETALLE)</div>",
            unsafe_allow_html=True)
        order = proc_order("2")
        for r0 in range(0, len(order), 3):
            cols = st.columns(3, gap="medium")
            for j in range(3):
                if r0 + j >= len(order):
                    continue
                idx = order[r0 + j]
                with cols[j]:
                    with st.container(border=True, key=f"w2box_{idx}"):
                        render_subproc("s2", idx, W2_PROCS[idx], W2_METRICS, per_op_feeds=True)
    with st.container(border=True, key="wp2_acc"):
        acts = [g[f'wp2_act_{i}'] for i in range(5)
                if not g.get(f'wp2_actvac_{i}', False) and str(g[f'wp2_act_{i}']).strip()]
        items = "".join(f"<li style='margin-bottom:3px'>{a}</li>" for a in acts) or \
            "<li style='color:#888'>—</li>"
        st.markdown(
            f"<div class='det-hd'>ACCIONES RECOMENDADAS</div>"
            f"<ul style='margin:0 0 0 2px;padding-left:18px;font-size:14px;color:{TEXT}'>{items}</ul>",
            unsafe_allow_html=True)


def detail_wp3():
    g = st.session_state
    with st.container(border=True, key="wp3_detail"):
        st.markdown(
            f"<div class='det-hd'>WP3 — FIJACIÓN DE ARSÉNICO (DETALLE)</div>",
            unsafe_allow_html=True)
        cols = st.columns(3, gap="medium")
        for col_i, idx in enumerate(proc_order("3")):
            with cols[col_i % 3]:
                with st.container(border=True, key=f"w3box_{idx}"):
                    render_subproc("s3", idx, W3_PROCS[idx], W3_METRICS, per_op_feeds=True)
    with st.container(border=True, key="wp3_acc"):
        acts = [g[f'wp3_act_{i}'] for i in range(5)
                if not g.get(f'wp3_actvac_{i}', False) and str(g[f'wp3_act_{i}']).strip()]
        items = "".join(f"<li style='margin-bottom:3px'>{a}</li>" for a in acts) or \
            "<li style='color:#888'>—</li>"
        st.markdown(
            f"<div class='det-hd'>ACCIONES RECOMENDADAS</div>"
            f"<ul style='margin:0 0 0 2px;padding-left:18px;font-size:14px;color:{TEXT}'>{items}</ul>",
            unsafe_allow_html=True)


def render_ampliacion():
    g = st.session_state
    render_header()
    # Recolectar servicios activos y clasificarlos por estado
    servs = []
    for i in range(15):
        if g.get(f'amp_serv{i}_vac', False):
            continue
        nm = str(g.get(f'amp_serv{i}_name', '')).strip()
        if not nm:
            continue
        try:
            p = max(0, min(100, float(g.get(f'amp_serv{i}_prog', 0))))
        except (TypeError, ValueError):
            p = 0
        servs.append((nm, p, g.get(f'amp_serv{i}_desc', ''),
                      g.get(f'amp_serv{i}_resp', ''), g.get(f'amp_serv{i}_fecha', ''),
                      g.get(f'amp_serv{i}_estado', ''), g.get(f'amp_serv{i}_crit', '')))
    n_comp = sum(1 for _, p, *_ in servs if p >= 100)
    n_curso = sum(1 for _, p, *_ in servs if 0 < p < 100)
    n_ini = sum(1 for _, p, *_ in servs if p == 0)
    prom = round(sum(p for _, p, *_ in servs) / len(servs)) if servs else 0

    # Tarjeta resumen (mismo lenguaje visual que los WP)
    kpi = (
        f"<div class='kpi-box' style='flex:1'><div class='kpi-label'>Avance general</div>"
        f"<div class='kpi-value' style='color:{BLUE}'>{nf(g.get('amp_avance', 0))}%</div></div>"
        f"<div class='kpi-box' style='flex:1'><div class='kpi-label'>Servicios activos</div>"
        f"<div class='kpi-value'>{len(servs)}</div></div>"
        f"<div class='kpi-box' style='flex:1'><div class='kpi-label'>Completados</div>"
        f"<div class='kpi-value' style='color:{WP2}'>{n_comp}</div></div>"
        f"<div class='kpi-box' style='flex:1'><div class='kpi-label'>En curso</div>"
        f"<div class='kpi-value' style='color:{YELLOW}'>{n_curso}</div></div>"
        f"<div class='kpi-box' style='flex:1'><div class='kpi-label'>Por iniciar</div>"
        f"<div class='kpi-value' style='color:{MUTED}'>{n_ini}</div></div>"
        f"<div class='kpi-box' style='flex:1'><div class='kpi-label'>Avance medio servicios</div>"
        f"<div class='kpi-value'>{prom}%</div></div>")
    with st.container(border=True):
        st.markdown(
            f"<div class='det-hd'>📈 AMPLIACIÓN DE PLANTA — SERVICIOS Y CONTRATOS</div>"
            f"<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px'>{kpi}</div>"
            + status_bar("Avance general de la etapa", g.get('amp_avance', 0), BLUE),
            unsafe_allow_html=True)

    # Servicios agrupados por estado (más didáctico)
    GROUPS = [("✅ Completados", WP2, lambda p: p >= 100),
              ("🟡 En curso", YELLOW, lambda p: 0 < p < 100),
              ("⚪ Por iniciar", GRAY, lambda p: p == 0)]
    for title, col, cond in GROUPS:
        grp = [s for s in servs if cond(s[1])]
        if not grp:
            continue
        cards = ""
        for nm, p, ds, resp, fecha, estado, crit in grp:
            meta = ""
            if str(resp).strip():
                meta += f"<span>👤 {resp}</span>"
            if str(fecha).strip():
                meta += f"<span style='margin-left:10px'>📅 {fecha}</span>"
            meta_html = (f"<div style='font-size:12px;color:{TEXT};margin-top:5px'>{meta}</div>"
                         if meta else "")
            CRIT_COL = {"Alta": REDTXT, "Media": YELLOW, "Baja": WP2}
            tags = ""
            if str(estado).strip():
                tags += (f"<span style='font-size:11px;font-weight:700;color:{BLUE};"
                         f"background:#EAF1FB;border-radius:10px;padding:2px 8px'>{estado}</span>")
            if str(crit).strip():
                cc_ = CRIT_COL.get(crit, MUTED)
                tags += (f"<span style='font-size:11px;font-weight:700;color:{cc_};"
                         f"background:#F4F6F8;border-radius:10px;padding:2px 8px;margin-left:6px'>"
                         f"Criticidad {crit}</span>")
            tags_html = f"<div style='margin-top:6px'>{tags}</div>" if tags else ""
            cards += (
                f"<div style='flex:1 1 320px;min-width:280px;border:1px solid #E6ECF2;"
                f"border-left:4px solid {col};border-radius:8px;padding:10px 12px;background:#fff'>"
                f"<div style='font-weight:800;color:{NAVY};font-size:14px;margin-bottom:5px'>{nm}</div>"
                f"<div style='display:flex;align-items:center;gap:8px'>"
                f"<div class='pbar' style='flex:1'><div class='pfill' style='width:{p}%;background:{col}'></div></div>"
                f"<b style='color:{TEXT};font-size:14px'>{nf(p)}%</b></div>"
                f"{tags_html}{meta_html}"
                f"<div style='font-size:12px;color:{MUTED};margin-top:6px'>{ds or '—'}</div></div>")
        with st.container(border=True):
            st.markdown(
                f"<div class='pp-card-title'>{title} &nbsp;<span style='color:{MUTED};font-weight:600'>"
                f"({len(grp)})</span></div>"
                f"<div style='display:flex;flex-wrap:wrap;gap:10px;margin-top:8px'>{cards}</div>",
                unsafe_allow_html=True)
    if not servs:
        with st.container(border=True):
            st.markdown(f"<div style='color:{MUTED};font-size:14px'>Sin servicios activos. "
                        f"Agrégalos en Parámetros → 📈 Ampliación.</div>", unsafe_allow_html=True)


def render_general():
    g = st.session_state
    render_header()
    # ---- Parámetros operacionales (cajas KPI) + esquemas/logos ----
    pblocks = ""
    for i in range(12):
        if g.get(f'gen_op{i}_vac', False):
            continue
        nm = str(g.get(f'gen_op{i}_name', '')).strip()
        if not nm:
            continue
        vl = g.get(f'gen_op{i}_val', ''); un = g.get(f'gen_op{i}_unit', '')
        pblocks += (
            f"<div class='kpi-box' style='flex:1 1 160px;min-width:150px;text-align:center'>"
            f"<div class='kpi-label'>{nm}</div>"
            f"<div class='kpi-value'>{vl}{(' ' + un) if un else ''}</div></div>")
    if not pblocks:
        pblocks = f"<div style='color:{MUTED};font-size:14px'>Sin parámetros activos.</div>"
    logos = ""
    for j in range(4):
        if g.get(f'gen_logo{j}_vac', True):
            continue
        url = str(g.get(f'gen_logo{j}_url', '')).strip()
        if not url:
            continue
        cap = g.get(f'gen_logo{j}_caption', '')
        logos += (
            f"<div style='flex:0 0 auto;text-align:center;border:1px solid #E6ECF2;border-radius:8px;"
            f"padding:8px;background:#fff'>"
            f"<img src='{url}' style='max-height:120px;max-width:240px;object-fit:contain;display:block'/>"
            f"<div style='font-size:12px;color:{MUTED};margin-top:4px'>{cap}</div></div>")
    logos_html = (f"<div style='display:flex;flex-wrap:wrap;gap:10px;margin-top:10px;"
                  f"align-items:flex-start'>{logos}</div>") if logos else ""
    with st.container(border=True):
        st.markdown(
            f"<div class='det-hd'>📊 GENERAL — PARÁMETROS OPERACIONALES</div>"
            f"<div style='display:flex;flex-wrap:wrap;gap:8px;margin-top:8px'>{pblocks}</div>"
            f"{logos_html}",
            unsafe_allow_html=True)

    # ---- Insumos agrupados por tipo (nombre de tipo editable por insumo) ----
    CAT_COLORS = ["#8E6FC0", BLUE, WP1, "#2BA7C4", WP2, "#C0497E", "#0E7C86", MUTED]
    grupos = {}
    for i in range(15):
        if g.get(f'gen_ins{i}_vac', False):
            continue
        nm = str(g.get(f'gen_ins{i}_name', '')).strip()
        if not nm:
            continue
        tp = str(g.get(f'gen_ins{i}_type', '')).strip() or "Sin categoría"
        grupos.setdefault(tp, []).append(
            (nm, g.get(f'gen_ins{i}_mass', ''), g.get(f'gen_ins{i}_use', '')))
    blocks = ""
    for ci, (tp, items) in enumerate(grupos.items()):
        col = CAT_COLORS[ci % len(CAT_COLORS)]
        chips = ""
        for nm, ms, us in items:
            chips += (
                f"<div style='border:1px solid #E6ECF2;border-top:3px solid {col};border-radius:8px;"
                f"padding:9px 12px;background:#fff;flex:1 1 240px;min-width:220px'>"
                f"<div style='display:flex;justify-content:space-between;align-items:baseline;gap:8px'>"
                f"<span style='font-weight:800;color:{NAVY};font-size:14px'>{nm}</span>"
                f"<b style='color:{col};font-size:14px;white-space:nowrap'>{ms} kg</b></div>"
                f"<div style='font-size:12px;color:{MUTED};margin-top:4px'>{us or '—'}</div></div>")
        blocks += (
            f"<div style='margin-top:10px'>"
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px'>"
            f"<span class='dot' style='width:11px;height:11px;background:{col}'></span>"
            f"<span style='font-weight:800;color:{NAVY};font-size:14px'>{tp}</span>"
            f"<span style='color:{MUTED};font-size:13px'>({len(items)})</span></div>"
            f"<div style='display:flex;flex-wrap:wrap;gap:8px'>{chips}</div></div>")
    if not blocks:
        blocks = f"<div style='color:{MUTED};font-size:14px'>Sin insumos activos.</div>"
    with st.container(border=True):
        st.markdown(
            f"<div class='det-hd'>INSUMOS POR TIPO</div>{blocks}",
            unsafe_allow_html=True)


def render_wp_tab(wp, color, detail_fn, bar_color=None):
    render_header()
    render_summary(wp, color, bar_color)
    ca, cn = st.columns([1.35, 1], gap="small")
    with ca: render_avance(wp)
    with cn: render_niveles(wp)
    render_riesgos(wp)
    detail_fn()


# ============================================================
# NAVEGACIÓN POR PÁGINAS (solo renderiza la sección activa = mucho más rápido)
# ============================================================
PAGES = ["⚙️ Parámetros", "🟠 WP1 Oxidación/Reducción",
         "🟢 WP2 Separación metalúrgica", "🔴 WP3 Fijación de arsénico", "🛡️ Seguridad",
         "📈 Ampliación", "📊 General"]
page = st.radio("Sección", PAGES, horizontal=True, label_visibility="collapsed", key="_nav")

# ------------------------------------------------------------
# PÁGINA PARÁMETROS
# ------------------------------------------------------------
if page == PAGES[0]:
    st.markdown(
        f"<h3 style='color:{NAVY};margin:0 0 2px 0'>⚙️ Carga y modificación de parámetros</h3>"
        f"<p style='color:{MUTED};font-size:14px;margin:0 0 4px 0'>"
        "Editor central: todo lo que cambies aquí se refleja al instante en las pestañas WP1/WP2/WP3 y Seguridad. "
        "Esta pestaña siempre muestra el estado actual de todos los datos.</p>", unsafe_allow_html=True)

    if st.session_state.get("_msg"):
        st.success(st.session_state.pop("_msg"))

    cA, cB, cC = st.columns([1, 1, 1.4])
    cA.button("♻️ Restablecer valores", width='stretch', on_click=reset_defaults)
    cfg = {k: st.session_state[k] for k in DEFAULTS}
    cB.download_button("💾 Descargar TODO (JSON)",
        data=json.dumps(cfg, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="config_planta_piloto.json", mime="application/json", width='stretch')
    with cC:
        st.file_uploader("Cargar JSON (todo)", type="json", key="uploader", label_visibility="collapsed")
        st.button("📂 Aplicar archivo cargado (todo)", width='stretch', on_click=apply_upload)

    st.markdown(
        f"<div style='font-weight:800;color:{NAVY};font-size:14px;margin:14px 0 2px'>"
        f"CARGA / DESCARGA INDEPENDIENTE POR PESTAÑA</div>"
        f"<div style='color:{MUTED};font-size:13px;margin-bottom:6px'>"
        f"Cada pestaña tiene su propio archivo (4 en total). «Descargar» guarda solo los datos de esa "
        f"pestaña; «Aplicar» los carga desde un archivo. No afecta a las demás pestañas.</div>",
        unsafe_allow_html=True)
    sc = st.columns(4)
    for i, (sec, lbl, icon, fname) in enumerate(SECTION_META):
        with sc[i]:
            with st.container(border=True):
                st.markdown(f"<div style='font-weight:800;color:{NAVY};font-size:13px;"
                            f"margin:2px 0 12px 0;min-height:34px;line-height:1.25'>{icon} {lbl}</div>",
                            unsafe_allow_html=True)
                seccfg = {k: st.session_state[k] for k in SECTION_KEYS[sec]}
                st.download_button(
                    "💾 Descargar", key=f"dl_{sec}",
                    data=json.dumps(seccfg, ensure_ascii=False, indent=2).encode("utf-8"),
                    file_name=f"config_{fname}.json", mime="application/json", width='stretch')
                st.file_uploader("Cargar", type="json", key=f"up_{sec}", label_visibility="collapsed")
                st.button("📂 Aplicar", key=f"apply_{sec}", width='stretch',
                          on_click=apply_upload_section, args=(sec,))

    st.divider()

    with st.expander("🏷️ ENCABEZADO / ESTADO GLOBAL", expanded=True):
        c = st.columns(3)
        c[0].text_input("Título", key="hdr_title")
        c[1].text_input("Actualizado", key="hdr_updated")
        c[2].selectbox("Estado global", ["VERDE", "AMARILLO", "ROJO"], key="hdr_status")

    # ---- bloque editor por WP ----
    def wp_editor(wp, titulo):
        st.markdown(f"<div class='det-hd'>{titulo}</div>", unsafe_allow_html=True)
        procs = PROCS[wp]
        levels = WP_LEVELS[wp]
        SECS = ["📋 Resumen", "🎯 KPIs", "📊 Avance", "🚦 Niveles",
                "⚠️ Riesgos", "🔬 Detalle", "📝 Acciones"]
        st.caption("Elige una sección. Se construye solo esa (mucho más rápido).")
        sec = st.radio("Sección", SECS, horizontal=True,
                       label_visibility="collapsed", key=f"_sec_{wp}")

        if sec == "📋 Resumen":
            st.caption("Nombre, nivel y % de avance global")
            c = st.columns(3)
            c[0].text_input("Nombre", key=f"wp{wp}_name")
            c[1].text_input("Nivel", key=f"wp{wp}_level")
            c[2].number_input("Avance (%)", step=1, key=f"wp{wp}_progress")

        elif sec == "🎯 KPIs":
            st.caption("«Vacío (KPI)» oculta la fila · «Orden» define la posición · «Vacío» en una meta "
                       "deja esa celda en blanco; las columnas de meta sin uso no se muestran.")
            _metas = [("Meta 1", "ref", "m1vac"), ("Meta 2", "meta2", "m2vac"),
                      ("Meta 3", "meta3", "m3vac"), ("Meta 4", "meta4", "m4vac")]
            kpi_sel = st.selectbox("KPI a editar", [f"KPI {i}" for i in range(1, 19)],
                                   key=f"_kpi_{wp}")
            i = int(kpi_sel.split()[1]) if kpi_sel else 1
            hc = st.columns([3, 1.2, 1.2])
            hc[0].caption(f"KPI {i}")
            hc[1].number_input("Orden", min_value=1, max_value=18, step=1, key=f"wp{wp}_kpi{i}_ord")
            hc[2].checkbox("Vacío (KPI)", key=f"wp{wp}_kpi{i}_vac")
            cc = st.columns([1, 1.4, 2])
            cc[0].text_input("Operación unitaria", key=f"wp{wp}_kpi{i}_op",
                             label_visibility="collapsed", placeholder="Operación unitaria")
            cc[1].text_input("Descripción objetivo", key=f"wp{wp}_kpi{i}_name",
                             label_visibility="collapsed", placeholder="Descripción objetivo")
            cc[2].text_input("Descripción KPI", key=f"wp{wp}_kpi{i}_desc",
                             label_visibility="collapsed", placeholder="Descripción KPI")
            cc = st.columns(4)
            for j, (lbl, fld, vac) in enumerate(_metas):
                with cc[j]:
                    st.text_input(lbl, key=f"wp{wp}_kpi{i}_{fld}")
                    st.checkbox("Vacío", key=f"wp{wp}_kpi{i}_{vac}")
            cc = st.columns(2)
            cc[0].text_input("Resultado", key=f"wp{wp}_kpi{i}_val")
            cc[1].selectbox("Semáforo", SEM_OPTS, key=f"wp{wp}_kpi{i}_sem")

        elif sec == "📊 Avance":
            st.caption("Marca/desmarca «Requiere» por celda para dejarla vacía.")
            lvl_sel = st.selectbox("Nivel a editar", levels, key=f"_avlvl_{wp}")
            li = levels.index(lvl_sel) if lvl_sel in levels else 0
            for pi, proc in enumerate(procs):
                st.caption(proc)
                cc = st.columns([1.1, 1, 1, 1, 1])
                cc[0].checkbox("Requiere", key=f"w{wp}_req_{pi}_{li}")
                cc[1].number_input("Planif.", step=1, key=f"w{wp}av_{pi}_{li}_planif")
                cc[2].number_input("Ejec.", step=1, key=f"w{wp}av_{pi}_{li}_ejec")
                cc[3].number_input("Válidos", step=1, key=f"w{wp}av_{pi}_{li}_valid")
                cc[4].number_input("Pend.", step=1, key=f"w{wp}av_{pi}_{li}_pend")

        elif sec == "🚦 Niveles":
            st.caption("Desmarca «Req» para dejar la celda vacía.")
            for pi, proc in enumerate(procs):
                st.caption(proc)
                cc = st.columns(len(levels))
                for li, lvl in enumerate(levels):
                    with cc[li]:
                        st.selectbox(lvl, NIV_OPTS, key=f"w{wp}niv_{pi}_{li}")
                        st.checkbox("Req", key=f"w{wp}_nivreq_{pi}_{li}")

        elif sec == "⚠️ Riesgos":
            st.caption("Selecciona «—» como nivel para no mostrar la alerta.")
            for i in (1, 2, 3):
                r = st.columns([1, 4])
                r[0].selectbox(f"Nivel {i}", RISK_OPTS, key=f"wp{wp}_r{i}_level")
                r[1].text_input(f"Descripción {i}", key=f"wp{wp}_r{i}_desc")

        elif sec == "🔬 Detalle":
            if wp == "1":
                ops = ([("ox", i, f"OXIDACIÓN · {OX_PROCS[i]}", OX_METRICS) for i in range(len(OX_PROCS))]
                       + [("rd", i, f"REDUCCIÓN · {RD_PROCS[i]}", RD_METRICS) for i in range(len(RD_PROCS))])
            elif wp == "2":
                ops = [("s2", i, W2_PROCS[i], W2_METRICS) for i in range(len(W2_PROCS))]
            else:
                ops = [("s3", i, W3_PROCS[i], W3_METRICS) for i in range(len(W3_PROCS))]
            cc = st.columns(2)
            cc[0].checkbox("Muestras química como gráfico de torta", key="quim_pie")
            cc[1].checkbox("Muestras mineralógica como tortas (DRX/QEMSCAN)", key="min_pie")
            names = [o[2] for o in ops]
            op_sel = st.selectbox("Operación unitaria a editar", names, key=f"_detop_{wp}")
            pos = names.index(op_sel) if op_sel in names else 0
            o = ops[pos]
            st.number_input(
                "Orden de visualización de esta operación (para reposicionarla)",
                min_value=1, max_value=len(ops), step=1, key=f"wp{wp}_proc{pos}_ord")
            subproc_editor(o[0], o[1], o[2], o[3])

        elif sec == "📝 Acciones":
            st.caption("Hasta 5 · marca «Vacío» para ocultar una acción.")
            for i in range(5):
                cc = st.columns([6, 1])
                cc[0].text_input(f"Acción {i + 1}", key=f"wp{wp}_act_{i}",
                                 label_visibility="collapsed", placeholder=f"Acción {i + 1}")
                cc[1].checkbox("Vacío", key=f"wp{wp}_actvac_{i}")

    st.markdown(
        f"<div style='font-weight:800;color:{NAVY};font-size:14px;margin:8px 0 2px'>"
        f"EDITOR DE PARÁMETROS</div>"
        f"<div style='color:{MUTED};font-size:13px;margin-bottom:4px'>"
        f"Elige el work package a editar. Se construyen solo sus campos (más rápido).</div>",
        unsafe_allow_html=True)
    edit_wp = st.radio("Editar WP",
                       ["🟠 WP1", "🟢 WP2", "🔴 WP3", "🛡️ Seguridad", "📈 Ampliación", "📊 General"],
                       horizontal=True, label_visibility="collapsed", key="_editwp")
    if edit_wp == "🟠 WP1":
        wp_editor("1", "🟠 WP1 — OXIDACIÓN / REDUCCIÓN")
    elif edit_wp == "🟢 WP2":
        wp_editor("2", "🟢 WP2 — SEPARACIÓN METALÚRGICA")
    elif edit_wp == "🔴 WP3":
        wp_editor("3", "🔴 WP3 — FIJACIÓN DE ARSÉNICO")
    elif edit_wp == "📈 Ampliación":
        st.markdown(f"<div class='det-hd'>📈 AMPLIACIÓN — SERVICIOS Y CONTRATOS</div>",
                    unsafe_allow_html=True)
        st.number_input("Avance general de la etapa (%)", min_value=0, max_value=100, step=1,
                        key="amp_avance")
        st.caption("15 servicios · «Vacío» oculta el servicio (los visibles se reacomodan). "
                   "Nombre, % avance, responsable, fecha, estado contractual, criticidad y descripción.")
        for i in range(15):
            cc = st.columns([2.4, 0.9, 1.8, 1.4, 1])
            cc[0].text_input(f"Servicio {i + 1}", key=f"amp_serv{i}_name",
                             label_visibility="collapsed", placeholder=f"Servicio {i + 1}")
            cc[1].number_input("%", min_value=0, max_value=100, step=1, key=f"amp_serv{i}_prog",
                               label_visibility="collapsed")
            cc[2].text_input("Responsable", key=f"amp_serv{i}_resp",
                             label_visibility="collapsed", placeholder="Responsable / empresa")
            cc[3].text_input("Fecha", key=f"amp_serv{i}_fecha",
                             label_visibility="collapsed", placeholder="Fecha objetivo")
            cc[4].checkbox("Vacío", key=f"amp_serv{i}_vac")
            cc = st.columns([2, 1.6, 5])
            cc[0].selectbox("Estado", AMP_ESTADOS, key=f"amp_serv{i}_estado",
                            label_visibility="collapsed")
            cc[1].selectbox("Criticidad", AMP_CRIT, key=f"amp_serv{i}_crit",
                            label_visibility="collapsed")
            cc[2].text_input("Descripción", key=f"amp_serv{i}_desc",
                             label_visibility="collapsed", placeholder="Breve descripción del servicio")
    elif edit_wp == "📊 General":
        st.markdown(f"<div class='det-hd'>📊 GENERAL — PARÁMETROS OPERACIONALES E INSUMOS</div>",
                    unsafe_allow_html=True)
        st.caption("Parámetros operacionales (nombre · valor · unidad) · «Vacío» oculta y reacomoda.")
        for i in range(12):
            cc = st.columns([3, 2, 1.5, 1])
            cc[0].text_input(f"Parámetro {i + 1}", key=f"gen_op{i}_name",
                             label_visibility="collapsed", placeholder=f"Parámetro {i + 1}")
            cc[1].text_input("Valor", key=f"gen_op{i}_val",
                             label_visibility="collapsed", placeholder="Valor")
            cc[2].text_input("Unidad", key=f"gen_op{i}_unit",
                             label_visibility="collapsed", placeholder="Unidad")
            cc[3].checkbox("Vacío", key=f"gen_op{i}_vac")
        st.caption("Esquemas / logos (pega la URL de una imagen) · «Vacío» lo oculta.")
        for j in range(4):
            cc = st.columns([4, 3, 1])
            cc[0].text_input(f"URL imagen {j + 1}", key=f"gen_logo{j}_url",
                             label_visibility="collapsed", placeholder="https://… (logo o esquema)")
            cc[1].text_input("Leyenda", key=f"gen_logo{j}_caption",
                             label_visibility="collapsed", placeholder="Leyenda")
            cc[2].checkbox("Vacío", key=f"gen_logo{j}_vac")
        st.caption("Nombres de las categorías sugeridas (referencia para escribir el tipo).")
        st.caption("Sugerencias: " + " · ".join(_INS_TYPES))
        st.caption("Insumos (nombre · masa kg · tipo · uso) · «Vacío» oculta y reacomoda. "
                   "El «tipo» es un nombre editable; los insumos se agrupan por ese nombre.")
        for i in range(15):
            cc = st.columns([2.6, 1.3, 2, 3, 1])
            cc[0].text_input(f"Insumo {i + 1}", key=f"gen_ins{i}_name",
                             label_visibility="collapsed", placeholder=f"Insumo {i + 1}")
            cc[1].text_input("Masa kg", key=f"gen_ins{i}_mass",
                             label_visibility="collapsed", placeholder="Masa (kg)")
            cc[2].text_input("Tipo", key=f"gen_ins{i}_type",
                             label_visibility="collapsed", placeholder="Tipo / categoría")
            cc[3].text_input("Uso", key=f"gen_ins{i}_use",
                             label_visibility="collapsed", placeholder="Uso en operación")
            cc[4].checkbox("Vacío", key=f"gen_ins{i}_vac")
    elif edit_wp == "🛡️ Seguridad":
        st.markdown(
            f"<div style='font-weight:800;color:{NAVY};font-size:15px;margin:6px 0 2px'>"
            f"🛡️ SEGURIDAD / HSE</div>", unsafe_allow_html=True)
        with st.expander("📊 Indicadores HSE", expanded=True):
            st.caption("Marca «Vacío» para ocultar una variable; las visibles se autoajustan en una fila.")
            _hse = [("Días sin incidentes", "s_dias_sin", "s_dias_sin_vac", False),
                    ("Incidentes", "s_inc_mes", "s_inc_vac", False),
                    ("Días sin accidentes", "s_acc_dias_sin", "s_acc_dias_sin_vac", False),
                    ("Accidentes", "s_acc_camp", "s_acc_vac", False),
                    ("Acc. con tiempo perdido", "s_acc_ctp", "s_acc_ctp_vac", False),
                    ("Capacitación (%)", "s_capacit", "s_capacit_vac", False),
                    ("Cumplimiento EPP (%)", "s_epp", "s_epp_vac", False)]
            for r0 in range(0, len(_hse), 5):
                cc = st.columns(5)
                for j in range(5):
                    if r0 + j >= len(_hse):
                        continue
                    lbl, key, vack, isf = _hse[r0 + j]
                    with cc[j]:
                        st.number_input(lbl, step=(0.1 if isf else 1),
                                        format=("%.1f" if isf else None), key=key)
                        st.checkbox("Vacío", key=vack)
            st.caption("Próxima capacitación")
            cc = st.columns([3, 2])
            cc[0].text_input("Nombre de la próxima capacitación", key="s_next_cap")
            cc[1].text_input("Fecha", key="s_next_cap_date")
        with st.expander("📋 Registro de incidentes y accidentes", expanded=False):
            st.text_area("Incidentes (Fecha;Tipo;Área;Severidad;Estado)",
                         key="s_inc_log", height=120)
            st.text_area("Accidentes (Fecha;Tipo;Descripción;Área;Estado)",
                         key="s_acc_log", height=100,
                         help="Usa «—» en los campos si no hay accidentes que registrar.")
        with st.expander("🎓 Registro de capacitaciones", expanded=False):
            st.text_area("Capacitaciones (Fecha;Tema;Área;Asistentes;Estado)",
                         key="s_cap_log", height=130,
                         help="Estado: Realizada · Programada · Pendiente · Cancelada")
        with st.expander("🟢 Estado de incidentes (gráfico)", expanded=False):
            st.caption("Cantidad de incidentes por estado de avance (gráfico de torta).")
            c = st.columns(4)
            c[0].number_input("No iniciado", step=1, key="s_est_noini")
            c[1].number_input("En desarrollo", step=1, key="s_est_des")
            c[2].number_input("En revisión", step=1, key="s_est_rev")
            c[3].number_input("Aprobado", step=1, key="s_est_apr")
        with st.expander("🔧 Seguimiento de acciones correctivas", expanded=False):
            c = st.columns(4)
            c[0].number_input("Acciones totales", step=1, key="s_acc_total")
            c[1].number_input("Cerradas", step=1, key="s_acc_cerradas")
            c[2].number_input("Abiertas", step=1, key="s_acc_abiertas")
            c[3].number_input("Vencidas", step=1, key="s_acc_vencidas")
        with st.expander("📑 Estado MIPER", expanded=False):
            c = st.columns(3)
            c[0].number_input("% Actualización", step=1, key="miper_actualiz")
            c[1].number_input("Total peligros identificados", step=1, key="miper_peligros")
            c[2].selectbox("Estado MIPER", MIPER_OPTS, key="miper_estado")
            st.caption("Cantidad de peligros por nivel de riesgo (el % respecto del total se calcula solo).")
            c = st.columns(3)
            c[0].number_input("Riesgos bajos (cantidad)", step=1, key="miper_bajos")
            c[1].number_input("Riesgos medios (cantidad)", step=1, key="miper_medios")
            c[2].number_input("Riesgos críticos (cantidad)", step=1, key="miper_criticos")
            c = st.columns(2)
            c[0].text_input("Última revisión", key="miper_revision")
            c[1].text_input("Próxima revisión", key="miper_proxima")
        with st.expander("⚠️ Acciones / alertas de seguridad", expanded=False):
            for i in (1, 2, 3):
                cc = st.columns([1, 4])
                cc[0].selectbox(f"Nivel {i}", ["—", "Alta", "Media", "Baja"],
                                key=f"s_alert{i}_level")
                cc[1].text_input(f"Descripción {i}", key=f"s_alert{i}_desc")

# ------------------------------------------------------------
# PESTAÑAS WP
# ------------------------------------------------------------
elif page == PAGES[1]:
    try:
        render_wp_tab("1", WP1, detail_wp1, bar_color=NAVY)
    except Exception as e:
        st.error(f"Error al renderizar WP1: {type(e).__name__}: {e}")
elif page == PAGES[2]:
    try:
        render_wp_tab("2", WP2, detail_wp2, bar_color=NAVY)
    except Exception as e:
        st.error(f"Error al renderizar WP2: {type(e).__name__}: {e}")
elif page == PAGES[3]:
    try:
        render_wp_tab("3", WP3, detail_wp3, bar_color=NAVY)
    except Exception as e:
        st.error(f"Error al renderizar WP3: {type(e).__name__}: {e}")

# ------------------------------------------------------------
# PESTAÑA SEGURIDAD
# ------------------------------------------------------------
elif page == PAGES[4]:
    g = st.session_state
    render_header()

    # KPIs HSE — una sola fila autoajustable, con casilla «vacío» por variable
    kpis = [("Días sin incidentes", nf(g['s_dias_sin']), WP2, "s_dias_sin_vac"),
            ("Incidentes", nf(g['s_inc_mes']), REDTXT if g['s_inc_mes'] else TEXT, "s_inc_vac"),
            ("Días sin accidentes", nf(g['s_acc_dias_sin']), WP2, "s_acc_dias_sin_vac"),
            ("Accidentes", nf(g['s_acc_camp']), REDTXT if g['s_acc_camp'] else TEXT, "s_acc_vac"),
            ("Acc. c/tiempo perdido", nf(g['s_acc_ctp']), REDTXT if g['s_acc_ctp'] else TEXT, "s_acc_ctp_vac"),
            ("Capacitación", f"{nf(g['s_capacit'])}%", WP2, "s_capacit_vac"),
            ("Cumplimiento EPP", f"{nf(g['s_epp'])}%", WP2, "s_epp_vac")]
    blocks = "".join(
        f"<div class='kpi-box' style='flex:1 1 0;min-width:0;text-align:center'>"
        f"<div class='kpi-label'>{l}</div>"
        f"<div class='kpi-value' style='color:{cc}'>{v}</div></div>"
        for l, v, cc, vk in kpis if not g.get(vk, False))
    # Próxima capacitación (nombre + fecha)
    nxt = str(g.get('s_next_cap', '')).strip()
    if nxt:
        blocks += (
            f"<div class='kpi-box' style='flex:1.4 1 0;min-width:0;text-align:center'>"
            f"<div class='kpi-label'>Próxima capacitación</div>"
            f"<div class='kpi-value' style='color:{BLUE};font-size:14px'>{nxt}</div>"
            f"<div style='font-size:11px;color:{MUTED}'>{g.get('s_next_cap_date', '')}</div></div>")
    st.markdown(f"<div class='pp-card'><div class='pp-card-title'>🛡️ INDICADORES DE SEGURIDAD (HSE)</div>"
                f"<div style='display:flex;gap:6px;margin-top:8px;flex-wrap:nowrap'>{blocks}</div></div>",
                unsafe_allow_html=True)

    cL, cR = st.columns([1.4, 1])

    # ---- Columna izquierda: Incidentes y accidentes + Capacitaciones ----
    with cL:
        rows = parse_table(g['s_inc_log'])
        body = ""
        for r in rows:
            r = (r + ["", "", "", "", ""])[:5]
            fecha, tipo, area, sev, est = r
            body += (f"<tr><td>{fecha}</td><td>{tipo}</td><td>{area}</td>"
                     f"<td>{badge(sev, SEV_MAP)}</td><td>{badge(est, INCEST_MAP)}</td></tr>")
        arows_t = parse_table(g['s_acc_log'])
        abody = ""
        for r in arows_t:
            r = (r + ["", "", "", "", ""])[:5]
            fecha, tipo, desc, area, est = r
            abody += (f"<tr><td>{fecha}</td><td>{tipo}</td><td>{desc}</td><td>{area}</td>"
                      f"<td>{badge(est, INCEST_MAP)}</td></tr>")
        with st.container(border=True):
            st.markdown(
                f"<div class='pp-card-title'>📋 REGISTRO Y SEGUIMIENTO DE INCIDENTES Y ACCIDENTES</div>"
                f"<div class='pp-sub' style='font-weight:700;margin-top:8px'>Incidentes</div>"
                f"<table class='tbl'><tr><th>Fecha</th><th>Tipo</th><th>Área</th>"
                f"<th>Severidad</th><th>Estado</th></tr>{body}</table>"
                f"<div class='pp-sub' style='font-weight:700;margin-top:12px'>Accidentes</div>"
                f"<table class='tbl'><tr><th>Fecha</th><th>Tipo</th><th>Descripción</th>"
                f"<th>Área</th><th>Estado</th></tr>{abody}</table>", unsafe_allow_html=True)
        crows = parse_table(g['s_cap_log'])
        cbody = ""
        for r in crows:
            r = (r + ["", "", "", "", ""])[:5]
            fecha, tema, area, asis, est = r
            cbody += (f"<tr><td>{fecha}</td><td>{tema}</td><td>{area}</td>"
                      f"<td style='text-align:center'>{asis}</td><td>{badge(est, CAP_MAP)}</td></tr>")
        with st.container(border=True):
            st.markdown(f"<div class='pp-card-title'>🎓 REGISTRO DE CAPACITACIONES</div>"
                        f"<table class='tbl'><tr><th>Fecha</th><th>Tema</th><th>Área</th>"
                        f"<th>Asist.</th><th>Estado</th></tr>{cbody}</table>", unsafe_allow_html=True)

    # ---- Columna derecha: Estado de incidentes y accidentes + Acciones correctivas ----
    with cR:
        with st.container(border=True):
            st.markdown("<div class='pp-card-title'>ESTADO DE INCIDENTES Y ACCIDENTES</div>",
                        unsafe_allow_html=True)
            labs = [l for l, _, _ in INCPIE]
            vals = [g.get(k, 0) for _, k, _ in INCPIE]
            cols = [c for _, _, c in INCPIE]
            if sum(vals) > 0:
                fig = go.Figure(go.Pie(values=vals, labels=labs, hole=0.55,
                    marker=dict(colors=cols, line=dict(color="#fff", width=2)),
                    texttemplate="<b>%{percent:.0%}</b>", textposition="inside",
                    insidetextfont=dict(color="#000", size=13), sort=False))
                fig.update_layout(height=185, margin=dict(l=4, r=4, t=4, b=4),
                    paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig, width='stretch', config=CHART_CFG, key="seg_est")
            else:
                st.markdown(f"<div style='color:{MUTED};font-size:13px;margin-top:6px'>"
                            f"Sin datos de estado.</div>", unsafe_allow_html=True)
            legend = "".join(
                f"<div style='display:flex;align-items:center;gap:6px;margin:3px 0'>"
                f"<span class='dot' style='width:11px;height:11px;background:{c}'></span>"
                f"<span style='flex:1;font-size:13px;color:{TEXT}'>{l}</span>"
                f"<b style='font-size:13px;color:{TEXT}'>{g.get(k, 0)}</b></div>"
                for l, k, c in INCPIE)
            st.markdown(f"<div style='margin-top:6px'>{legend}</div>", unsafe_allow_html=True)
        tot = g['s_acc_total']; cer = g['s_acc_cerradas']; ab = g['s_acc_abiertas']; ven = g['s_acc_vencidas']
        pct = round(100 * cer / tot) if tot else 0
        with st.container(border=True):
            st.markdown(
                f"""<div class='pp-card-title'>🔧 SEGUIMIENTO DE ACCIONES CORRECTIVAS</div>
                  <div style="display:flex;gap:8px;margin-top:10px">
                    <div class='kpi-box' style='flex:1'><div class='kpi-label'>Totales</div><div class='kpi-value'>{tot}</div></div>
                    <div class='kpi-box' style='flex:1'><div class='kpi-label'>Cerradas</div><div class='kpi-value' style='color:{WP2}'>{cer}</div></div>
                    <div class='kpi-box' style='flex:1'><div class='kpi-label'>Abiertas</div><div class='kpi-value'>{ab}</div></div>
                    <div class='kpi-box' style='flex:1'><div class='kpi-label'>Vencidas</div><div class='kpi-value' style='color:{REDTXT}'>{ven}</div></div>
                  </div>
                  <div class='pp-sub' style='font-weight:700;margin-top:10px'>% CIERRE DE ACCIONES</div>
                  <div style="display:flex;align-items:center;gap:8px">
                    <div class="pbar" style="flex:1"><div class="pfill" style="width:{pct}%;background:{WP2}"></div></div>
                    <b>{pct}%</b></div>""",
                unsafe_allow_html=True)

    # ---- MIPER (ancho completo, compacto) ----
    _tot = g['miper_peligros']
    def _rp(v):
        try:
            return pct1(100 * float(v) / float(_tot)) if float(_tot) else "—"
        except (TypeError, ValueError, ZeroDivisionError):
            return "—"
    risk = [("Bajos", g['miper_bajos'], WP2), ("Medios", g['miper_medios'], YELLOW),
            ("Críticos", g['miper_criticos'], WP3)]
    rblocks = "".join(
        f"<div class='kpi-box' style='flex:1'><div class='kpi-label'>Riesgos {l.lower()}</div>"
        f"<div class='kpi-value' style='color:{c}'>{_rp(v)}</div></div>" for l, v, c in risk)
    with st.container(border=True):
        st.markdown(
            f"""<div class='pp-card-title'>📑 ESTADO MIPER &nbsp; {badge(g['miper_estado'], MIPER_MAP)}</div>
              <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:nowrap;align-items:stretch">
                <div class='kpi-box' style='flex:1'><div class='kpi-label'>Actualización</div><div class='kpi-value'>{nf(g['miper_actualiz'])}%</div></div>
                <div class='kpi-box' style='flex:1'><div class='kpi-label'>Total peligros</div><div class='kpi-value'>{g['miper_peligros']}</div></div>
                {rblocks}
                <div class='kpi-box' style='flex:1.2'><div class='kpi-label'>Revisión</div>
                  <div style='font-size:13px;color:{TEXT};font-weight:700'>Últ: {g['miper_revision']}</div>
                  <div style='font-size:13px;color:{TEXT};font-weight:700'>Próx: {g['miper_proxima']}</div></div>
              </div>""",
            unsafe_allow_html=True)

    # ---- Acciones / alertas de seguridad ----
    icon = {"Alta": "❗", "Media": "⚠️", "Baja": "ℹ️"}
    arows = ""
    for i in (1, 2, 3):
        lvl = g[f's_alert{i}_level']; desc = g[f's_alert{i}_desc']
        if lvl == "—" or not str(desc).strip():
            continue
        bg, fg = RISK_STYLE[lvl]
        arows += (f"<div style='display:flex;align-items:center;gap:8px;margin:9px 0'>"
                  f"<span class='pp-badge' style='background:{bg};color:{fg};font-size:12px;padding:4px 10px'>{lvl}</span>"
                  f"<span style='flex:1;font-size:13.5px;color:{TEXT}'>{desc}</span>"
                  f"<span>{icon[lvl]}</span></div>")
    if not arows:
        arows = f"<div style='color:{WP2};font-size:14px;margin-top:8px'>✅ Sin alertas activas</div>"
    with st.container(border=True):
        st.markdown(f"<div class='pp-card-title'>ACCIONES / ALERTAS</div>"
                    f"<div style='margin-top:4px'>{arows}</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# PESTAÑA AMPLIACIÓN
# ------------------------------------------------------------
elif page == PAGES[5]:
    try:
        render_ampliacion()
    except Exception as e:
        st.error(f"Error al renderizar Ampliación: {type(e).__name__}: {e}")

# ------------------------------------------------------------
# PESTAÑA GENERAL
# ------------------------------------------------------------
elif page == PAGES[6]:
    try:
        render_general()
    except Exception as e:
        st.error(f"Error al renderizar General: {type(e).__name__}: {e}")