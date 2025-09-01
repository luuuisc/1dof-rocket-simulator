# 🖥️ Using the Streamlit Interface

Follow these steps to create an isolated environment, install dependencies, and launch the app.

## 1) Create and activate a virtual environment

> **Python**: 3.9–3.12 recommended

### macOS / Linux (bash/zsh)
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
````

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 2) Install requirements

```bash
pip install -r requirements.txt
```

> Optional (improves live-reload performance):

```bash
pip install watchdog
```

## 3) Run the app

```bash
streamlit run app.py
```

## 4) Deactivate the environment (when finished)

```bash
deactivate
```

### Notes

* If the port is busy: `streamlit run app.py --server.port 8502`
* If you see a “watchdog” message: it’s optional; install with `pip install watchdog`.

The app opens in your browser. The **left sidebar** controls the simulation; the **main panel** shows results (metrics + plots).

### 1) Sidebar — Parameters & Inputs

**A. Quick defaults (from the PDF)**

* Click **“Load PDF defaults”** to prefill values from `data/pdf_defaults.json`.
* If your PDF gives **diameter**, the app switches to “Use diameter to compute A”.
* If it gives **area**, it keeps “A” as a direct input.

**B. Environment & aerodynamics**

* **Time step** `Δt [s]`: baseline `0.01`. (Refine to `0.005` to verify mesh-convergence.)
* **Max time \[s]**: e.g., `60`.
* **Air density ρ \[kg/m³]**, **Gravity g \[m/s²]**, **Drag coefficient C\_D \[-]**.

**C. Geometry — area or diameter**

* Toggle **“Use diameter to compute A”**.

  * If ON: enter **D \[m]**; the app computes $A=\pi(D/2)^2$.
  * If OFF: enter **A \[m²]** directly.

**D. Mass properties & motor**

* **Dry mass** $m_{\mathrm{dry}}$ \[kg], **Propellant mass** $m_{\mathrm{prop}}$ \[kg].
* **Exhaust velocity** $u_e$ \[m/s] (activity uses **960 m/s**).

**E. Motor curve (mass-flow)**

* Upload CSV (**`time_s,mdot_kg_s`**) or tick **“Use sample trapezoidal curve”**.
* Example CSV (header required):

  ```csv
  time_s,mdot_kg_s
  0.00,0.00
  0.50,3.00
  4.50,3.00
  5.00,0.00
  ```

**F. Plot style (optional)**

* Check **“Use custom color”** to pick a single color for all plots.

Finally, click **“Run simulation”**.

---

## 📤 Outputs (what you get)

* **Metrics JSON** (MECO, Apogee, Touchdown, maxima, t\_end) appears in the main panel and is saved as:

  ```
  plots/metrics.json
  ```

  You can also **Download metrics.json** from the button.

* **Plots** saved to `plots/`:

  ```
  altitude_vs_time.png
  velocity_vs_time.png
  acceleration_vs_time.png
  mass_vs_time.png
  forces_vs_time.png
  ```

---

## 🧭 Interface Map

<!-- Sidebar overview -->
<p><strong>Sidebar overview</strong></p>
<p align="center">
  <img src="docs/images/sidebar.png" alt="UI Sidebar" width="800"><br>
  <em>Left panel with all controls to configure the simulation (time step, environment, geometry, masses, and motor curve).</em>
</p>

<!-- Running a simulation -->
<p><strong>Running a simulation</strong></p>

<p align="center">
  <img src="docs/images/result.png" alt="Run Results - Metrics" width="900"><br>
  <em>Summary of computed metrics (MECO, apogee, touchdown, maxima) after running the simulation.</em>
</p>

<p align="center">
  <img src="docs/images/plot1.png" alt="Run Results - Plot 1" width="900"><br>
  <em>Key time histories (e.g., altitude, velocity, acceleration) produced by the solver.</em>
</p>

<p align="center">
  <img src="docs/images/plot2.png" alt="Run Results - Plot 2" width="900"><br>
  <em>Forces over time (thrust, drag, weight) and total mass evolution.</em>
</p>


---

## 🧪 Model & Equations (GitHub-friendly)

> [!TIP]
> Ensure there’s a blank line before/after each `$$...$$` block. Here’s the corrected velocity equation:

**Altitude**

$$
\dot{h} = V
$$

**Velocity**

$$
\dot{V} = -g - \frac{1}{2}\frac{\rho\,V\,|V|\,C_D\,A}{m} \;+\; \frac{V}{|V|}\,\frac{\dot{m}_{\mathrm{fuel}}\,u_e}{m}
$$

**Mass**

$$
\dot{m} = -\dot{m}_{\mathrm{fuel}}
$$

**Integration (Forward Euler)**

$$
y_{i+1} = y_i + \dot{y}_i\,\Delta t
$$

---

## 🧩 Tips & Troubleshooting

* **Units**: Use **SI** consistently. If the PDF gives **diameter in cm**, convert to **m** (e.g., 8.6 cm → 0.086 m).
* **CSV header**: Must be exactly `time_s,mdot_kg_s` (case-insensitive).
* **MECO not detected?** Check that total propellant mass integrates ≈ $m_{\mathrm{prop}}$ and that `mdot` goes to zero at end.
* **Refinement check**: Try `Δt = 0.01`, then `0.005`. Curves and metrics should change only slightly.
* **Where files go**: the app writes `data/` (curves) and `plots/` (figures + metrics).

---

## 🧰 Optional: Run the core simulator from CLI

```bash
python src/simulator.py --g 9.78 --rho 1.0 --m_dry 2.2 --m_prop 0.625 --Cd 0.75 --A 0.00581 --ue 960 --curve data/motor_curve.csv
```

Outputs are saved in `plots/` and metrics printed to stdout as JSON.
