# pages/1_Resumen.py
import streamlit as st
import pandas as pd
import numpy as np

st.title("Resumen")

# --- Cargar CSVs ---
csv_files = ["s1.csv", "s2.csv"]
dfs = []
for f in csv_files:
    try:
        dfs.append(pd.read_csv(f))
    except FileNotFoundError:
        st.error(f"Archivo no encontrado: {f}")
        st.stop()
    except Exception as e:
        st.error(f"Error leyendo {f}: {e}")
        st.stop()

df = pd.concat(dfs, ignore_index=True)

# --- Normalizar nombres de columna ---
def normalize_cols(cols):
    cols = [c.strip() for c in cols]
    cols = [c.replace("%", "percent") for c in cols]
    cols = [c.replace(" ", "_") for c in cols]
    cols = [c.replace("-", "_") for c in cols]
    cols = [c.lower() for c in cols]
    return cols

df.columns = normalize_cols(df.columns)

# --- Intentar mapear nombres comunes a nuestros estándares ---
# Estándares que usaremos en el resto del código:
# cpu -> cpu_percent
# memory -> memory_percent
# disk -> disk_percent

col_map_candidates = {
    "cpu_percent": ["cpu_percent", "cpu", "cpu_usage", "cpu_percentage", "cpu%"],
    "memory_percent": ["memory_percent", "memory", "mem_percent", "mem", "memory_usage", "memory%"],
    "disk_percent": ["disk_percent", "disk", "disk_usage", "disk_percent_used", "disk%"]
}

# función para encontrar la primera columna existente entre candidatos
def find_column(candidates, cols):
    for c in candidates:
        c_norm = c.strip().lower().replace("%", "percent").replace(" ", "_").replace("-", "_")
        if c_norm in cols:
            return c_norm
    return None

# construir mapping final (estándar -> existente en df)
mapping = {}
for std, cand in col_map_candidates.items():
    found = find_column(cand, df.columns)
    if found:
        mapping[std] = found

# Si alguna columna crítica falta, mostramos las columnas actuales y un mensaje
required = ["cpu_percent", "memory_percent", "disk_percent", "host", "timestamp"]
missing = [r for r in required if r not in mapping and r not in df.columns]

if missing:
    st.error("Faltan columnas críticas para el resumen.")
    st.write("Columnas esperadas (ejemplos):", required)
    st.write("Columnas encontradas en tus CSVs:")
    st.dataframe(pd.DataFrame({"columns": df.columns}))
    st.stop()

# --- Asegurar acceso con nombres estándar: crear columnas alias si es necesario ---
# si ya existen con el nombre estándar no hacemos nada; si no, creamos un alias desde mapping
for std in ["cpu_percent", "memory_percent", "disk_percent"]:
    if std not in df.columns:
        df[std] = df[mapping[std]]

# normalizar host y timestamp
if "host" not in df.columns:
    # intentar encontrar alternativas
    host_alt = find_column(["host", "hostname", "server"], df.columns)
    if host_alt:
        df["host"] = df[host_alt]
    else:
        st.error("No se encontró columna 'host' o equivalente.")
        st.stop()

if "timestamp" not in df.columns:
    ts_alt = find_column(["timestamp", "time", "date"], df.columns)
    if ts_alt:
        df["timestamp"] = df[ts_alt]
    else:
        st.warning("No se encontró columna 'timestamp'. Se usará el orden actual de registros.")
        # crear timestamp ficticio incremental
        df["timestamp"] = pd.date_range(end=pd.Timestamp.now(), periods=len(df))

# intentar convertir timestamp a datetime para ordenar
try:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
except Exception:
    # si falla, dejar como está y ordenar por índice
    pass

# --- Obtener último registro por host ---
latest = df.sort_values("timestamp").groupby("host", as_index=False).tail(1)

# --- Función semáforo ---
def status_color(value, warn=70, crit=90):
    try:
        v = float(value)
    except:
        return "🟢"
    if v >= crit:
        return "🔴"
    if v >= warn:
        return "🟡"
    return "🟢"

st.write(f"Servidores monitoreados: **{latest['host'].nunique()}**")

# Mostrar KPIs por host en grid
for _, row in latest.iterrows():
    host = row["host"]
    col1, col2, col3 = st.columns(3)
    cpu_val = row.get("cpu_percent", np.nan)
    mem_val = row.get("memory_percent", np.nan)
    disk_val = row.get("disk_percent", np.nan)

    col1.metric("CPU %", f"{cpu_val:.1f}%", delta=status_color(cpu_val))
    col2.metric("RAM %", f"{mem_val:.1f}%", delta=status_color(mem_val))
    col3.metric("Disco %", f"{disk_val:.1f}%", delta=status_color(disk_val))

st.write("---")
st.write(" Datos más recientes por servidor:")
st.dataframe(latest[["host", "timestamp", "cpu_percent", "memory_percent", "disk_percent"]])
