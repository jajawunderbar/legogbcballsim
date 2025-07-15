import streamlit as st
import pandas as pd

st.sidebar.header("Fluid‑Loop Settings")
n = st.sidebar.number_input("Modules", 1, 20, 3)
rates = [st.sidebar.slider(f"Rate M{i+1}", 0.1, 2.0, 0.5, 0.1) for i in range(n)]
inits = [st.sidebar.number_input(f"Init Bälle M{i+1}", 0, 100, 20) for i in range(n)]
T  = st.sidebar.number_input("Sim‑Zeit (s)", 10, 1000, 200)
dt = st.sidebar.number_input("Δt (s)",      0.01, 1.0,   0.1)

def run_fluid(rates, inits, T, dt):
    n = len(rates)
    q = list(inits)
    rec = {"t":[]}
    for i in range(n): rec[f"M{i+1}"]=[]

    t = 0
    while t<=T:
        rec["t"].append(t)
        for i in range(n): rec[f"M{i+1}"].append(q[i])
        dq = [0]*n
        for i in range(n):
            mv = min(q[i], rates[i]*dt)
            dq[i]   -= mv
            dq[(i+1)%n] += mv
        for i in range(n):
            q[i] += dq[i]
        t += dt

    return pd.DataFrame(rec)

df = run_fluid(rates, inits, T, dt)
st.line_chart(df.set_index("t"))
st.dataframe(df, height=400)
