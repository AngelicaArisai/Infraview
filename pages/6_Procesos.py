import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Top Procesos por Consumo de CPU")

# --- Leer CSVs ---
dfs = [pd.read_csv(f) for f in ["s1.csv", "s2.csv"]]
data = pd.concat(dfs)

# --- Selector de host ---
host = st.selectbox("Selecciona un servidor:", data["host"].unique())
filtered = data[data["host"] == host]

# --- Últimos 20 registros ---
top = filtered[[
    "timestamp",
    "top_process_name",
    "top_process_pid",
    "top_process_cpu_percent"
]].tail(20)

# Renombrar columnas
top = top.rename(columns={
    "timestamp": "Fecha",
    "top_process_name": "Proceso",
    "top_process_pid": "PID",
    "top_process_cpu_percent": "CPU %"
})

# --- Obtener último proceso ---
last_proc = top.iloc[-1]
proc_name = last_proc["Proceso"]
proc_cpu = last_proc["CPU %"]

# --- Semáforo ---
def proc_status(cpu):
    if cpu < 30:
        return "🟢 Normal"
    elif cpu < 70:
        return "🟡 Alto"
    return "🔴 Crítico"

# --- KPI ---
st.metric(
    label=f"Proceso más activo en {host}",
    value=f"{proc_name} ({proc_cpu:.2f}%)",
    delta=proc_status(proc_cpu)
)

# --- Gráfico de barras ---
fig = px.bar(
    top,
    x="Fecha",
    y="CPU %",
    color="CPU %",
    color_continuous_scale="RdYlGn_r",
    title=f"CPU del proceso más activo — {host}"
)

fig.update_layout(
    xaxis_title="Tiempo",
    yaxis_title="Uso de CPU (%)",
    hovermode="x"
)

st.plotly_chart(fig, use_container_width=True)

# --- Estilos de tabla ---
def color_cpu(val):
    if val < 30:
        return "background-color: lightgreen"
    elif val < 70:
        return "background-color: khaki"
    return "background-color: salmon"

st.write("### Últimos procesos detectados:")
st.dataframe(top.style.applymap(color_cpu, subset=["CPU %"]))

