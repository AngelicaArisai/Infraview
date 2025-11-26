import streamlit as st
import pandas as pd
import plotly.express as px
from utils import to_gb

st.title("Uso de Disco")

# --- Leer CSVs ---
dfs = [pd.read_csv(f) for f in ["s1.csv", "s2.csv"]]
data = pd.concat(dfs)

# --- Selector de servidor ---
host = st.selectbox("Selecciona un servidor", data["host"].unique())
filtered = data[data["host"] == host]

# --- Últimos datos ---
last = filtered.iloc[-1]

total_gb = to_gb(last["disk_total"])
used_gb = to_gb(last["disk_used"])
free_gb = to_gb(last["disk_free"])
percent = last["disk_percent"]

# --- Estado semaforizado ---
def disk_status(p):
    if p < 70:
        return "🟢 OK"
    elif p < 90:
        return "🟡 Aviso"
    return "🔴 Crítico"

# --- KPI ---
st.metric(
    label=f"Uso actual en {host}",
    value=f"{percent:.2f}%",
    delta=disk_status(percent)
)

# --- Info detallada ---
st.write(f"**Capacidad total:** {total_gb:.2f} GB")  
st.write(f"**En uso:** {used_gb:.2f} GB")  
st.write(f"**Libre:** {free_gb:.2f} GB")  

# --- Agregar columnas convertidas ---
filtered["Total (GB)"] = filtered["disk_total"].apply(to_gb)
filtered["Usado (GB)"] = filtered["disk_used"].apply(to_gb)
filtered["Libre (GB)"] = filtered["disk_free"].apply(to_gb)

# --- Plotly Line Chart ---
fig = px.area(
    filtered.tail(40),
    x="timestamp",
    y="Usado (GB)",
    title=f"Histórico de uso de disco — {host}",
)

fig.update_layout(
    hovermode="x unified",
    xaxis_title="Tiempo",
    yaxis_title="GB Usados",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# --- Tabla lógica estilo LM ---
def color_disk(val):
    if val < 70:
        return "background-color: lightgreen"
    elif val < 90:
        return "background-color: khaki"
    return "background-color: salmon"

st.write("### Últimos registros:")

table = filtered[[
    "timestamp",
    "Usado (GB)",
    "Libre (GB)",
    "disk_percent"
]].tail(15)

table = table.rename(columns={
    "timestamp": "Fecha",
    "disk_percent": "% Disco"
})

st.dataframe(table.style.applymap(color_disk, subset=["% Disco"]))
