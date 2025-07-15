import streamlit as st
import time
import random

# --- Simulationseinstellungen ---
st.title("GBC-Modul Simulation")

processing_time = st.slider("Bearbeitungszeit pro Ball (Sekunden)", 1, 5, 2)
input_buffer_size = st.slider("Max. Input-Puffergröße", 1, 10, 5)
output_buffer_size = st.slider("Max. Output-Puffergröße", 1, 10, 5)
ball_rate = st.slider("Ball-Eingangsrate (Ball alle X Sekunden)", 1, 5, 1)
sim_time = st.slider("Simulationsdauer (Sekunden)", 10, 60, 30)

# --- Statusvariablen ---
input_buffer = []
output_buffer = []
current_ball = None
processing_end_time = 0

ball_id = 0
processed_balls = []

# --- Simulation starten ---
if st.button("Simulation starten"):
    start_time = time.time()
    next_ball_time = start_time

    st.subheader("Laufende Simulation")
    status_area = st.empty()

    while time.time() - start_time < sim_time:
        now = time.time()

        # Ball kommt an
        if now >= next_ball_time:
            if len(input_buffer) < input_buffer_size:
                ball_id += 1
                input_buffer.append({"id": ball_id, "time": now})
            next_ball_time = now + ball_rate

        # Ballverarbeitung starten
        if current_ball is None and input_buffer:
            current_ball = input_buffer.pop(0)
            processing_end_time = now + processing_time

        # Ballverarbeitung beenden
        if current_ball and now >= processing_end_time:
            if len(output_buffer) < output_buffer_size:
                current_ball["processed_at"] = now
                output_buffer.append(current_ball)
                processed_balls.append(current_ball)
                current_ball = None
            else:
                # Output voll – Warte
                pass

        # Statusanzeige
        status_area.markdown(f"""
        ⏱️ Simulationszeit: `{int(now - start_time)}s`\n
        🎱 Eingangs-Puffer: `{len(input_buffer)}`\n
        ⚙️ In Verarbeitung: `{current_ball['id'] if current_ball else '-'}`\n
        📤 Ausgangs-Puffer: `{len(output_buffer)}`\n
        ✅ Verarbeitet: `{len(processed_balls)}`\n
        """)

        time.sleep(0.1)

    st.success("Simulation beendet")
    st.write("Verarbeitete Bälle:", [b["id"] for b in processed_balls])
