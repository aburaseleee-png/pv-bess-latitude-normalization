"""
Draws the two figures used in the summary attachment:
  fig_pv.png    PV capacity vs half-cosine GHI (Moscow excluded from the fit)
  fig_bess.png  BESS capacity vs 1/cos(theta), with and without Moscow
Data: Table I and Table III of Matsuo & Pandey (IEEE PREE 2025).

Run:  pip install numpy matplotlib
      python make_figures.py
"""
import numpy as np
import matplotlib.pyplot as plt

# city, latitude (deg), GHI (kWh/m2/day), HOMER PV (kW), HOMER BESS (kWh)
DATA = [
    ("Kinshasa",     4.442, 4.91,  948, 937.2),
    ("Manaus",       3.119, 5.09,  888, 937.2),
    ("Singapore",    1.352, 4.74,  893, 937.2),
    ("Alice Springs",23.698, 6.19,  690, 976.8),
    ("Cairo",       30.044, 6.12,  635, 950.4),
    ("Riyadh",      24.714, 6.12,  647, 937.2),
    ("Rome",        41.903, 4.41,  865, 871.2),
    ("Atlanta",     33.749, 4.65,  870, 844.8),
    ("Kyoto",       35.012, 3.88, 1027, 937.2),
    ("Winnipeg",    49.895, 3.67,  923, 818.4),
    ("Minneapolis", 44.978, 3.92,  989, 884.4),
    ("Moscow",      55.756, 2.67,  766, 541.2),
]
names = [r[0] for r in DATA]
lat = np.radians([r[1] for r in DATA])
ghi = np.array([r[2] for r in DATA])
pv = np.array([r[3] for r in DATA], dtype=float)
bess = np.array([r[4] for r in DATA])
ghinh = 2 * ghi / (1 + np.cos(lat))      # half-cosine GHI
u = 1 / np.cos(lat)                      # 1/cos(theta)
m = names.index("Moscow")
rest = [i for i in range(len(names)) if i != m]
RED, BLUE = "#C00000", "#1F3864"

# ---------------- Figure (a): PV ----------------
c = np.polyfit(ghinh[rest], pv[rest], 1)
fig, ax = plt.subplots(figsize=(4.3, 3.4), dpi=200)
x = np.linspace(3.3, 6.8, 50)
ax.plot(x, np.polyval(c, x), "k--", lw=1, label="Fit (11 cities, R²=0.947)")
ax.scatter(ghinh[rest], pv[rest], c=BLUE, s=18, zorder=3, label="HOMER (11 cities)")
ax.scatter(ghinh[m], pv[m], c=RED, s=28, zorder=3, label="Moscow (HOMER)")
pred = np.polyval(c, ghinh[m])
ax.scatter(ghinh[m], pred, marker="x", c=RED, s=30, zorder=3, label="Moscow (fit prediction)")
ax.annotate("", xy=(ghinh[m], pred - 15), xytext=(ghinh[m], pv[m] + 15),
            arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))
ax.text(ghinh[m] + 0.1, 950, f"+{(pred - pv[m]) / pv[m] * 100:.0f}%", color=RED, fontsize=8)
ax.set_xlabel("Half-cosine GHI, GHInh (kWh/m²/day)", fontsize=8)
ax.set_ylabel("PV capacity (kW)", fontsize=8)
ax.tick_params(labelsize=7)
ax.legend(fontsize=6.5, loc="upper right", frameon=False)
ax.set_title("(a) PV capacity", fontsize=9)
plt.tight_layout(); plt.savefig("fig_pv.png"); plt.close()

# ---------------- Figure (b): BESS ----------------
c_all = np.polyfit(u, bess, 2)
c_no = np.polyfit(u[rest], bess[rest], 2)
fig, ax = plt.subplots(figsize=(4.3, 3.4), dpi=200)
xx = np.linspace(1.0, 1.8, 60)
ax.plot(xx, np.polyval(c_all, xx), "k-", lw=1, label="Quadratic, all 12 (R²=0.915)")
ax.plot(xx, np.polyval(c_no, xx), "k--", lw=1, label="Quadratic, Moscow excluded (R²≈0.64)")
ax.scatter(u[rest], bess[rest], c=BLUE, s=18, zorder=3, label="HOMER (11 cities)")
ax.scatter(u[m], bess[m], c=RED, s=28, zorder=3, label="Moscow (HOMER)")
ax.set_xlabel("1/cosθ", fontsize=8)
ax.set_ylabel("BESS capacity (kWh)", fontsize=8)
ax.set_ylim(450, 1080)
ax.tick_params(labelsize=7)
ax.legend(fontsize=6.5, loc="lower left", frameon=False)
ax.set_title("(b) BESS capacity", fontsize=9)
plt.tight_layout(); plt.savefig("fig_bess.png"); plt.close()
print("Saved fig_pv.png and fig_bess.png")
