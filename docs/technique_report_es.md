# Simulación de Trayectoria de Cohete 1-DoF — Reporte Técnico

**Autor:** Pérez Castro Luis Ángel  
**Equipo:** Propulsión UNAM  
**Fecha:** 2025-08-31

---

## Resumen
Este reporte presenta una simulación de trayectoria vertical de un cohete con un grado de libertad (1-DoF) implementada en Python. El modelo integra altitud, velocidad y masa mediante un esquema explícito de Euler hacia adelante e incluye empuje, arrastre aerodinámico y gravedad. La simulación reproduce las salidas requeridas: historiales de tiempo de altitud, velocidad, aceleración, masa y fuerzas, así como eventos clave como MECO y apogeo. Las decisiones de implementación se validan mediante refinamiento del paso de tiempo y verificaciones de consistencia física.

---

## 1. Introducción
El simulador 1-DoF es una herramienta central para estimar el desempeño de un cohete antes del vuelo, integrando conceptos de Propulsión, Aeroestructuras y Aviónica. En esta actividad seguimos las notas unificadas del MIT para el cálculo de trayectorias y el enunciado de Propulsión UNAM (entregables y datos del motor).

**Objetivos**
- Implementar un integrador numérico robusto para las ecuaciones de movimiento 1-DoF.  
- Generar y analizar las gráficas y métricas solicitadas (MECO, apogeo, máximos).  
- Documentar la metodología y discutir los hallazgos físicos.

---

## 2. Modelo Físico–Matemático
**Variables de estado:** altitud \(h(t)\), velocidad \(V(t)\), masa \(m(t)\).  
**Fuerzas:** gravedad, arrastre aerodinámico y empuje.

### 2.1 EDOs rectoras (formulación MIT)

$$
\dot{h} = V
$$

$$
\dot{V} = -g - \frac{1}{2}\frac{\rho\,V\,|V|\,C_D\,A}{m} + \frac{V}{|V|}\frac{\dot{m}_{\mathrm{fuel}}\,u_e}{m}
$$

$$
\dot{m} = -\dot{m}_{\mathrm{fuel}}
$$

Esta forma compacta con signo consistente (usando \(V|V|\) y \(V/|V|\)) es equivalente a la expresión por tramos de las fuerzas en ascenso/descenso y es estándar en el modelo académico 1-DoF.

### 2.2 Definiciones de fuerzas

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

**Dato específico de la actividad:** la velocidad de escape es $u_e = 960\,\mathrm{m/s}$; la curva de gasto másico $\dot m_{\mathrm{fuel}}(t)$ la provee el enunciado y debe **interpolarse linealmente** para el avance temporal.

$$
T(t) = \dot m_{\mathrm{fuel}}(t)\,u_e
$$

Dadas muestras discretas $\{(t_k,\dot m_k)\}_{k=0}^{N}$, usar interpolación lineal por tramos:

$$
\dot m_{\mathrm{fuel}}(t)=
\begin{cases}
\dot m_k + \dfrac{\dot m_{k+1}-\dot m_k}{t_{k+1}-t_k}\,(t-t_k), & t_k \le t \le t_{k+1},\\
0, & \text{otherwise.}
\end{cases}
$$


En tiempo discreto \(t_i\) (para código y gráficas):

$$
T_i = \dot m_{\mathrm{fuel},i}\,u_e
$$

$$
m_{i+1} = m_i - \dot m_{\mathrm{fuel},i}\,\Delta t
$$

Detener el consumo de combustible cuando se agota el propelente (condición MECO):

$$
\dot m_{\mathrm{fuel},i} = 0 \quad \text{if} \quad m_i \le m_{\mathrm{dry}}
$$

### 2.3 Fuerza total por tramos (opcional)

$$
F =
\begin{cases}
-\,m g - D + T, & V>0,\\
-\,m g + D - T, & V<0.
\end{cases}
$$


---

## 3. Método Numérico
Se utiliza un integrador **Euler hacia adelante** con paso fijo.

### 3.1 Discretización (paso de tiempo constante $\Delta t$)

$$
h_{i+1} = h_i + V_i\,\Delta t
$$

$$
V_{i+1} = V_i +
\left(-g - \frac{1}{2}\frac{\rho\,V_i\,|V_i|\,C_D\,A}{m_i} + \frac{V_i}{|V_i|}\frac{\dot{m}_{\mathrm{fuel},i}\,u_e}{m_i}\right)\,\Delta t
$$

$$
m_{i+1} = m_i - \dot{m}_{\mathrm{fuel},i}\,\Delta t
$$

$$
t_{i+1} = t_i + \Delta t
$$


### Eventos y terminación (con interpolación robusta)

**MECO — fin de combustión.**  
Detener empuje cuando la masa de combustible llega a la masa en seco (o cuando $\dot m_{\mathrm{fuel}}=0$).  
Si $m_i>m_{\mathrm{dry}}$ y $m_{i+1}\le m_{\mathrm{dry}}$, definir

$$
\theta_{\mathrm{MECO}}=\frac{m_i-m_{\mathrm{dry}}}{m_i-m_{i+1}},\qquad
t_{\mathrm{MECO}}=t_i+\theta_{\mathrm{MECO}}\,\Delta t
$$

Registrar (interpolación lineal en tiempo)

$$
h_{\mathrm{MECO}}\approx h_i+\theta_{\mathrm{MECO}}(h_{i+1}-h_i),\qquad
V_{\mathrm{MECO}}\approx V_i+\theta_{\mathrm{MECO}}(V_{i+1}-V_i)
$$


**Apogeo — primer cruce por cero de $V$ tras el ascenso.**  
Si $V_i>0$ y $V_{i+1}\le 0$, entonces

$$
\theta_{\mathrm{apo}}=\frac{V_i}{\,V_i-V_{i+1}\,},\qquad
t_{\mathrm{apo}}=t_i+\theta_{\mathrm{apo}}\,\Delta t
$$

Altura al apogeo (dos aproximaciones prácticas)

$$
h_{\mathrm{apo}}\approx h_i+\theta_{\mathrm{apo}}(h_{i+1}-h_i)
$$

$$
h_{\mathrm{apo}}\approx h_i+\frac{1}{2}\,(V_i+0)\,\theta_{\mathrm{apo}}\,\Delta t
$$


**Aterrizaje — raíz de la altitud en descenso.**  
Si $h_i>0$ y $h_{i+1}\le 0$, entonces

$$
\theta_{\mathrm{td}}=\frac{h_i}{\,h_i-h_{i+1}\,},\qquad
t_{\mathrm{td}}=t_i+\theta_{\mathrm{td}}\,\Delta t
$$


**Verificación (refinamiento del paso).**  
Repetir con $\Delta t/2$ y comparar trazas clave. Definir

$$
E_{\mathrm{rel}}(y)=
\frac{\max_t\bigl|\,y_{\Delta t}(t)-y_{\Delta t/2}(t)\,\bigr|}
     {\max_t\bigl|\,y_{\Delta t/2}(t)\,\bigr|+\varepsilon},
\qquad \varepsilon\sim 10^{-9}
$$

Reducir $\Delta t$ hasta que $E_{\mathrm{rel}}(y)$ esté por debajo de la tolerancia (p. ej., $<1\%$).


---

## 4. Entradas y Condiciones Iniciales
- **Ambiente:** $g = 9.78\ \mathrm{m/s^2}$; $\rho = 1.0\ \mathrm{kg/m^3}$ (enunciado 1-DoF).  
- **Vehículo:** $m_{\mathrm{dry}} = 2.2\ \mathrm{kg}$; $m_{\mathrm{prop}} = 0.625\ \mathrm{kg}$; $C_D = 0.75$;  
  diámetro $D = 0.086\ \mathrm{m}$ $(8.6\ \mathrm{cm})$ ⇒ área $A = \pi(D/2)^2 \approx 5.81\times 10^{-3}\ \mathrm{m}^2$.  
- **Motor:** $u_e = 960\ \mathrm{m/s}$; $\dot m_{\mathrm{fuel}}(t)$ de la curva del enunciado (interpolada linealmente).  
- **Condiciones iniciales:** $h_0 = 0\ \mathrm{m}$, $V_0 = 0\ \mathrm{m/s}$, $m_0 = m_{\mathrm{dry}} + m_{\mathrm{prop}} = 2.825\ \mathrm{kg}$.  
- **Numéricos:** $\Delta t = 0.01\ \mathrm{s}$ (línea base; verificar con $\Delta t/2$); $t_{\max} = 60\ \mathrm{s}$ o hasta **touchdown** (evento).

---

## 5. Resultados

> Exportar figuras a `plots/` y referenciarlas abajo. Cada figura debe incluir pie de imagen y breve explicación, tal como pide el enunciado.

**Figura 1. Altitud vs Tiempo.**  
*Pie:* Posición vertical desde el despegue hasta el aterrizaje; apogeo marcado.  
*Discusión:* Ascenso bajo empuje, fase balística tras MECO y descenso bajo arrastre y gravedad.

**Figura 2. Velocidad vs Tiempo.**  
*Pie:* Historial de velocidad; el cruce por cero indica apogeo.  
*Discusión:* Velocidad pico cerca del fin de combustión; el arrastre limita la aceleración.

**Figura 3. Aceleración vs Tiempo.**  
*Pie:* Aceleración neta; fase de empuje vs fase balística.  
*Discusión:* Pueden aparecer transitorios al inicio/fin de la combustión; el arrastre domina en descenso.

**Figura 4. Masa Total vs Tiempo.**  
*Pie:* Consumo de combustible durante la combustión; masa en seco constante después.  
*Discusión:* La pendiente equivale a $-\dot m_{\mathrm{fuel}}$ durante la combustión.

**Figura 5. Fuerzas (Empuje, Arrastre, Peso) vs Tiempo.**  
*Pie:* Balance de fuerzas a lo largo del vuelo.  
*Discusión:* El empuje sigue la curva de gasto másico; el arrastre crece con $V^2$; el peso disminuye levemente durante la combustión por la pérdida de masa.

### 5.1 Métricas de desempeño
- **MECO:** $t_{\mathrm{MECO}}=$ `<value>` s, $h_{\mathrm{MECO}}=$ `<value>` m, $V_{\mathrm{MECO}}=$ `<value>` m/s.  
- **Apogeo:** $t_{\mathrm{apogee}}=$ `<value>` s, $h_{\mathrm{apogee}}=$ `<value>` m.  
- **Máximos:** $h_{\max}=$ `<value>` m, $V_{\max}=$ `<value>` m/s, $a_{\max}=$ `<value>` m/s$^2$.  
- **Tiempo a apogeo:** $\Delta t = t_{\mathrm{apogee}} - t_0$ con $t_0=0$ en el despegue.

---

## 6. Análisis y Discusión
- **Intuición física:** Durante la combustión, el empuje vence al peso y al arrastre; tras MECO, el vehículo vuela en balística y el arrastre reduce el apogeo respecto al vacío.  
- **Sensibilidad:** Aumentar $C_D$ o $A$ reduce $V_{\max}$ y $h_{\max}$; mayor $\dot m$ o $u_e$ mejora el desempeño.  
- **Precisión numérica:** Euler es condicionalmente preciso; al halvar $\Delta t$ las curvas deben cambiar poco (prueba de malla).  
- **Limitaciones:** $\rho$ y $C_D$ constantes; sin viento; 1-DoF (sin actitud ni control).

---

## 7. Conclusiones
El simulador 1-DoF implementado cumple con los requerimientos, produciendo las gráficas y métricas clave (MECO, apogeo, máximos). La metodología sigue la formulación del MIT y sirve como base sólida para extensiones de mayor fidelidad (RK4, atmósfera variable, múltiples etapas).

---

## Referencias
1. MIT Unified Engineering — *Trajectory Calculation (Lab 2 Lecture Notes).*  
2. Propulsión UNAM — *Actividad 1DoF — Reclutamiento: entregables y parámetros.*

---

## Apéndice A — Nomenclatura
$t$ tiempo; $h$ altitud; $V$ velocidad; $F$ fuerza total; $D$ arrastre; $T$ empuje; $g$ gravedad; $m$ masa; $C_D$ coeficiente de arrastre; $A$ área de referencia; $\rho$ densidad del aire; $\dot{m}_{\mathrm{fuel}}$ gasto másico de propelente; $u_e$ velocidad de escape; $\Delta t$ paso de tiempo.
