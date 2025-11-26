import streamlit as st
import pandas as pd
import plotly.express as px
from utils import to_gb

st.title("Uso de Memoria")

# --- Cargar CSVs ---
csv_files = ["s1.csv", "s2.csv"]
dfs = []
for f in csv_files:
    try:
        dfs.append(pd.read_csv(f))
    except:
        st.warning(f"No se encontró: {f}")

if not dfs:
    st.error("No hay datos para mostrar.")
    st.stop()

data = pd.concat(dfs)

# --- Validar columnas necesarias ---
required_cols = ["host", "memory_used", "memory_total", "memory_percent"]

missing = [c for c in required_cols if c not in data.columns]
if missing:
    st.error(f"Faltan columnas necesarias: {missing}")
    st.dataframe(data.head())
    st.stop()

# --- Selección de servidor ---
host = st.selectbox("Selecciona un servidor", data["host"].unique())
filtered = data[data["host"] == host]

# --- Último dato ---
last = filtered.iloc[-1]

used_gb = to_gb(last["memory_used"])
total_gb = to_gb(last["memory_total"])
percent = last["memory_percent"]
free_gb = total_gb - used_gb

# --- Semáforo ---
def mem_status(p):
    if p < 70:
        return "🟢 OK"
    elif p < 90:
        return "🟡 Aviso"
    return "🔴 Crítico"

# --- KPI principal ---
st.metric(
    label=f"Uso de memoria en {host}",
    value=f"{percent:.1f}%",
    delta=mem_status(percent)
)

# --- Detalle numérico ---
st.write(f"**Total:** {total_gb:.2f} GB")
st.write(f"**Usada:** {used_gb:.2f} GB")
st.write(f"**Libre:** {free_gb:.2f} GB")

# --- Añadir columnas convertidas ---
filtered["Usada (GB)"] = filtered["memory_used"].apply(to_gb)
filtered["Total (GB)"] = filtered["memory_total"].apply(to_gb)

# --- Gráfica con Plotly ---
fig = px.area(
    filtered.tail(40),
    x="timestamp",
    y="Usada (GB)",
    title=f"Histórico de uso — {host}",
)

fig.update_layout(
    hovermode="x unified",
    xaxis_title="Tiempo",
    yaxis_title="GB Usados",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# --- Tabla estilo LogicMonitor ---
def mem_color(val):
    if val < 70:
        return "background-color: lightgreen"
    elif val < 90:
        return "background-color: khaki"
    return "background-color: salmon"

st.write("### Últimos registros")

table = filtered[
    ["timestamp", "Usada (GB)", "Total (GB)", "memory_percent"]
].tail(15)

table = table.rename(columns={
    "timestamp": "Fecha",
    "memory_percent": "% Mem"
})

st.dataframe(table.style.applymap(mem_color, subset=["% Mem"]))
