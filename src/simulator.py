#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador 1-DoF (un grado de libertad) para trayectoria vertical de cohete.

Modelo físico:
  Estados: altura h(t), velocidad V(t), masa m(t).
  Fuerzas: peso W = m g, arrastre D = 0.5 ρ V|V| C_D A, empuje T = ṁ_fuel u_e.
  Ecuaciones (convención "arriba" positiva):
      ḣ = V
      V̇ = -g - D/m + sgn(V) * T/m        (forma de signo consistente)
      ṁ = -ṁ_fuel

Integración:
  Esquema explícito de Euler hacia adelante con paso fijo Δt.
  Detección de eventos con interpolación lineal:
    - MECO (fin de combustión) por cruce de masa (m → m_dry) o por fin de curva ṁ.
    - Apogeo por cruce de V por cero (V_i > 0 y V_{i+1} ≤ 0).
    - Aterrizaje por cruce de h por cero en descenso.

Entradas del motor:
  Curva de flujo másico en CSV con encabezados: time_s, mdot_kg_s.
  Si no se proporciona, se usa una curva trapezoidal de ejemplo.
"""

import argparse, os, json, math
import numpy as np
import matplotlib.pyplot as plt


def load_motor_curve(path):
    """
    Carga una curva de flujo másico (ṁ) desde un archivo CSV.

    Formato esperado de encabezados (no sensible a mayúsculas/minúsculas):
        time_s, mdot_kg_s
    Si los nombres no están, se intenta usar las dos primeras columnas.

    Parámetros
    ----------
    path : str | None
        Ruta al archivo CSV.

    Retorna
    -------
    (t, md) : (np.ndarray, np.ndarray) | (None, None)
        t  : tiempos [s] ordenados ascendentemente.
        md : flujo másico ṁ [kg/s] correspondiente.
        (None, None) si no hay archivo válido.
    """
    if path and os.path.exists(path):
        # names=True permite direccionar por nombre de columna
        data = np.genfromtxt(path, delimiter=',', names=True, dtype=None, encoding=None)
        cols = [c.strip().lower() for c in data.dtype.names]

        # Intento robusto: buscar por nombre y, si falla, tomar las dos primeras columnas
        try:
            t = np.array(data[data.dtype.names[cols.index('time_s')]]).astype(float)
        except Exception:
            t = np.array(data[data.dtype.names[0]]).astype(float)

        try:
            md = np.array(data[data.dtype.names[cols.index('mdot_kg_s')]]).astype(float)
        except Exception:
            md = np.array(data[data.dtype.names[1]]).astype(float)

        # Garantizar que la curva esté ordenada en tiempo
        idx = np.argsort(t)
        return t[idx], md[idx]
    return None, None


def mdot_piecewise_linear(t, t_curve, md_curve):
    """
    Interpolación lineal por tramos de ṁ(t). Cero fuera del soporte.

    Reglas:
      - Si no hay curva o contiene <2 puntos → retorna 0.
      - En los extremos devuelve exactamente el valor tabulado (evita saltos).
      - En el interior usa np.interp (lineal).

    Parámetros
    ----------
    t : float
        Tiempo de consulta [s].
    t_curve, md_curve : np.ndarray | None
        Vectores de soporte (tiempos y ṁ). Deben ser del mismo tamaño.

    Retorna
    -------
    float : ṁ(t) [kg/s]
    """
    if t_curve is None or md_curve is None or len(t_curve) < 2:
        return 0.0

    # Valores exactos en los extremos; 0 fuera del intervalo
    if t <= t_curve[0] or t >= t_curve[-1]:
        if abs(t - t_curve[0]) < 1e-12:
            return float(md_curve[0])
        if abs(t - t_curve[-1]) < 1e-12:
            return float(md_curve[-1])
        return 0.0

    # Interior: interpolación lineal
    return float(np.interp(t, t_curve, md_curve))


def simulate(dt=0.01, tmax=60.0, g=9.81, rho=1.225, Cd=0.5, A=0.01,
             m_dry=20.0, m_prop=30.0, ue=960.0, curve_path=None, out_dir="plots", color=None):
    """
    Ejecuta la simulación 1-DoF con Euler hacia adelante y genera gráficas/métricas.

    Parámetros
    ----------
    dt : float
        Paso de integración [s].
    tmax : float
        Tiempo máximo de simulación [s].
    g : float
        Gravedad [m/s^2].
    rho : float
        Densidad del aire [kg/m^3].
    Cd : float
        Coeficiente de arrastre (adimensional).
    A : float
        Área de referencia [m^2].
    m_dry : float
        Masa en seco del vehículo [kg].
    m_prop : float
        Masa de propelente [kg].
    ue : float
        Velocidad de eyección/exhaust [m/s].
    curve_path : str | None
        Ruta al CSV de la curva de flujo másico (time_s, mdot_kg_s).
    out_dir : str
        Carpeta donde se guardan las figuras y el JSON de métricas.
    color : str | None
        Color opcional (matplotlib) para unificar el estilo de todas las curvas.

    Retorna
    -------
    dict
        Diccionario con métricas clave: MECO, apogeo, touchdown, máximos y t_end.
    """
    # Cargar curva de motor; si no existe, usar una trapezoidal simple de ejemplo
    t_curve, md_curve = load_motor_curve(curve_path)
    if t_curve is None:
        t_curve = np.array([0.0, 0.5, 4.5, 5.0])
        md_curve = np.array([0.0, 3.0, 3.0, 0.0])

    # Prealocar arreglos (un poco holgado: +2) para rendimiento
    n = int(math.ceil(tmax / dt)) + 2
    t = np.zeros(n); h = np.zeros(n); V = np.zeros(n); m = np.zeros(n); a = np.zeros(n)
    Th = np.zeros(n); D = np.zeros(n); W = np.zeros(n)

    # Condiciones iniciales
    t[0] = 0.0; h[0] = 0.0; V[0] = 0.0; m[0] = m_dry + m_prop

    # Variables para eventos (None hasta detectarlos)
    meco = False; t_MECO = h_MECO = V_MECO = None
    apo  = False; t_apo  = h_apo  = None
    td   = False; t_td   = None

    # Bucle principal de integración
    for i in range(n - 1):
        # 1) Flujo másico en el instante actual; si ya no queda propelente → 0
        mdot = mdot_piecewise_linear(t[i], t_curve, md_curve)
        if m[i] <= m_dry + 1e-12:
            mdot = 0.0

        # 2) Fuerzas en i
        Th[i] = mdot * ue                                  # Empuje
        D[i]  = 0.5 * rho * V[i] * abs(V[i]) * Cd * A      # Arrastre (usa V|V|)
        W[i]  = m[i] * g                                   # Peso

        # 3) Aceleración (forma de signo consistente)
        #    sgnV es 0 si V≈0, ±1 en otro caso → evita división por 0
        sgnV = 1.0 if abs(V[i]) < 1e-12 else (V[i] / abs(V[i]))
        a[i] = -g - D[i] / m[i] + sgnV * Th[i] / m[i]

        # 4) Condición de suelo (evita que "perfore" el terreno):
        #    Si está en h≈0, con V≤0 y la fuerza neta no empuja hacia arriba,
        #    fijamos h=0 y V=0 y anulamos la aceleración.
        netF = Th[i] - D[i] - W[i]
        if (h[i] <= 0.0 + 1e-12) and (V[i] <= 0.0 + 1e-12) and (netF <= 0.0):
            a[i]  = 0.0
            h_new = 0.0
            V_new = 0.0
        else:
            # Paso de Euler
            h_new = h[i] + V[i] * dt
            V_new = V[i] + a[i] * dt

        # 5) Actualización de masa y tiempo (Euler)
        m_new = m[i] - mdot * dt
        t_new = t[i] + dt

        # ===== Detección de eventos (con interpolación lineal) =====

        # (a) MECO por cruce de masa: m_i > m_dry y m_{i+1} ≤ m_dry
        if (not meco) and (m[i] > m_dry + 1e-12) and (m_new <= m_dry + 1e-12):
            theta_meco = (m[i] - m_dry) / ((m[i] - m_new) + 1e-12)  # fracción del paso donde ocurre
            t_MECO = t[i] + theta_meco * dt
            h_MECO = h[i] + theta_meco * (h_new - h[i])
            V_MECO = V[i] + theta_meco * (V_new - V[i])
            meco = True

        # (b) MECO por fin de curva (ṁ → 0 entre i e i+1)
        mdot_next = mdot_piecewise_linear(t_new, t_curve, md_curve)
        if (not meco) and (mdot > 1e-12) and (mdot_next <= 1e-12):
            t_MECO, h_MECO, V_MECO = t_new, h_new, V_new
            meco = True

        # (c) Apogeo: cruce de V por cero durante el paso (de + a ≤ 0)
        if (not apo) and (V[i] > 0.0) and (V_new <= 0.0):
            theta = V[i] / (V[i] - V_new + 1e-12)
            t_apo = t[i] + theta * dt
            h_apo = h[i] + theta * (h_new - h[i])
            apo = True

        # (d) Aterrizaje: cruce de h por cero en descenso
        if (not td) and (h[i] > 0.0) and (h_new <= 0.0):
            theta = h[i] / (h[i] - h_new + 1e-12)
            t_td = t[i] + theta * dt
            td = True
            h_new = 0.0  # fijar exactamente en el suelo

        # Escribir el siguiente estado
        t[i + 1]  = t_new
        h[i + 1]  = h_new
        V[i + 1]  = V_new
        m[i + 1]  = max(m_new, m_dry)  # no permitir masas menores que m_dry
        Th[i + 1] = Th[i]
        D[i + 1]  = D[i]
        W[i + 1]  = W[i]
        a[i + 1]  = a[i]

        if td:
            break  # fin de simulación al tocar suelo

    # Recortar arreglos al último índice útil (> 0 s)
    last = np.max(np.where(t > 0.0)) if np.any(t > 0.0) else 0
    t = t[:last + 1]; h = h[:last + 1]; V = V[:last + 1]; m = m[:last + 1]; a = a[:last + 1]
    Th = Th[:last + 1]; D = D[:last + 1]; W = W[:last + 1]

    # Métricas básicas
    h_max = float(np.max(h)) if len(h) else None
    V_max = float(np.max(V)) if len(V) else None
    a_max = float(np.max(a)) if len(a) else None

    metrics = {
        "MECO": {"t": t_MECO, "h": h_MECO, "V": V_MECO},
        "apogee": {"t": t_apo, "h": h_apo},
        "touchdown": {"t": t_td},
        "maxima": {"h_max": h_max, "V_max": V_max, "a_max": a_max},
        "final": {"t_end": float(t[-1]) if len(t) else None}
    }

    # === Salidas: figuras y JSON de métricas ===
    os.makedirs(out_dir, exist_ok=True)

    # Altura
    plt.figure()
    plt.plot(t, h, color=color if color else None)
    plt.xlabel("Time [s]"); plt.ylabel("Altitude h [m]")
    plt.title("Altitude vs Time"); plt.grid(True, linestyle=":")
    plt.savefig(os.path.join(out_dir, "altitude_vs_time.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # Velocidad
    plt.figure()
    plt.plot(t, V, color=color if color else None)
    plt.xlabel("Time [s]"); plt.ylabel("Velocity V [m/s]")
    plt.title("Velocity vs Time"); plt.grid(True, linestyle=":")
    plt.savefig(os.path.join(out_dir, "velocity_vs_time.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # Aceleración
    plt.figure()
    plt.plot(t, a, color=color if color else None)
    plt.xlabel("Time [s]"); plt.ylabel("Acceleration a [m/s^2]")
    plt.title("Acceleration vs Time"); plt.grid(True, linestyle=":")
    plt.savefig(os.path.join(out_dir, "acceleration_vs_time.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # Masa
    plt.figure()
    plt.plot(t, m, color=color if color else None)
    plt.xlabel("Time [s]"); plt.ylabel("Mass m [kg]")
    plt.title("Total Mass vs Time"); plt.grid(True, linestyle=":")
    plt.savefig(os.path.join(out_dir, "mass_vs_time.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # Fuerzas
    plt.figure()
    if color:
        plt.plot(t, Th, label="Thrust", color=color, linestyle="-")
        plt.plot(t, D,  label="Drag",   color=color, linestyle="--")
        plt.plot(t, W,  label="Weight", color=color, linestyle=":")
    else:
        plt.plot(t, Th, label="Thrust")
        plt.plot(t, D,  label="Drag")
        plt.plot(t, W,  label="Weight")
    plt.xlabel("Time [s]"); plt.ylabel("Force [N]")
    plt.title("Forces vs Time"); plt.grid(True, linestyle=":"); plt.legend()
    plt.savefig(os.path.join(out_dir, "forces_vs_time.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # Guardar métricas
    with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


def main():
    """
    Punto de entrada por CLI. Ejemplos:

      # Usar parámetros por defecto y una curva CSV
      python simulator.py --curve data/motor.csv

      # Parámetros del enunciado 1-DoF (g=9.78, ρ=1.0, m_dry=2.2, m_prop=0.625, Cd=0.75, A≈5.81e-3)
      python simulator.py --g 9.78 --rho 1.0 --m_dry 2.2 --m_prop 0.625 --Cd 0.75 --A 0.00581 --ue 960
    """
    p = argparse.ArgumentParser()
    p.add_argument("--dt",     type=float, default=0.01,  help="Paso de integración Δt [s]")
    p.add_argument("--tmax",   type=float, default=60.0,  help="Tiempo máximo de simulación [s]")
    p.add_argument("--g",      type=float, default=9.81,  help="Gravedad g [m/s^2]")
    p.add_argument("--rho",    type=float, default=1.225, help="Densidad del aire ρ [kg/m^3]")
    p.add_argument("--Cd",     type=float, default=0.5,   help="Coeficiente de arrastre C_D [-]")
    p.add_argument("--A",      type=float, default=0.01,  help="Área de referencia A [m^2]")
    p.add_argument("--m_dry",  type=float, default=20.0,  help="Masa en seco [kg]")
    p.add_argument("--m_prop", type=float, default=30.0,  help="Masa de propelente [kg]")
    p.add_argument("--ue",     type=float, default=960.0, help="Velocidad de eyección u_e [m/s]")
    p.add_argument("--curve",  type=str,   default=None,  help="Ruta al CSV (time_s,mdot_kg_s)")
    p.add_argument("--out",    type=str,   default="plots", help="Carpeta de salida para figuras/JSON")
    p.add_argument("--color",  type=str,   default=None,  help="Color matplotlib (p. ej. '#1f77b4')")
    args = p.parse_args()

    metrics = simulate(args.dt, args.tmax, args.g, args.rho, args.Cd, args.A,
                       args.m_dry, args.m_prop, args.ue, args.curve, args.out, args.color)

    # Imprimir métricas en stdout en formato JSON (útil para CI o bitácoras)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
