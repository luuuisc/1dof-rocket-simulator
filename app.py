#!/usr/bin/env python3
import os, io, json, importlib.util, streamlit as st

SIM_PATH = os.path.join(os.path.dirname(__file__), "src", "simulator.py")
spec = importlib.util.spec_from_file_location("simulator", SIM_PATH)
sim = importlib.util.module_from_spec(spec); spec.loader.exec_module(sim)

st.set_page_config(page_title="1-DoF Rocket Simulator", layout="centered")
st.title("🚀 1-DoF Rocket Trajectory Simulator")
st.caption("MIT 1-DoF formulation • Propulsión UNAM activity")

# ---- helpers ----
def load_pdf_defaults(path="data/pdf_defaults.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Initialize default session values only once
_defaults = {
    "dt": 0.01, "tmax": 60.0, "rho": 1.225, "Cd": 0.5, "g": 9.81,
    "A": 0.01, "D": 0.15, "use_diameter": False,
    "m_dry": 20.0, "m_prop": 30.0, "ue": 960.0,
    "use_sample_curve": True, "chosen_color": "#1f77b4", "use_custom_color": False
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

with st.sidebar:
    st.header("Simulation parameters")

    # --- Load defaults from PDF button ---
    st.markdown("**Defaults from PDF (optional)**")
    if st.button("Load PDF defaults"):
        cfg = load_pdf_defaults()
        # push into session_state so widgets update visually
        for key in ["dt","tmax","rho","g","Cd","A","D","m_dry","m_prop","ue"]:
            if key in cfg:
                st.session_state[key] = cfg[key]
        # decide whether to use diameter or area based on what is given
        if "D" in cfg and cfg["D"] is not None:
            st.session_state["use_diameter"] = True
        elif "A" in cfg and cfg["A"] is not None:
            st.session_state["use_diameter"] = False
        st.success("PDF defaults loaded into the form.")

    # --- Numeric inputs (bound to session_state via keys) ---
    dt   = st.number_input("Time step Δt [s]", min_value=1e-4, max_value=0.1, step=0.001, format="%.4f", key="dt")
    tmax = st.number_input("Max time [s]",     min_value=5.0,   max_value=1000.0, step=1.0,    format="%.1f", key="tmax")
    rho  = st.number_input("Air density ρ [kg/m³]", min_value=0.0, max_value=5.0, step=0.025, key="rho")
    g    = st.number_input("Gravity g [m/s²]", min_value=0.0, max_value=20.0, step=0.01, format="%.2f", key="g")
    Cd   = st.number_input("Drag coefficient CD [-]", min_value=0.0, max_value=2.5, step=0.05, format="%.2f", key="Cd")

    use_diameter = st.checkbox("Use diameter to compute A", key="use_diameter")
    D = st.number_input("Body diameter D [m]", min_value=0.0, max_value=5.0, step=0.001, format="%.3f", key="D")
    if use_diameter:
        A_effective = 3.141592653589793*(D/2.0)**2
        st.caption(f"Reference area A computed from D: A = π(D/2)^2 = {A_effective:.6f} m²")
        A = A_effective
    else:
        A = st.number_input("Reference area A [m²]", min_value=0.0, max_value=5.0, step=0.001, format="%.3f", key="A")

    m_dry  = st.number_input("Dry mass mdry [kg]",      min_value=0.1,  max_value=10000.0, step=0.1,  key="m_dry")
    m_prop = st.number_input("Propellant mass mprop [kg]", min_value=0.0,  max_value=10000.0, step=0.1,  key="m_prop")
    ue     = st.number_input("Exhaust velocity ue [m/s]",  min_value=10.0, max_value=6000.0, step=10.0, key="ue")

    st.markdown("**Motor curve CSV** (`time_s,mdot_kg_s`)")
    uploaded = st.file_uploader("Upload mass-flow curve", type=["csv"])
    use_sample = st.checkbox("Use sample trapezoidal curve", key="use_sample_curve")

    st.markdown("**Plot color (optional)**")
    use_custom_color = st.checkbox("Use custom color", key="use_custom_color")
    chosen_color = st.color_picker("Select color", value=st.session_state.get("chosen_color","#1f77b4")) if use_custom_color else None
    if chosen_color is not None:
        st.session_state["chosen_color"] = chosen_color

    out_dir = "plots"
    if st.button("Run simulation", type="primary"):
        # choose curve path
        if uploaded and not use_sample:
            content = uploaded.read()
            path = os.path.join("data", "uploaded_motor_curve.csv")
            os.makedirs("data", exist_ok=True)
            with open(path, "wb") as f:
                f.write(content)
            curve_path = path
        else:
            curve_path = os.path.join("data", "motor_curve.csv")
            os.makedirs("data", exist_ok=True)
            if not os.path.exists(curve_path):
                with open(curve_path, "w", encoding="utf-8") as f:
                    f.write("time_s,mdot_kg_s\n0.0,0.0\n0.5,3.0\n4.5,3.0\n5.0,0.0\n")

        # run simulation
        metrics = sim.simulate(dt=dt, tmax=tmax, g=g, rho=rho, Cd=Cd, A=A,
                               m_dry=m_dry, m_prop=m_prop, ue=ue,
                               curve_path=curve_path, out_dir=out_dir,
                               color=(st.session_state.get("chosen_color") if use_custom_color else None))
        st.session_state["metrics"] = metrics

st.markdown("### Results")
metrics = st.session_state.get("metrics")
if metrics is None:
    st.info("Choose parameters on the left and click **Run simulation**. Use **Load PDF defaults** to prefill the form.")
else:
    st.json(metrics)

    # Show plots saved by the simulator
    plot_files = [
        ("Altitude vs Time", "altitude_vs_time.png"),
        ("Velocity vs Time", "velocity_vs_time.png"),
        ("Acceleration vs Time", "acceleration_vs_time.png"),
        ("Total Mass vs Time", "mass_vs_time.png"),
        ("Forces vs Time", "forces_vs_time.png"),
    ]
    for title, fname in plot_files:
        path = os.path.join("plots", fname)
        if os.path.exists(path):
            st.markdown(f"**{title}**")
            st.image(path, width='stretch')

    # Download metrics
    buf = io.BytesIO(json.dumps(metrics, indent=2).encode("utf-8"))
    st.download_button("Download metrics.json", data=buf, file_name="metrics.json", mime="application/json")
