# 🚀 1-DoF Rocket Trajectory Simulator

> **Goal:** Implement a **One Degree of Freedom (1-DoF) Rocket Simulator** that models the vertical trajectory of a rocket, applying key concepts from **Propulsion, Aero-Structures, and Avionics**.  
> This project is based on the MIT lecture notes on rocket trajectories and adapted for **Python** implementation.

---

## 📖 Overview

The **1-DoF simulator** is one of the most fundamental tools in experimental rocketry.  
It allows us to estimate and analyze the **performance of a rocket before flight** by solving the governing physical and mathematical equations of motion.

This repository provides:
- A **numerical solver** for rocket trajectory using **Forward Euler integration**.
- **Plots** of altitude, velocity, mass, and forces over time.
- **Technical notes** in Markdown for learning and documentation purposes.
- A baseline for extending the simulation into higher fidelity models (multi-DoF, 6-DoF, Monte Carlo, etc.).

---

## ⚙️ Features

- Simulation of **vertical rocket motion (1DoF)**.  
- Time integration of **altitude, velocity, and mass**.  
- Force modeling:
  - **Thrust** from mass flow rate & exhaust velocity.  
  - **Aerodynamic drag** with configurable drag coefficient.  
  - **Gravity force**.  
- Configurable **motor mass flow profile** (e.g., solid rocket motor burn).  
- Automatic detection of **MECO** (Main Engine Cut-Off) and **apogee**.  
- Clear plots for performance evaluation.  

---

## 📂 Repository Structure

```

├── src/
│   └── simulator.py      # Python implementation of the 1DoF model
├── docs/
│   ├── theory.md         # Theoretical notes on rocket trajectory
│   ├── report.md         # Technical report template
│   └── references.md     # Key references (MIT notes, textbooks, papers)
├── plots/                # Output graphs from simulations
├── app.py                # Streamlit app
├── requirements.txt      # Dependencies
└── README.md             # Project overview
```

---

## 🧮 Model & Equations

The simulator is governed by the following differential equations.

**Altitude**

$$
\dot{h} = V
$$

**Velocity**

$$
\dot{V} = -g - \frac{1}{2}\frac{\rho\,V\,|V|\,C_D\,A}{m} + \frac{V}{|V|}\frac{\dot{m} {\mathrm{fuel}}\,u_e}{m}
$$

**Mass**

$$
\dot{m} = -\dot{m}_{\mathrm{fuel}}
$$

**Integration method: Forward Euler**

$$
y_{i+1} = y_i + \dot{y}_i\,\Delta t
$$



---

## 📊 Expected Outputs

The simulation produces the following plots:

- **Altitude vs Time**  
- **Velocity vs Time**  
- **Acceleration vs Time**  
- **Mass vs Time**  
- **Forces (Thrust, Drag, Weight) vs Time**

Additionally, the report includes:
- **MECO time and velocity**  
- **Apogee altitude and time**  
- **Maximum altitude, velocity, and acceleration**  

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/1dof-rocket-simulator.git
cd 1dof-rocket-simulator
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

### 4. View results

Check the **plots/** directory or see plots directly in the terminal output.

---

## 📚 References

* MIT Unified Engineering – *Trajectory Calculation Notes*
* Sutton, G. P. & Biblarz, O. (2016). *Rocket Propulsion Elements*. Wiley.
* Anderson, J. D. (2010). *Fundamentals of Aerodynamics*. McGraw-Hill.

---

## 🛠️ Future Work

* Implement **Runge-Kutta 4th order (RK4)** for improved accuracy.
* Introduce **variable air density with altitude**.
* Add **multi-stage rocket simulation**.
* Extend to **6-DoF models** (pitch, yaw, roll dynamics).

---

## 🤝 Contributing

Contributions are welcome!
If you’d like to propose improvements or add features, feel free to **open an issue** or submit a **pull request**.

---

## 📜 License

This project is licensed under the **MIT License** see the [LICENSE](LICENSE) file for details.