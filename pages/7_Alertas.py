# pages/2_Alertas.py
import streamlit as st
import pandas as pd
import numpy as np

st.title("Alertas en Tiempo Real")

# --- Cargar CSVs ---
csv_files = ["s1.csv", "s2.csv"]
dfs = []
for f in csv_files:
    try:
        dfs.append(pd.read_csv(f))
    except:
        pass

if not dfs:
    st.error("No hay datos disponibles para mostrar.")
    st.stop()

df = pd.concat(dfs, ignore_index=True)

# Normalizar columnas (mismo código del Resumen)
def normalize_cols(cols):
    cols = [c.strip().replace("%", "percent").replace(" ", "_").replace("-", "_").lower() for c in cols]
    return cols

df.columns = normalize_cols(df.columns)

# Mapeo flexible de columnas
col_map_candidates = {
    "cpu_percent": ["cpu_percent", "cpu", "cpu_usage", "cpu_percentage", "cpu%"],
    "memory_percent": ["memory_percent", "memory", "mem_percent", "mem", "memory_usage", "memory%"],
    "disk_percent": ["disk_percent", "disk", "disk_usage", "disk_percent_used", "disk%"]
}

def find_column(choices, cols):
    for c in choices:
        c_norm = c.strip().replace("%", "percent").replace(" ", "_").replace("-", "_").lower()
        if c_norm in cols:
            return c_norm
    return None

mapping = {}
for std, cand in col_map_candidates.items():
    found = find_column(cand, df.columns)
    if found:
        mapping[std] = found

# Asegurar columnas estándar
for std in ["cpu_percent", "memory_percent", "disk_percent"]:
    if std not in df.columns and std in mapping:
        df[std] = df[mapping[std]]

# Host y timestamp
if "host" not in df.columns:
    host_alt = find_column(["host", "hostname", "server"], df.columns)
    df["host"] = df[host_alt]

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="ignore")

# Ordenar por tiempo
df = df.sort_values("timestamp")

# Obtener último registro por host
latest = df.groupby("host", as_index=False).tail(1)

# Umbrales
WARN = 70
CRIT = 90

# Detectar alertas
alertas = latest[
    (latest["cpu_percent"] >= WARN) |
    (latest["memory_percent"] >= WARN) |
    (latest["disk_percent"] >= WARN)
]

st.write(f"Alertas detectadas: **{len(alertas)}**")

if alertas.empty:
    st.success("Todo en verde. No hay alertas por ahora. 🟢")
    st.stop()

# Selector de severidad
sev = st.radio(
    "Mostrar:",
    ["Todas", "Críticas", "Advertencias"]
)

if sev == "Críticas":
    alertas = alertas[
        (alertas["cpu_percent"] >= CRIT) |
        (alertas["memory_percent"] >= CRIT) |
        (alertas["disk_percent"] >= CRIT)
    ]

elif sev == "Advertencias":
    alertas = alertas[
        ((alertas["cpu_percent"] >= WARN) & (alertas["cpu_percent"] < CRIT)) |
        ((alertas["memory_percent"] >= WARN) & (alertas["memory_percent"] < CRIT)) |
        ((alertas["disk_percent"] >= WARN) & (alertas["disk_percent"] < CRIT))
    ]

# Ordenar
sort_col = st.selectbox(
    "Ordenar por:",
    ["cpu_percent", "memory_percent", "disk_percent"]
)

alertas = alertas.sort_values(sort_col, ascending=False)

# Mostrar tabla
st.dataframe(
    alertas[
        ["host", "timestamp", "cpu_percent", "memory_percent", "disk_percent"]
    ]
)

# Gráfica opcional
host_sel = st.selectbox("Ver histórico de:", alertas["host"].unique())

hist = df[df["host"] == host_sel].tail(50).set_index("timestamp")

st.line_chart(hist[["cpu_percent", "memory_percent", "disk_percent"]])
