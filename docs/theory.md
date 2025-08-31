# Theory Notes — 1-DoF Rocket

**State variables:** \(h(t)\), \(V(t)\), \(m(t)\).  
**Forces:** weight \(W=mg\), drag \(D=\tfrac{1}{2}\rho V^2 C_D A\), thrust \(T=\dot m_{\mathrm{fuel}}\,u_e\).

## Governing ODEs (MIT)

$$
\dot{h}=V,\qquad
\dot{V}=-\,g-\frac{1}{2}\frac{\rho\,V\,|V|\,C_D\,A}{m}
+\frac{V}{|V|}\frac{\dot m_{\mathrm{fuel}}\,u_e}{m},\qquad
\dot{m}=-\,\dot m_{\mathrm{fuel}}
$$

- Using \(V|V|\) and \(V/|V|\) ensures correct signs for drag and thrust during ascent and descent.
- With constant \(u_e\) (activity spec), \(T=\dot m_{\mathrm{fuel}}\,u_e\).

## Numerical Integration — Forward Euler

$$
h_{i+1}=h_i+V_i\,\Delta t
$$

$$
V_{i+1}=V_i+\left(
-\,g-\tfrac{1}{2}\tfrac{\rho\,V_i\,|V_i|\,C_D\,A}{m_i}
+\tfrac{V_i}{|V_i|}\tfrac{\dot m_{\mathrm{fuel},i}\,u_e}{m_i}
\right)\Delta t
$$

$$
m_{i+1}=m_i-\dot m_{\mathrm{fuel},i}\,\Delta t
$$

## Motor curve and interpolation

Given \(\{(t_k,\dot m_k)\}\), use piecewise-linear interpolation:

$$
\dot m_{\mathrm{fuel}}(t)=
\begin{cases}
\dot m_k+\dfrac{\dot m_{k+1}-\dot m_k}{t_{k+1}-t_k}\,(t-t_k), & t_k\le t\le t_{k+1},\\[8pt]
0, & \text{otherwise.}
\end{cases}
$$

**Consistency check:** ensure \(\displaystyle \int \dot m\,dt \approx m_{\mathrm{prop}}\) (propellant mass).

## Events
- **MECO:** end of burn (\(\dot m\to 0\)) or when \(m\to m_{\mathrm{dry}}\).
- **Apogee:** first zero-crossing of \(V\) after ascent.
- **Touchdown:** altitude crosses zero on descent (interpolate time).

## Outputs (required)
- Plots vs time: \(h\), \(V\), \(a\), \(m\), and forces \((T,D,W)\).
- Metrics: MECO \((t,h,V)\), apogee \((t,h)\), maxima \(h_{\max}, V_{\max}, a_{\max}\), time-to-apogee.
