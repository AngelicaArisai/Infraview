import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Uso de CPU por Servidor")

# --- Cargar CSVs ---
dfs = [pd.read_csv(f) for f in ["s1.csv", "s2.csv"]]
data = pd.concat(dfs)

# --- Selección de host ---
host = st.selectbox("Selecciona un servidor:", data["host"].unique())
filtered = data[data["host"] == host]

# --- Último valor de CPU ---
latest_cpu = filtered["cpu_percent"].iloc[-1]

# --- Función semáforo ---
def get_status(cpu):
    if cpu < 50:
        return "🟢 Bajo"
    elif cpu < 80:
        return "🟡 Medio"
    else:
        return "🔴 Alto"

# --- Mostrar KPI ---
st.metric(
    label=f"CPU actual en {host}",
    value=f"{latest_cpu:.2f}%",
    delta=get_status(latest_cpu)
)

# --- Gráfico con Plotly ---
fig = px.line(
    filtered,
    x="timestamp",
    y="cpu_percent",
    title=f"Histórico de CPU — {host}",
    markers=True
)

fig.update_layout(
    hovermode="x unified",
    xaxis_title="Tiempo",
    yaxis_title="Uso (%)"
)

st.plotly_chart(fig, use_container_width=True)

# --- Tabla con colores (estilo LogicMonitor) ---
def color_cpu(val):
    if val < 50:
        return "background-color: lightgreen"
    elif val < 80:
        return "background-color: khaki"
    return "background-color: salmon"

st.write("### Datos detallados:")
st.dataframe(
    filtered.style.applymap(color_cpu, subset=["cpu_percent"])
)
