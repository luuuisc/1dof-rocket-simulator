#!/usr/bin/env python3
import argparse, os, json, math
import numpy as np
import matplotlib.pyplot as plt

def load_motor_curve(path):
    if path and os.path.exists(path):
        data = np.genfromtxt(path, delimiter=',', names=True, dtype=None, encoding=None)
        cols = [c.strip().lower() for c in data.dtype.names]
        try:
            t = np.array(data[data.dtype.names[cols.index('time_s')]]).astype(float)
        except Exception:
            t = np.array(data[data.dtype.names[0]]).astype(float)
        try:
            md = np.array(data[data.dtype.names[cols.index('mdot_kg_s')]]).astype(float)
        except Exception:
            md = np.array(data[data.dtype.names[1]]).astype(float)
        idx = np.argsort(t)
        return t[idx], md[idx]
    return None, None

def mdot_piecewise_linear(t, t_curve, md_curve):
    if t_curve is None or md_curve is None or len(t_curve) < 2:
        return 0.0
    if t <= t_curve[0] or t >= t_curve[-1]:
        if abs(t - t_curve[0]) < 1e-12:
            return float(md_curve[0])
        if abs(t - t_curve[-1]) < 1e-12:
            return float(md_curve[-1])
        return 0.0
    return float(np.interp(t, t_curve, md_curve))

def simulate(dt=0.01, tmax=60.0, g=9.81, rho=1.225, Cd=0.5, A=0.01,
             m_dry=20.0, m_prop=30.0, ue=960.0, curve_path=None, out_dir="plots", color=None):
    g=g
    t_curve, md_curve = load_motor_curve(curve_path)
    if t_curve is None:
        t_curve = np.array([0.0, 0.5, 4.5, 5.0])
        md_curve = np.array([0.0, 3.0, 3.0, 0.0])

    n=int(math.ceil(tmax/dt))+2
    t=np.zeros(n); h=np.zeros(n); V=np.zeros(n); m=np.zeros(n); a=np.zeros(n)
    Th=np.zeros(n); D=np.zeros(n); W=np.zeros(n)

    t[0]=0.0; h[0]=0.0; V[0]=0.0; m[0]=m_dry+m_prop

    meco=False; t_MECO=h_MECO=V_MECO=None
    apo=False; t_apo=h_apo=None
    td=False; t_td=None

    for i in range(n-1):
        mdot = mdot_piecewise_linear(t[i], t_curve, md_curve)
        if m[i] <= m_dry + 1e-12:
            mdot = 0.0

        Th[i] = mdot*ue
        D[i]  = 0.5 * rho * V[i] * abs(V[i]) * Cd * A
        W[i]  = m[i]*g

        sgnV = 1.0 if abs(V[i])<1e-12 else (V[i]/abs(V[i]))
        a[i] = -g - D[i]/m[i] + sgnV*Th[i]/m[i]

        netF = Th[i] - D[i] - W[i]
        if (h[i] <= 0.0 + 1e-12) and (V[i] <= 0.0 + 1e-12) and (netF <= 0.0):
            a[i] = 0.0
            h_new = 0.0
            V_new = 0.0
        else:
            h_new = h[i] + V[i]*dt
            V_new = V[i] + a[i]*dt

        
        m_new = m[i] - mdot*dt
        t_new = t[i] + dt

        # ---- Robust MECO detection ----
        # (1) Fuel exhaustion within the step (mass crossing)
        if (not meco) and (m[i] > m_dry + 1e-12) and (m_new <= m_dry + 1e-12):
            theta_meco = (m[i] - m_dry) / ((m[i] - m_new) + 1e-12)
            t_MECO = t[i] + theta_meco*dt
            h_MECO = h[i] + theta_meco*(h_new - h[i])
            V_MECO = V[i] + theta_meco*(V_new - V[i])
            meco = True

        # (2) End of motor curve (mdot goes to ~0)
        mdot_next = mdot_piecewise_linear(t_new, t_curve, md_curve)
        if (not meco) and (mdot > 1e-12) and (mdot_next <= 1e-12):
            t_MECO = t_new; h_MECO = h_new; V_MECO = V_new; meco = True

        if (not apo) and (V[i] > 0.0) and (V_new <= 0.0):
            theta = V[i]/(V[i]-V_new + 1e-12)
            t_apo = t[i] + theta*dt
            h_apo = h[i] + theta*(h_new-h[i])
            apo=True

        if (not td) and (h[i] > 0.0) and (h_new <= 0.0):
            theta = h[i]/(h[i]-h_new + 1e-12)
            t_td = t[i] + theta*dt
            td=True
            h_new = 0.0

        t[i+1]=t_new; h[i+1]=h_new; V[i+1]=V_new; m[i+1]=max(m_new, m_dry)
        Th[i+1]=Th[i]; D[i+1]=D[i]; W[i+1]=W[i]; a[i+1]=a[i]

        if td:
            break

    # trim arrays to last positive time index
    last = np.max(np.where(t>0.0)) if np.any(t>0.0) else 0
    t=t[:last+1]; h=h[:last+1]; V=V[:last+1]; m=m[:last+1]; a=a[:last+1]
    Th=Th[:last+1]; D=D[:last+1]; W=W[:last+1]

    h_max=float(np.max(h)) if len(h) else None
    V_max=float(np.max(V)) if len(V) else None
    a_max=float(np.max(a)) if len(a) else None

    metrics = {
        "MECO": {"t": t_MECO, "h": h_MECO, "V": V_MECO},
        "apogee": {"t": t_apo, "h": h_apo},
        "touchdown": {"t": t_td},
        "maxima": {"h_max": h_max, "V_max": V_max, "a_max": a_max},
        "final": {"t_end": float(t[-1]) if len(t) else None}
    }

    os.makedirs(out_dir, exist_ok=True)

    # plots (support optional color)
    plt.figure(); plt.plot(t,h, color=color if color else None); plt.xlabel("Time [s]"); plt.ylabel("Altitude h [m]"); plt.title("Altitude vs Time"); plt.grid(True, linestyle=":"); plt.savefig(os.path.join(out_dir,"altitude_vs_time.png"),dpi=150,bbox_inches="tight"); plt.close()
    plt.figure(); plt.plot(t,V, color=color if color else None); plt.xlabel("Time [s]"); plt.ylabel("Velocity V [m/s]"); plt.title("Velocity vs Time"); plt.grid(True, linestyle=":"); plt.savefig(os.path.join(out_dir,"velocity_vs_time.png"),dpi=150,bbox_inches="tight"); plt.close()
    plt.figure(); plt.plot(t,a, color=color if color else None); plt.xlabel("Time [s]"); plt.ylabel("Acceleration a [m/s^2]"); plt.title("Acceleration vs Time"); plt.grid(True, linestyle=":"); plt.savefig(os.path.join(out_dir,"acceleration_vs_time.png"),dpi=150,bbox_inches="tight"); plt.close()
    plt.figure(); plt.plot(t,m, color=color if color else None); plt.xlabel("Time [s]"); plt.ylabel("Mass m [kg]"); plt.title("Total Mass vs Time"); plt.grid(True, linestyle=":"); plt.savefig(os.path.join(out_dir,"mass_vs_time.png"),dpi=150,bbox_inches="tight"); plt.close()

    plt.figure()
    if color:
        plt.plot(t,Th,label="Thrust", color=color, linestyle="-")
        plt.plot(t,D,label="Drag", color=color, linestyle="--")
        plt.plot(t,W,label="Weight", color=color, linestyle=":")
    else:
        plt.plot(t,Th,label="Thrust")
        plt.plot(t,D,label="Drag")
        plt.plot(t,W,label="Weight")
    plt.xlabel("Time [s]"); plt.ylabel("Force [N]"); plt.title("Forces vs Time"); plt.grid(True, linestyle=":"); plt.legend(); plt.savefig(os.path.join(out_dir,"forces_vs_time.png"),dpi=150,bbox_inches="tight"); plt.close()

    with open(os.path.join(out_dir,"metrics.json"),"w",encoding="utf-8") as f:
        json.dump(metrics,f,indent=2)

    return metrics

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--tmax", type=float, default=60.0)
    p.add_argument("--g", type=float, default=9.81)
    p.add_argument("--rho", type=float, default=1.225)
    p.add_argument("--Cd", type=float, default=0.5)
    p.add_argument("--A", type=float, default=0.01)
    p.add_argument("--m_dry", type=float, default=20.0)
    p.add_argument("--m_prop", type=float, default=30.0)
    p.add_argument("--ue", type=float, default=960.0)
    p.add_argument("--curve", type=str, default=None)
    p.add_argument("--out", type=str, default="plots")
    p.add_argument("--color", type=str, default=None, help="Matplotlib color for plots (e.g., #ff0000)")
    args=p.parse_args()
    metrics=simulate(args.dt,args.tmax,args.g,args.rho,args.Cd,args.A,args.m_dry,args.m_prop,args.ue,args.curve,args.out,args.color)
    print(json.dumps(metrics, indent=2))

if __name__=="__main__":
    main()
