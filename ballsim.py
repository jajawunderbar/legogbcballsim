import streamlit as st
import pandas as pd
import numpy as np

# Sidebar: inputs
st.sidebar.header("Loop Simulation Settings")
n = st.sidebar.number_input("Modules", min_value=1, value=10, step=1)
rates = np.array([
    st.sidebar.number_input(
        f"Rate M{i+1} (balls/sec)",
        min_value=0.000, max_value=10.000,
        value=0.700, step=0.001, format="%.3f"
    )
    for i in range(n)
], dtype=float)
inits = np.array([
    st.sidebar.number_input(f"Init balls M{i+1}", min_value=0, value=20, step=1)
    for i in range(n)
], dtype=float)
caps = np.array([
    st.sidebar.number_input(f"Capacity M{i+1}", min_value=1, value=30, step=1)
    for i in range(n)
], dtype=float)
T      = st.sidebar.number_input("Total time (s)",    10, 3600, 1200, step=10)
dt     = st.sidebar.number_input("Time step (s)",     0.001, 1.0, 0.1, step=0.001, format="%.3f")
rec_int= st.sidebar.number_input("Record every (s)", float(dt), float(T), 1.0, step=float(dt))

# Simulation
def run_blocking(rates, inits, caps, T, dt, rec_int):
    n = len(rates)
    queues = inits.copy()
    busy   = np.zeros(n, bool)
    rem    = np.zeros(n, float)
    t, next_rec = 0.0, 0.0
    times, data = [], []

    steps = int(T/dt) + 1
    for _ in range(steps):
        # complete & forward
        rem[busy] -= dt
        done = np.where(busy & (rem <= 0))[0]
        for i in done:
            j = (i+1) % n
            if queues[j] < caps[j]:
                queues[j] = min(queues[j]+1, caps[j])
                busy[i]   = False
                rem[i]    = 0.0

        # start new service
        can = (~busy) & (queues > 0)
        for i in np.where(can)[0]:
            j = (i+1) % n
            if queues[j] < caps[j]:
                queues[i] -= 1
                busy[i]   = True
                rem[i]    = 1.0 / rates[i]

        # record
        if t >= next_rec - dt/2:
            times.append(t)
            data.append(queues.copy())
            next_rec += rec_int

        t += dt

    df = pd.DataFrame(data, columns=[f"M{i+1}" for i in range(n)])
    df.insert(0, "time", times)
    return df

df = run_blocking(rates, inits, caps, T, dt, rec_int)

# Results
st.subheader("Buffer Levels Over Time")
st.line_chart(df.set_index("time"))

st.subheader("Raw Data Table")
st.dataframe(df, height=400)

# compute time to empty / overflow
empty, overflow = [], []
for i in range(n):
    col = f"M{i+1}"
    ser = df[col]
    empty.append(df["time"][ser <= 0].iloc[0] if (ser <= 0).any() else None)
    overflow.append(df["time"][ser >= caps[i]].iloc[0] if (ser >= caps[i]).any() else None)

res = pd.DataFrame({
    "Module":        [f"M{i+1}" for i in range(n)],
    "Time to empty": empty,
    "Time to overflow": overflow
})
st.subheader("Time to Empty/Overflow")
st.table(res)
