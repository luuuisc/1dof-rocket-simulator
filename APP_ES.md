# 🖥️ Uso de la Interfaz Streamlit

Sigue estos pasos para crear un entorno aislado, instalar dependencias y lanzar la app.

## 1) Crear y activar un entorno virtual

> **Python**: se recomienda 3.9–3.12

### macOS / Linux (bash/zsh)
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
```

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 2) Instalar dependencias

```bash
pip install -r requirements.txt
```

> Opcional (mejora el live-reload):

```bash
pip install watchdog
```

## 3) Ejecutar la app

```bash
streamlit run app.py
```

## 4) Desactivar el entorno (al terminar)

```bash
deactivate
```

### Notas

* Si el puerto está ocupado: `streamlit run app.py --server.port 8502`
* Si ves un mensaje sobre “watchdog”: es opcional; instala con `pip install watchdog`.

La app se abre en tu navegador. La **barra lateral izquierda** controla la simulación; el **panel principal** muestra resultados (métricas + gráficas).

### 1) Barra lateral — Parámetros e insumos

**A. Carga rápida de valores por defecto (desde el PDF)**

* Haz clic en **“Load PDF defaults”** para precargar valores desde `data/pdf_defaults.json`.
* Si tu PDF proporciona **diámetro**, la app cambia a “Use diameter to compute A”.
* Si proporciona **área**, mantiene “A” como entrada directa.

**B. Ambiente y aerodinámica**

* **Paso de tiempo** `Δt [s]`: base `0.01`. (Refina a `0.005` para verificar convergencia de malla.)
* **Tiempo máximo \[s]**: p. ej., `60`.
* **Densidad del aire ρ \[kg/m³]**, **gravedad g \[m/s²]**, **coeficiente de arrastre C\_D \[-]**.

**C. Geometría — área o diámetro**

* Activa **“Use diameter to compute A”**.

  * Si está **ON**: ingresa **D \[m]**; la app calcula $A=\pi(D/2)^2$.
  * Si está **OFF**: ingresa **A \[m²]** directamente.

**D. Masas y motor**

* **Masa en seco** $m_{\mathrm{dry}}$ \[kg], **masa de propelente** $m_{\mathrm{prop}}$ \[kg].
* **Velocidad de eyección** $u_e$ \[m/s] (la actividad usa **960 m/s**).

**E. Curva del motor (gasto másico)**

* Sube un CSV (**`time_s,mdot_kg_s`**) o marca **“Use sample trapezoidal curve”**.
* CSV de ejemplo (encabezado obligatorio):

  ```csv
  time_s,mdot_kg_s
  0.00,0.00
  0.50,3.00
  4.50,3.00
  5.00,0.00
  ```

**F. Estilo de gráficas (opcional)**

* Marca **“Use custom color”** para elegir un color único para todas las gráficas.

Finalmente, haz clic en **“Run simulation”**.

---

## 📤 Salidas (qué obtienes)

* **Metrics JSON** (MECO, apogeo, touchdown, máximos, `t_end`) aparece en el panel principal y se guarda en:

  ```
  plots/metrics.json
  ```

  También puedes **descargar `metrics.json`** con el botón correspondiente.

* **Gráficas** guardadas en `plots/`:

  ```
  altitude_vs_time.png
  velocity_vs_time.png
  acceleration_vs_time.png
  mass_vs_time.png
  forces_vs_time.png
  ```

---

## 🧭 Mapa de la interfaz

**Vista de la barra lateral**

![UI Sidebar](../1_DoF/docs/images/sidebar.png)

**Ejecución de una simulación**

![Run Results](../1_DoF/docs/images/result.png)
![Run Results](../1_DoF/docs/images/plot1.png)
![Run Results](../1_DoF/docs/images/plot2.png)

---

## 🧪 Modelo y ecuaciones (compatible con GitHub)

> \[!TIP]
> Asegúrate de dejar una línea en blanco antes y después de cada bloque `$$...$$`. Ecuación de velocidad corregida:

**Altitud**

$$
\dot{h} = V
$$

**Velocidad**

$$
\dot{V} = -g - \frac{1}{2}\frac{\rho\,V\,|V|\,C_D\,A}{m} \;+\; \frac{V}{|V|}\,\frac{\dot{m}_{\mathrm{fuel}}\,u_e}{m}
$$

**Masa**

$$
\dot{m} = -\dot{m}_{\mathrm{fuel}}
$$

**Integración (Euler hacia adelante)**

$$
y_{i+1} = y_i + \dot{y}_i\,\Delta t
$$

---

## 🧩 Consejos y solución de problemas

* **Unidades**: usa **SI** de forma consistente. Si el PDF da **diámetro en cm**, convierte a **m** (p. ej., 8.6 cm → 0.086 m).
* **Encabezado del CSV**: debe ser exactamente `time_s,mdot_kg_s` (insensible a mayúsculas).
* **¿No se detecta MECO?** Verifica que la masa total de propelente integre ≈ $m_{\mathrm{prop}}$ y que `mdot` llegue a cero al final.
* **Chequeo de refinamiento**: prueba `Δt = 0.01` y luego `0.005`. Las curvas y métricas deberían cambiar poco.
* **Dónde se guardan los archivos**: la app escribe en `data/` (curvas) y `plots/` (figuras + métricas).

---

## 🧰 Opcional: ejecutar el simulador “core” por CLI

```bash
python src/simulator.py --g 9.78 --rho 1.0 --m_dry 2.2 --m_prop 0.625 --Cd 0.75 --A 0.00581 --ue 960 --curve data/motor_curve.csv
```

Las salidas se guardan en `plots/` y las métricas se imprimen en stdout como JSON.
