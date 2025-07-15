import streamlit as st
import pandas as pd

# Sidebar: Simulationseinstellungen
st.sidebar.header("Loop Simulation Settings")
num_mod = st.sidebar.number_input("Anzahl Module", min_value=1, value=3, step=1)

rates, inits, caps = [], [], []
for i in range(num_mod):
    st.sidebar.subheader(f"Modul {i+1}")
    rates.append(st.sidebar.slider(
        f"Rate M{i+1} (balls/sec)", 0.1, 2.0, 0.5, 0.1
    ))
    inits.append(st.sidebar.number_input(
        f"Anfangs‑Bälle M{i+1}", min_value=0, value=20, step=1
    ))
    caps.append(st.sidebar.number_input(
        f"Kapazität M{i+1}", min_value=1, value=30, step=1
    ))

T  = st.sidebar.number_input("Sim‑Zeit (s)", min_value=10, value=200, step=10)
dt = st.sidebar.number_input("Time step (s)", min_value=0.01, value=0.1, step=0.01)

st.markdown("""
**Hinweise:**  
- Keine externen Bälle: Gesamtsumme = Summe aller Anfangs‑Bälle.  
- Kapazitätsgrenzen werden beachtet: Wenn nächstes Modul voll ist, blockiert das aktuelle Modul, bis wieder Platz frei wird.  
""")

# Simulation (diskrete Zeit mit Blocking)
def run_sim(rates, inits, caps, T, dt):
    n = len(rates)
    queues = inits.copy()           # aktuelle Puffermengen
    busy   = [False]*n              # Modul verarbeitet gerade
    rem    = [0.0]*n                # verbleibende Service‑Zeit
    records = {"time": []}
    for i in range(n):
        records[f"M{i+1}"] = []
    t = 0.0

    while t <= T:
        # 1) Fertigstellung & Weitergabe
        for i in range(n):
            if busy[i]:
                rem[i] -= dt
                if rem[i] <= 0:
                    j = (i+1) % n
                    # nur weitergeben, wenn nächstes nicht voll
                    if queues[j] < caps[j]:
                        queues[j] += 1
                        busy[i] = False
                        rem[i] = 0.0

        # 2) Starte neue Verarbeitung, falls Puffer >0 und nächste frei
        for i in range(n):
            j = (i+1) % n
            if (not busy[i] and queues[i] > 0 and queues[j] < caps[j]):
                queues[i] -= 1
                busy[i]    = True
                rem[i]     = 1.0 / rates[i]

        # 3) Zustände aufzeichnen
        records["time"].append(t)
        for i in range(n):
            records[f"M{i+1}"].append(queues[i])

        t += dt

    return pd.DataFrame(records)

# Ausführen und Anzeigen
df = run_sim(rates, inits, caps, T, dt)

st.subheader("Pufferstände über die Zeit")
st.line_chart(df.set_index("time"))

st.subheader("Rohdaten (alle Zeitschritte)")
st.dataframe(df, height=400)
