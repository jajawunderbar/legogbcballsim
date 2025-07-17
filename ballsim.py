import streamlit as st
import pandas as pd
import numpy as np

st.sidebar.header("Loop Simulation Settings")
n = st.sidebar.number_input("Number of modules", min_value=1, value=3, step=1)

# 1. Rate als float mit 3 Nachkommastellen
rates = np.array([
    st.sidebar.slider(
        f"Rate M{i+1} (balls/sec)",
        min_value=0.001,    # kleinster Wert
        max_value=10.000,   # beliebig hoch
        value=0.700,        # Default
        step=0.001,         # jetzt kommen 0.714, 0.715, … an
        format="%.3f"       # immer 3 Nachkommastellen anzeigen
    )
    for i in range(n)
], dtype=float)


# 2. Initial-Bälle pro Modul
inits = np.array([
    st.sidebar.number_input(
        f"Init balls M{i+1}", min_value=0, value=20, step=1
    )
    for i in range(n)
], dtype=float)

# 3. Kapazität pro Modul
caps = np.array([
    st.sidebar.number_input(
        f"Capacity M{i+1}", min_value=1, value=30, step=1
    )
    for i in range(n)
], dtype=float)

T      = st.sidebar.number_input("Total simulation time (s)",  10, 3600, 1200, step=10)
dt     = st.sidebar.number_input("Time step (s)",            0.01,  1.0,  0.1, step=0.01)
rec_int= st.sidebar.number_input("Record every (s)", float(dt), float(T), 1.0, step=float(dt))

# Diskrete Blocking‑Simulation
def run_blocking(rates, inits, caps, T, dt, rec_int):
    n = len(rates)
    queues = inits.copy()       # aktueller Pufferstand
    busy   = np.zeros(n, bool) 
    rem    = np.zeros(n, float)
    t = 0.0
    next_rec = 0.0
    times, data = [], []

    steps = int(T/dt) + 1
    for _ in range(steps):
        # 1) Abschlüsse & Weitergabe
        rem[busy] -= dt
        done = np.where(busy & (rem <= 0))[0]
        for i in done:
            j = (i+1) % n
            if queues[j] < caps[j]:
                queues[j] += 1
                busy[i] = False
                rem[i]  = 0.0

        # 2) Starte neuen Ball, wenn möglich
        can_start = (~busy) & (queues > 0)
        for i in np.where(can_start)[0]:
            j = (i+1) % n
            if queues[j] < caps[j]:
                queues[i] -= 1
                busy[i]    = True
                rem[i]     = 1.0 / rates[i]  # keine Rundung!

        # 3) Aufzeichnen
        if t >= next_rec - dt/2:
            times.append(t)
            data.append(queues.copy())
            next_rec += rec_int

        t += dt

    df = pd.DataFrame(data, columns=[f"M{i+1}" for i in range(n)])
    df.insert(0, "time", times)
    return df

df = run_blocking(rates, inits, caps, T, dt, rec_int)

st.subheader("Buffer Levels Over Time")
st.line_chart(df.set_index("time"))

st.subheader("Time to Empty Each Module")
empty_times = []
for i in range(n):
    col = f"M{i+1}"
    # suche ersten Zeitpunkt, an dem <= 0
    mask = df[col] <= 0
    if mask.any():
        # index in df entspricht append-Reihenfolge
        empty_times.append(df.loc[mask, "time"].iloc[0])
    else:
        empty_times.append(None)

res = pd.DataFrame({
    "Module": [f"M{i+1}" for i in range(n)],
    "Time to empty (s)": empty_times
})
st.table(res)
