import streamlit as st
import pandas as pd

st.title("Actividad de Red")

dfs = [pd.read_csv(f) for f in ["s1.csv","s2.csv"]]
data = pd.concat(dfs)

host = st.selectbox("Servidor", data["host"].unique())
filtered = data[data["host"] == host]

st.line_chart(filtered[["bytes_sent","bytes_recv"]])
