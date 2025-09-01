# 1-DoF Rocket Trajectory Simulation — Technical Report

**Author:** Pérez Castro Luis Ángel  
**Team:** Propulsión UNAM  
**Date:** 2025-08-31

---

## Abstract
This report presents a One-Degree-of-Freedom (1-DoF) vertical rocket trajectory simulation implemented in Python. The model integrates altitude, velocity, and mass using an explicit Forward Euler scheme and includes thrust, aerodynamic drag, and gravity. The simulation reproduces the required outputs: time histories of altitude, velocity, acceleration, mass, and forces, as well as key events such as MECO and apogee. Results and implementation choices are validated through time-step refinement and physical consistency checks.

---

## 1. Introduction
The 1-DoF simulator is a core design tool to estimate a rocket’s performance prior to flight, integrating concepts from Propulsion, Aero-structures, and Avionics. In this activity, we follow MIT’s unified notes for trajectory calculation and the Propulsión UNAM assignment brief (deliverables and motor data).

**Objectives**
- Implement a robust numerical integrator for the 1-DoF equations of motion.  
- Generate and analyze the mandated plots and performance metrics (MECO, apogee, maxima).  
- Document the methodology and discuss physical insights.

---

## 2. Physical–Mathematical Model
**State variables:** altitude $h(t)$, velocity $V(t)$, mass $m(t)$.  
**Forces:** gravity, aerodynamic drag, and thrust.

### 2.1 Governing ODEs (MIT formulation)

$$
\dot{h} = V
$$

$$
\dot{V} = -g - \frac{1}{2}\frac{\rho\,V\,|V|\,C_D\,A}{m}
+ \frac{V}{|V|}\,\frac{\dot{m}_{\mathrm{fuel}}\,u_e}{m}
$$

$$
\dot{m} = -\dot{m}_{\mathrm{fuel}}
$$

This compact sign-consistent form (using $V|V|$ and $V/|V|$) is equivalent to the piecewise force expression for ascent/descent and is standard in the academic 1-DoF model.

### 2.2 Force definitions

$$
D = \frac{1}{2}\,\rho\,V^{2}\,C_D\,A
$$

$$
T = \dot{m}_{\mathrm{fuel}}\,u_e
$$

$$
W = m\,g
$$

$$
a = \dot{V} = \frac{F}{m}
$$

**Activity-specific motor data:** the exhaust velocity is $u_e=960\ \mathrm{m/s}$; the mass-flow curve $\dot{m}_{\mathrm{fuel}}(t)$ is provided by the assignment and should be **linearly interpolated** for time stepping.

$$
T(t) = \dot{m}_{\mathrm{fuel}}(t)\,u_e
$$

Given discrete samples $\{(t_k,\dot m_k)\}_{k=0}^{N}$, use piecewise-linear interpolation:

$$
\dot m_{\mathrm{fuel}}(t)=
\begin{cases}
\dot m_k + \dfrac{\dot m_{k+1}-\dot m_k}{\,t_{k+1}-t_k\,}\,(t-t_k), & t_k \le t \le t_{k+1},\\[8pt]
0, & \text{otherwise.}
\end{cases}
$$

In discrete time $t_i$ (for coding and plots):

$$
T_i = \dot m_{\mathrm{fuel},i}\,u_e
$$

$$
m_{i+1} = m_i - \dot m_{\mathrm{fuel},i}\,\Delta t
$$

Stop fuel consumption when propellant is exhausted (MECO condition):

$$
\dot m_{\mathrm{fuel},i} = 0 \quad \text{if} \quad m_i \le m_{\mathrm{dry}}
$$

### 2.3 Equivalent piecewise total force (optional)

$$
F =
\begin{cases}
-\,m g - D + T, & V>0,\\
-\,m g + D - T, & V<0.
\end{cases}
$$

---

## 3. Numerical Method
A fixed-step **Forward Euler** integrator is used.

### 3.1 Discretization (constant time step $\Delta t$)

$$
h_{i+1} = h_i + V_i\,\Delta t
$$

$$
V_{i+1} = V_i +
\left(-g - \frac{1}{2}\frac{\rho\,V_i\,|V_i|\,C_D\,A}{m_i}
+ \frac{V_i}{|V_i|}\frac{\dot{m}_{\mathrm{fuel},i}\,u_e}{m_i}\right)\Delta t
$$

$$
m_{i+1} = m_i - \dot{m}_{\mathrm{fuel},i}\,\Delta t
$$

$$
t_{i+1} = t_i + \Delta t
$$

### Events and termination (with robust interpolation)

- **MECO:** stop thrust when fuel mass reaches the dry mass (or when $\dot m_{\mathrm{fuel}}=0$).

  Detection by **mass crossing**:

  $$
  \text{If } m_i > m_{\mathrm{dry}} \text{ and } m_{i+1}\le m_{\mathrm{dry}},\quad
  \theta_{\mathrm{MECO}}=\frac{m_i-m_{\mathrm{dry}}}{\,m_i-m_{i+1}\,},\quad
  t_{\mathrm{MECO}}=t_i+\theta_{\mathrm{MECO}}\Delta t
  $$

  Record (linear-in-time interpolation):

  $$
  h_{\mathrm{MECO}}\approx h_i+\theta_{\mathrm{MECO}}(h_{i+1}-h_i),\qquad
  V_{\mathrm{MECO}}\approx V_i+\theta_{\mathrm{MECO}}(V_{i+1}-V_i)
  $$

- **Apogee:** first **zero crossing of velocity** after ascent.

  $$
  \text{If } V_i>0 \text{ and } V_{i+1}\le 0,\quad
  \theta_{\mathrm{apo}}=\frac{V_i}{\,V_i-V_{i+1}\,},\quad
  t_{\mathrm{apo}}=t_i+\theta_{\mathrm{apo}}\Delta t
  $$

  Height at apogee (two practical approximations):

  $$
  h_{\mathrm{apo}}\approx h_i+\theta_{\mathrm{apo}}(h_{i+1}-h_i)
  $$

  $$
  h_{\mathrm{apo}}\approx h_i+\frac{1}{2}\,(V_i+0)\,\theta_{\mathrm{apo}}\Delta t
  $$

- **Touchdown:** **root of altitude** on descent.

  $$
  \text{If } h_i>0 \text{ and } h_{i+1}\le 0,\quad
  \theta_{\mathrm{td}}=\frac{h_i}{\,h_i-h_{i+1}\,},\quad
  t_{\mathrm{td}}=t_i+\theta_{\mathrm{td}}\Delta t
  $$

- **Verification (time-step refinement):** repeat with $\Delta t/2$ and compare key traces. Define a relative discrepancy for a signal $y(t)$ (e.g., $h, V$):

  $$
  E_{\mathrm{rel}}(y)=
  \frac{\max_t\left|\,y_{\Delta t}(t)-y_{\Delta t/2}(t)\,\right|}
       {\max_t\left|\,y_{\Delta t/2}(t)\,\right|+\varepsilon},
  \qquad \varepsilon\sim 10^{-9}
  $$

  Reduce $\Delta t$ until $E_{\mathrm{rel}}(y)$ is below your tolerance (e.g., $<1\%$).

---

## 4. Inputs and Initial Conditions
- **Environment:** $g=9.81\ \mathrm{m/s^2}$; $\rho=1.225\ \mathrm{kg/m^3}$ (sea-level baseline).  
- **Vehicle:** $m_{\mathrm{dry}}=$ `<value>` kg; $m_{\mathrm{prop}}=$ `<value>` kg; $C_D=$ `<value>`; $A=$ `<value>` m$^2$.  
- **Motor:** $u_e=960\ \mathrm{m/s}$; $\dot m_{\mathrm{fuel}}(t)$ from the supplied curve (interpolated).  
- **Initial Conditions:** $h_0=0\ \mathrm{m}$, $V_0=0\ \mathrm{m/s}$, $m_0=m_{\mathrm{dry}}+m_{\mathrm{prop}}$.  
- **Numerics:** $\Delta t=$ `<value>` s; $t_{\max}=$ `<value>` s.

---

## 5. Results

> Export figures to `plots/` and reference them below. Each figure must include a caption and a brief explanation, as requested in the assignment.

**Figure 1. Altitude vs Time.**  
*Caption:* Vertical position from lift-off to touchdown; apogee marked.  
*Discussion:* Ascent under thrust, ballistic coast after MECO, descent under drag and gravity.

**Figure 2. Velocity vs Time.**  
*Caption:* Velocity history; zero-crossing indicates apogee.  
*Discussion:* Peak velocity near the end of burn; drag limits further acceleration.

**Figure 3. Acceleration vs Time.**  
*Caption:* Net acceleration; thrust phase vs ballistic phase.  
*Discussion:* Transient spikes may appear at burn start/end; drag dominates during descent.

**Figure 4. Total Mass vs Time.**  
*Caption:* Fuel expenditure during burn; constant dry mass thereafter.  
*Discussion:* Slope equals $-\dot m_{\mathrm{fuel}}$ during burn.

**Figure 5. Forces (Thrust, Drag, Weight) vs Time.**  
*Caption:* Force balance throughout flight.  
*Discussion:* Thrust follows mass-flow curve; drag grows with $V^2$; weight decreases slightly during burn due to mass loss.

### 5.1 Key Performance Metrics
- **MECO:** $t_{\mathrm{MECO}}=$ `<value>` s, $h_{\mathrm{MECO}}=$ `<value>` m, $V_{\mathrm{MECO}}=$ `<value>` m/s.  
- **Apogee:** $t_{\mathrm{apogee}}=$ `<value>` s, $h_{\mathrm{apogee}}=$ `<value>` m.  
- **Maxima:** $h_{\max}=$ `<value>` m, $V_{\max}=$ `<value>` m/s, $a_{\max}=$ `<value>` m/s$^2$.  
- **Time-to-Apogee:** $\Delta t = t_{\mathrm{apogee}} - t_0$ where $t_0=0$ at lift-off.

---

## 6. Analysis and Discussion
- **Physics insight:** During burn, thrust overcomes weight and drag; after MECO, the vehicle coasts ballistically and drag reduces apogee relative to vacuum.  
- **Sensitivity:** Increasing $C_D$ or $A$ lowers both $V_{\max}$ and $h_{\max}$; larger $\dot m$ or $u_e$ boosts performance.  
- **Numerical accuracy:** Euler is conditionally accurate; halving $\Delta t$ should minimally change curves (mesh-refinement check).  
- **Limitations:** Constant $\rho$ and $C_D$; no wind; 1-DoF (no attitude dynamics or control).

---

## 7. Conclusions
The implemented 1-DoF simulator meets the assignment requirements, producing the mandated plots and key metrics (MECO, apogee, maxima). The methodology follows MIT’s formulation and is a solid baseline for higher-fidelity extensions (RK4, variable atmosphere, multi-stage).

---

## References
1. MIT Unified Engineering — *Trajectory Calculation (Lab 2 Lecture Notes).*  
2. Propulsión UNAM — *Actividad 1DoF — Reclutamiento: deliverables and parameters.*

---

## Appendix A — Nomenclature
$t$ time; $h$ altitude; $V$ velocity; $F$ total force; $D$ drag; $T$ thrust; $g$ gravitational acceleration; $m$ mass; $C_D$ drag coefficient; $A$ reference area; $\rho$ air density; $\dot{m}_{\mathrm{fuel}}$ propellant mass-flow rate; $u_e$ exhaust velocity; $\Delta t$ time step.
