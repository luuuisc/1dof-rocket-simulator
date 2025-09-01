# 🚀 Simulador de Trayectoria de Cohete 1-DoF

> **Objetivo:** Implementar un **Simulador de Cohete de Un Grado de Libertad (1-DoF)** que modele la trayectoria vertical de un cohete, aplicando conceptos clave de **Propulsión, Aeroestructuras y Aviónica**.  
> Este proyecto se basa en las notas del MIT sobre trayectorias de cohetes y está adaptado para implementación en **Python**.

---

## 📖 Descripción general

El **simulador 1-DoF** es una de las herramientas más fundamentales en cohetería experimental.  
Permite estimar y analizar el **desempeño de un cohete antes del vuelo** resolviendo las ecuaciones físicas y matemáticas que gobiernan el movimiento.

Este repositorio proporciona:
- Un **solucionador numérico** para la trayectoria del cohete usando **integración Euler hacia adelante**.
- **Gráficas** de altitud, velocidad, masa y fuerzas en el tiempo.
- **Notas técnicas** en Markdown para aprendizaje y documentación.
- Una base para extender la simulación a modelos de mayor fidelidad (multi-DoF, 6-DoF, Monte Carlo, etc.).

---

## ⚙️ Características

- Simulación del **movimiento vertical del cohete (1DoF)**.  
- Integración temporal de **altitud, velocidad y masa**.  
- Modelado de fuerzas:
  - **Empuje** a partir de flujo másico y velocidad de eyección.  
  - **Arrastre aerodinámico** con coeficiente configurable.  
  - **Gravedad**.  
- **Perfil de gasto másico del motor** configurable (p. ej., motor sólido).  
- Detección automática de **MECO** (corte de motor) y **apogeo**.  
- Gráficas claras para evaluación de desempeño.  

---

> [!IMPORTANT]
> ### Importante — Usa la App de Streamlit y su README
>
> Para **ejecutar y evaluar el simulador** conforme al enunciado, se recomienda usar la **interfaz web en Streamlit** y seguir su **README dedicado**. Ahí encontrarás:
> - **Valores por defecto** del enunciado y cómo **cargarlos automáticamente**.
> - El **formato exacto del CSV de gasto másico** (`time_s,mdot_kg_s`) con ejemplos.
> - Un mapa de la interfaz, opciones de color y dónde se guardan los resultados (**plots/** y **metrics.json**).
> - Guía para la **verificación numérica** (refinamiento de paso temporal).
>
> **Lee primero:** [App README](APP.md)

## 📂 Estructura del repositorio

```

├── src/
│   └── simulator.py      # Implementación en Python del modelo 1DoF
├── docs/
│   ├── theory.md         # Notas teóricas sobre trayectoria de cohetes
│   ├── report.md         # Plantilla de reporte técnico
│   └── references.md     # Referencias clave (notas MIT, libros, artículos)
├── plots/                # Gráficas de salida de las simulaciones
├── app.py                # App de Streamlit
├── requirements.txt      # Dependencias
└── README.md             # Descripción del proyecto

```

---

## 🧮 Modelo y ecuaciones

El simulador se rige por las siguientes ecuaciones diferenciales.

**Altitud**

$$
\dot{h} = V
$$

**Velocidad**

$$
\dot{V} = -g - \frac{1}{2}\frac{\rho\,V\,|V|\,C_D\,A}{m} + \frac{V}{|V|}\frac{\dot{m} {\mathrm{fuel}}\,u_e}{m}
$$

**Masa**

$$
\dot{m} = -\dot{m}_{\mathrm{fuel}}
$$

**Método de integración: Euler hacia adelante**

$$
y_{i+1} = y_i + \dot{y}_i\,\Delta t
$$



---

## 📊 Salidas esperadas

La simulación produce las siguientes gráficas:

- **Altitud vs Tiempo**  
- **Velocidad vs Tiempo**  
- **Aceleración vs Tiempo**  
- **Masa vs Tiempo**  
- **Fuerzas (Empuje, Arrastre, Peso) vs Tiempo**

Además, el reporte incluye:
- **Tiempo y velocidad en MECO**  
- **Altura y tiempo de apogeo**  
- **Altitud, velocidad y aceleración máximas**  

---

## 🚀 Inicio rápido

### 1. Clonar el repositorio
```bash
git clone https://github.com/luuuisc/1dof-rocket-simulator 
cd 1dof-rocket-simulator
````

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la app

```bash
streamlit run app.py
```

### 4. Ver resultados

Revisa la carpeta **plots/** o visualiza las gráficas directamente en la salida de la terminal.

---

## 📚 Referencias

* MIT Unified Engineering – *Trajectory Calculation Notes*
* Sutton, G. P. & Biblarz, O. (2016). *Rocket Propulsion Elements*. Wiley.
* Anderson, J. D. (2010). *Fundamentals of Aerodynamics*. McGraw-Hill.

---

## 🛠️ Trabajo futuro

* Implementar **Runge-Kutta de 4º orden (RK4)** para mejorar la precisión.
* Introducir **densidad del aire variable con la altitud**.
* Agregar **simulación multi-etapa**.
* Extender a **modelos 6-DoF** (dinámica de cabeceo, guiñada y alabeo).

---

## 🤝 Contribuciones

¡Contribuciones bienvenidas!
Si deseas proponer mejoras o añadir funciones, abre un **issue** o envía un **pull request**.

---

## 📜 Licencia

Este proyecto está licenciado bajo **MIT License**; consulta el archivo [LICENSE](LICENSE) para más detalles.

