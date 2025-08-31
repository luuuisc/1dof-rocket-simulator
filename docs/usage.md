# Usage

## 1) Command-line (batch/reproducible)

```bash
python src/simulator.py --dt 0.01 --tmax 60 --rho 1.225 --Cd 0.5 --A 0.01 \
  --m_dry 20 --m_prop 30 --ue 960 --curve data/motor_curve.csv --out plots
```

* **Inputs:** environment (\$g,\rho\$), vehicle (\$m\_{\mathrm{dry}},m\_{\mathrm{prop}},C\_D,A\$), motor (\$u\_e\$, CSV \$\dot m\$), numerics (\$\Delta t,t\_{\max}\$).
* **CSV format:** `time_s,mdot_kg_s` (seconds, kg/s). Sorted, non-negative; starts/ends at 0.
* **Outputs:** five PNGs in `plots/` + `metrics.json` (MECO, apogee, maxima, touchdown).

## 2) Streamlit UI (interactive)

```bash
pip install -r requirements.txt
streamlit run app.py
```

* Ajusta parámetros desde la barra lateral, sube tu CSV o usa el de ejemplo, y corre la simulación.
* Visualiza las figuras y descarga `metrics.json`.

## 3) Good practices

* **Time-step refinement:** halve \$\Delta t\$ and compare traces; aim for \$E\_{\mathrm{rel}}<1%\$.
* **Propellant consistency:** \$\int \dot m,dt \approx m\_{\mathrm{prop}}\$; ajusta escala/curva si no coincide.
* **Ground contact:** liftoff occurs only when \$T-D-W>0\$ at the pad.
