# 🧩 Conclusiones — Simulación de Trayectoria 1-DoF

Este documento resume los hallazgos de la simulación vertical 1-DoF del cohete, ejecutada con los parámetros del enunciado 1-DoF.

---

## Parámetros usados (del PDF)

- Masa seca: `m_seca = 2.2 kg`  
- Masa de combustible: `m_fuel = 0.625 kg`  
- Coeficiente de arrastre: `C_D = 0.75`  
- Diámetro: `D = 0.086 m` (8.6 cm)  
- Densidad del aire: `ρ = 1 kg/m^3`  
- Gravedad: `g = 9.78 m/s^2`  
- Velocidad de eyección: `u_e = 960 m/s`

Área de referencia (frontal) calculada desde el diámetro:

$$
A = \pi\left(\frac{D}{2}\right)^2 = \pi(0.043)^2 \approx 5.8088\times 10^{-3}\ \mathrm{m}^2
$$

Empuje a partir de la curva de flujo másico:

$$
T(t) = \dot m(t)\,u_e
$$

> La curva del motor se ingresa como CSV con encabezado `time_s,mdot_kg_s`. El simulador interpola linealmente.

---

## ✅ Resumen numérico de la corrida

| Magnitud | Valor |
|---|---|
| **MECO (t, h, V)** | **t = 2.00 s**, **h = 192.73 m**, **V = 165.19 m/s** |
| **Apogeo (t, h)** | **t = 12.55 s**, **h = 872.34 m** |
| **Toque de suelo** | **t = 27.83 s** |
| **Máximos** | **h_max = 872.34 m**, **V_max = 167.53 m/s**, **a_max = 101.35 m/s²** |
| **Tiempo total** | **t_end = 27.83 s** |

Tiempos característicos:
- **Burn**: ~**2.0 s** (consumo de 0.625 kg de propelente).  
- **Coast hasta apogeo**: ~**10.55 s**.  
- **Vuelo total**: ~**27.83 s**.

---

## 📈 Lectura física de los resultados

1. **Fase propulsada (0–2 s).**  
   Elevada relación empuje/peso → **aceleración pico ~10.4 g** y rápida ganancia de velocidad hasta \(V_{\max}\).

2. **Coast y apogeo (~2–12.55 s).**  
   Tras MECO, el cohete entra en **vuelo balístico**; el arrastre frena el ascenso y la velocidad cruza por cero en el **apogeo** (872 m).

3. **Descenso (~12.55–27.83 s).**  
   El **arrastre actúa hacia arriba**, reduciendo la magnitud de la aceleración respecto a \(-g\). El contacto con el suelo ocurre a ~27.83 s.

---

## 🔍 Consistencia y validación

- **Cierre de masa:** el consumo integra ~\(0.625\ \mathrm{kg}\), como se especifica.  
- **Eventos detectados con interpolación:**  
  **MECO** (cruce \(m \downarrow m_{\mathrm{seca}}\) o fin de curva), **apogeo** (cruce \(V=0\)), **aterrizaje** (cruce \(h=0\)).  
- **Sanidad física:** \(a \to -g\) cerca del apogeo; masa nunca negativa; empuje nulo tras MECO.

> Recomendación: repetir con \(\Delta t/2\) para verificar que las trazas \(h(t)\) y \(V(t)\) cambian < 1\%.

---

## 🛠️ Implicaciones de diseño

- **Aerodinámica:** con \(C_D=0.75\) y \(A\approx 5.81\times 10^{-3}\ \mathrm{m}^2\), el arrastre reduce el apogeo; **menor \(C_D\)** o **menor \(D\)** lo elevan.  
- **Propulsión:** mayor \(u_e\) o \(\dot m\) (a igual masa total) incrementan la velocidad al burnout y el apogeo.  
- **Estructura:** reducir \(m_{\mathrm{seca}}\) mejora \(T/W\) y desempeño global.

---

## 📌 Conclusión

Con los parámetros del enunciado, el vehículo alcanza **~0.87 km de apogeo** con **burn corto (~2 s)** y **aceleraciones pico ~10 g**. La dinámica observada coincide con el modelo 1-DoF: empuje dominante al inicio, **coast** balístico tras MECO y descenso moderado por arrastre. Es un baseline sólido para evaluar propuestas y futuras mejoras (RK4, \(\rho(h)\), \(C_D(M,Re)\), staging).
