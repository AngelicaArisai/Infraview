import streamlit as st
import pandas as pd
import time
import plotly.express as px

from config import CSV_FILES, REFRESH_SECONDS
from utils import to_gb, uptime_to_str

# ==================
# CONFIG
# ==================
st.set_page_config(
    page_title="InfraView",
    layout="wide",
    page_icon="🖥️"
)

# ==================
# SIDEBAR
# ==================
st.sidebar.title("⚙ Configuración")

auto = st.sidebar.checkbox("Auto-Refresh", value=True)
st.sidebar.caption(f"Frecuencia: {REFRESH_SECONDS} segundos")

# ==================
# LOAD DATA
# ==================
dfs = []
for f in CSV_FILES:
    try:
        dfs.append(pd.read_csv(f))
    except Exception as e:
        st.sidebar.warning(f"No se pudo cargar: {f} ({e})")

if not dfs:
    st.error("No hay datos disponibles.")
    st.stop()

df = pd.concat(dfs, ignore_index=True)

# ==================
# VALIDATE
# ==================
required_cols = ["host", "cpu_percent", "memory_percent", "disk_percent"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Columnas faltantes: {missing}")
    st.write("Columnas disponibles:")
    st.dataframe(pd.DataFrame({"columns": df.columns}))
    st.stop()

# ==================
# HOST SELECTION
# ==================
hosts = df["host"].unique()
host = st.sidebar.selectbox("Selecciona servidor", hosts)

filtered = df[df["host"] == host]
last = filtered.iloc[-1]

# ==================
# METRICS
# ==================
cpu = last["cpu_percent"]
mem = last["memory_percent"]
disk = last["disk_percent"]

# Opcional: si tienes uptime, red, etc:
uptime = uptime_to_str(last["uptime_seconds"]) if "uptime_seconds" in last else "N/A"
net_sent = last["bytes_sent"] if "bytes_sent" in last else None
net_recv = last["bytes_recv"] if "bytes_recv" in last else None

# Semáforos
def status(p):
    if p < 70: return "🟢 OK"
    if p < 90: return "🟡 Aviso"
    return "🔴 Crítico"

# ==================
# HEADER
# ==================
st.title(f"Dashboard de Servidor: {host}")

# ==================
# KPI GRID
# ==================
col1, col2, col3 = st.columns(3)

col1.metric("CPU %", f"{cpu:.1f}%", status(cpu))
col2.metric("RAM %", f"{mem:.1f}%", status(mem))
col3.metric("Disco %", f"{disk:.1f}%", status(disk))

st.write(f"**Uptime**: {uptime}")

# ==================
# ALERTS
# ==================
if cpu >= 90:
    st.error("🔥 CPU al 90% o más — riesgo crítico")
elif cpu >= 80:
    st.warning("⚠ CPU elevada")

if mem >= 90:
    st.error("🔥 Memoria agotándose")
elif mem >= 80:
    st.warning("⚠ Uso de memoria alto")

if disk >= 95:
    st.error("💀 El disco se llenará pronto")
elif disk >= 90:
    st.warning("⚠ Espacio en disco muy bajo")

st.write("---")

# ==================
# HISTÓRICO — GRÁFICAS PRO
# ==================

def chart(title, y, unit="%"):
    fig = px.line(
        filtered.tail(100),
        x="timestamp",
        y=y,
        title=title
    )
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Tiempo",
        yaxis_title=f"Uso ({unit})",
        template="plotly_white",
        title_x=0.15
    )
    return fig

colA, colB, colC = st.columns(3)
colA.plotly_chart(chart("Histórico CPU", "cpu_percent"), use_container_width=True)
colB.plotly_chart(chart("Histórico RAM", "memory_percent"), use_container_width=True)
colC.plotly_chart(chart("Histórico Disco", "disk_percent"), use_container_width=True)

st.write("---")

# ==================
# TABLA DE ÚLTIMOS DATOS
# ==================
st.subheader("Últimos registros")
st.dataframe(filtered.tail(20))

# ==================
# AUTO REFRESH
# ==================
if auto:
    time.sleep(REFRESH_SECONDS)
    st.rerun()

