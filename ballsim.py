import streamlit as st
import pandas as pd

st.sidebar.header("Loop Simulation Settings")
num_mod = st.sidebar.number_input("Number of modules", min_value=1, value=5, step=1)

rates, inits, caps, dwells = [], [], [], []
stall_starts, stall_durs = [], []

for i in range(num_mod):
    st.sidebar.subheader(f"Module {i+1}")
    rates.append(st.sidebar.slider(f"Rate M{i+1} (balls/sec)", 0.1, 2.0, 0.7, 0.1, key=f"rate_{i}"))
    inits.append(st.sidebar.number_input(f"Initial balls M{i+1}", min_value=0, value=20, key=f"init_{i}"))
    caps.append(st.sidebar.number_input(f"Capacity M{i+1}", min_value=1, value=30, key=f"cap_{i}"))
    dwells.append(st.sidebar.slider(f"Dwell time M{i+1} (s)", 0.0, 120.0, 2.0, 0.1, key=f"dwell_{i}"))
    stall_starts.append(st.sidebar.number_input(f"Stall start M{i+1} (s)", min_value=0.0, value=0.0, step=0.1, key=f"stall_start_{i}"))
    stall_durs.append(st.sidebar.number_input(f"Stall dur M{i+1} (s)", min_value=0.0, value=0.0, step=0.1, key=f"stall_dur_{i}"))

T = st.sidebar.number_input("Total sim time (s)", min_value=10, value=200)
dt = st.sidebar.number_input("Time step (s)", min_value=0.01, value=0.1)

def run_sim(rates, inits, caps, dwells, stall_starts, stall_durs, T, dt):
    n = len(rates)
    queues = inits.copy()
    busy = [False]*n
    rem = [0.0]*n
    records = {"time": []}
    for i in range(n):
        records[f"M{i+1}"] = []
    t = 0.0
    while t <= T:
        # complete & forward
        for i in range(n):
            # skip if in stall window
            ss, sd = stall_starts[i], stall_durs[i]
            if busy[i] and not (ss <= t < ss + sd):
                rem[i] -= dt
                if rem[i] <= 0:
                    j = (i+1) % n
                    if queues[j] < caps[j]:
                        queues[j] += 1
                        busy[i] = False
                    else:
                        rem[i] = 0
        # start new service
        for i in range(n):
            ss, sd = stall_starts[i], stall_durs[i]
            j = (i+1) % n
            if not busy[i] and queues[i] > 0 and queues[j] < caps[j] and not (ss <= t < ss + sd):
                queues[i] -= 1
                busy[i] = True
                rem[i] = 1.0/rates[i] + dwells[i]
        # record state
        records["time"].append(t)
        for i in range(n):
            records[f"M{i+1}"].append(queues[i])
        t += dt
    return pd.DataFrame(records)

df = run_sim(rates, inits, caps, dwells, stall_starts, stall_durs, T, dt)

st.subheader("Queue Lengths Over Time")
st.line_chart(df.set_index("time"))

st.subheader("Simulation Data Table")
# display full table with scrollbar
st.dataframe(df, height=500)
