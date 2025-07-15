import streamlit as st
import pandas as pd
import numpy as np

# Sidebar: user inputs
st.sidebar.header("Sim Loop")
n = st.sidebar.number_input("Modules", min_value=1, value=10, step=1)


T     = st.sidebar.number_input("Total time (s)", 10, 1000, 200)
dt    = st.sidebar.number_input("Time step (s)", 0.01, 1.0, 0.1)
rec_int = st.sidebar.number_input(
    "Record every (s)",
    min_value=float(dt),
    max_value=float(T),
    value=1.0,
    step=float(dt)
)

rates = np.array([
    st.sidebar.slider(f"Rate M{i+1}", 0.1, 2.0, 0.7, 0.1)
    for i in range(n)
])
# use same init for all modules
inits = np.array([
    st.sidebar.number_input(f"Init balls M{i+1}", min_value=0, value=20, step=1)
    for i in range(n)
], dtype=float)
caps  = np.array([
    st.sidebar.number_input(f"Capacity M{i+1}", 1, 1000, 30, step=1)
    for i in range(n)
])

def run_blocking_fast(rates, inits, caps, T, dt, rec_int):
    n = len(rates)
    steps = int(T / dt) + 1
    queues = inits.copy()              # current buffers
    busy   = np.zeros(n, bool)
    rem    = np.zeros(n, float)
    t = 0.0
    next_rec = 0.0
    times, data = [], []

    for _ in range(steps):
        # complete & forward
        rem[busy] -= dt
        done = np.where(busy & (rem <= 0))[0]
        for i in done:
            j = (i + 1) % n
            if queues[j] < caps[j]:
                queues[j] += 1
                busy[i] = False
                rem[i] = 0.0

        # start new service
        can_start = (~busy) & (queues > 0)
        for i in np.where(can_start)[0]:
            j = (i + 1) % n
            if queues[j] < caps[j]:
                queues[i] -= 1
                busy[i]  = True
                rem[i]   = 1.0 / rates[i]

        # record at intervals
        if t >= next_rec - dt/2:
            times.append(t)
            data.append(queues.copy())
            next_rec += rec_int

        t += dt

    df = pd.DataFrame(data, columns=[f"M{i+1}" for i in range(n)])
    df.insert(0, "time", times)
    return df

# Run simulation
df = run_blocking_fast(rates, inits, caps, T, dt, rec_int)
# … nach dem Aufruf von run_blocking_fast …

# compute time to empty / overflow
times_empty    = {}
times_overflow = {}
for i in range(n):
    col  = f"M{i+1}"
    cap  = caps[i]
    ser  = df.set_index("time")[col]
    # first time queue hits 0
    empty = ser[ser <= 0].index
    times_empty[col] = float(empty[0]) if len(empty) else None
    # first time queue reaches capacity
    ovf = ser[ser >= cap].index
    times_overflow[col] = float(ovf[0]) if len(ovf) else None

# show results
st.subheader("Time to Empty / Overflow")
res = pd.DataFrame({
    "Module":      times_empty.keys(),
    "Time Empty":  times_empty.values(),
    "Time Overflow": times_overflow.values()
})
st.table(res)

# Display results
st.subheader("Buffer Levels Over Time")
st.line_chart(df.set_index("time"))
st.subheader("Data Table")
st.dataframe(df, height=400)
