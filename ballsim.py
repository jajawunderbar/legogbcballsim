import streamlit as st
import pandas as pd

# Sidebar: parameters for blocking simulation
st.sidebar.header("Blocking Loop Settings")
n = st.sidebar.number_input("Modules", min_value=1, value=3, step=1)
rates = [st.sidebar.slider(f"Rate M{i+1} (balls/sec)", 0.1, 2.0, 0.5, 0.1) for i in range(n)]
inits = [st.sidebar.number_input(f"Init balls M{i+1}", min_value=0, value=20, step=1) for i in range(n)]
caps  = [st.sidebar.number_input(f"Capacity M{i+1}", min_value=1, value=30, step=1) for i in range(n)]
T     = st.sidebar.number_input("Sim time (s)", min_value=10, value=200, step=10)
dt    = st.sidebar.number_input("Time step (s)", min_value=0.01, value=0.1, step=0.01)

def run_blocking(rates, inits, caps, T, dt):
    n = len(rates)
    queues = inits.copy()       # current buffer levels
    busy   = [False]*n          # is module processing?
    rem    = [0.0]*n            # remaining service time
    records = {"time": []}
    for i in range(n):
        records[f"M{i+1}"] = []
    t = 0.0

    while t <= T:
        # 1) complete & forward if next has space
        for i in range(n):
            if busy[i]:
                rem[i] -= dt
                if rem[i] <= 0:
                    j = (i+1) % n
                    if queues[j] < caps[j]:
                        queues[j] += 1
                        busy[i] = False
                        rem[i] = 0.0

        # 2) start service if buffer>0 and next not full
        for i in range(n):
            j = (i+1) % n
            if not busy[i] and queues[i] > 0 and queues[j] < caps[j]:
                queues[i] -= 1
                busy[i]    = True
                rem[i]     = 1.0 / rates[i]  # service time

        # record state
        records["time"].append(t)
        for i in range(n):
            records[f"M{i+1}"].append(queues[i])

        t += dt

    return pd.DataFrame(records)

# run and display
df = run_blocking(rates, inits, caps, T, dt)
st.subheader("Buffer Levels Over Time")
st.line_chart(df.set_index("time"))
st.subheader("Data Table")
st.dataframe(df, height=400)
