"""
Preliminary analysis of the PV-BESS sizing results published in
Matsuo & Pandey, "A Unified PV-BESS Capacity Estimation Framework for Rural
Microgrids" (IEEE PREE 2025), Table I and Table III.

Only the 12 published points are used (latitude, GHI, HOMER PV and BESS
capacity), so this is a first check, not a replacement for a HOMER study.

Run:  python analysis.py        (needs numpy only)
"""
import numpy as np

# ---------------------------------------------------------------- 1. DATA
# city, latitude (deg), GHI (kWh/m2/day), avg temp (C), avg wind (m/s),
# HOMER PV capacity (kW), HOMER BESS capacity (kWh)   -- Table I and III
DATA = [
    ("Kinshasa",     4.442, 4.91, 25.12, 1.22,  948, 937.2),
    ("Manaus",       3.119, 5.09, 26.69, 0.65,  888, 937.2),
    ("Singapore",    1.352, 4.74, 27.16, 2.04,  893, 937.2),
    ("Alice Springs",23.698, 6.19, 22.31, 3.18,  690, 976.8),
    ("Cairo",       30.044, 6.12, 26.23, 2.94,  635, 950.4),
    ("Riyadh",      24.714, 6.12, 26.23, 2.94,  647, 937.2),
    ("Rome",        41.903, 4.41, 17.14, 2.29,  865, 871.2),
    ("Atlanta",     33.749, 4.65, 15.47, 1.20,  870, 844.8),
    ("Kyoto",       35.012, 3.88, 14.99, 2.27, 1027, 937.2),
    ("Winnipeg",    49.895, 3.67,  4.00, 3.51,  923, 818.4),
    ("Minneapolis", 44.978, 3.92,  6.56, 2.47,  989, 884.4),
    ("Moscow",      55.756, 2.67,  5.47, 3.14,  766, 541.2),
]
names = [r[0] for r in DATA]
lat   = np.radians([r[1] for r in DATA])      # latitude in radians
ghi   = np.array([r[2] for r in DATA])
temp  = np.array([r[3] for r in DATA])
wind  = np.array([r[4] for r in DATA])
pv    = np.array([r[5] for r in DATA], dtype=float)
bess  = np.array([r[6] for r in DATA], dtype=float)

# Predictors defined in the paper
ghinh = 2 * ghi / (1 + np.cos(lat))           # half-cosine GHI, Eq. (4)
u     = 1 / np.cos(lat)                       # 1/cos(theta), used for BESS, Eq. (7)

i_moscow = names.index("Moscow")
no_moscow = [i for i in range(len(names)) if i != i_moscow]   # indices of the 11 other cities

# ------------------------------------------------------------ 2. HELPERS
def fit(x, y, deg):
    """Least-squares polynomial fit; returns coefficients (highest power first)."""
    return np.polyfit(x, y, deg)

def r_squared(y, y_hat):
    return 1 - ((y - y_hat) ** 2).sum() / ((y - y.mean()) ** 2).sum()

def pct_err(pred, true):
    """Signed percentage error (prediction minus truth, relative to truth)."""
    return (pred - true) / true * 100

def leave_one_out(x, y, deg, idx):
    """Leave-one-city-out: fit on all cities in idx except one, predict the one left out."""
    errs = {}
    for i in idx:
        train = [j for j in idx if j != i]
        coef = fit(x[train], y[train], deg)
        errs[names[i]] = pct_err(np.polyval(coef, x[i]), y[i])
    return errs

def mape(errs):
    return float(np.mean(np.abs(list(errs.values()))))

# ----------------------------------------- 3. PV: half-cosine GHI regression
print("=" * 64)
print("PV CAPACITY vs half-cosine GHI (Moscow excluded, as in the paper)")
coef_pv = fit(ghinh[no_moscow], pv[no_moscow], 1)
pv_hat  = np.polyval(coef_pv, ghinh[no_moscow])
print(f"  fit:  PV = {coef_pv[0]:.2f} * GHInh + {coef_pv[1]:.1f}   (paper Eq. 5: -157.04, 1675.1)")
print(f"  R2 = {r_squared(pv[no_moscow], pv_hat):.3f}   (paper: 0.946)")
print(f"  in-sample MAPE = {np.mean(np.abs(pct_err(pv_hat, pv[no_moscow]))):.1f} %")

loo_pv = leave_one_out(ghinh, pv, 1, no_moscow)
print(f"  leave-one-city-out MAPE = {mape(loo_pv):.1f} %  (11 cities)")
worst = max(loo_pv, key=lambda k: abs(loo_pv[k]))
print(f"  largest leave-one-out error: {worst} {loo_pv[worst]:+.1f} %")

moscow_pred = np.polyval(coef_pv, ghinh[i_moscow])
print(f"  Moscow predicted by the fit that excludes it: {pct_err(moscow_pred, pv[i_moscow]):+.1f} % vs HOMER")

coef_all = fit(ghinh, pv, 1)
r2_all = r_squared(pv, np.polyval(coef_all, ghinh))
print(f"  PV fit INCLUDING Moscow: R2 = {r2_all:.2f}")

# ------------------------------- 4. BESS: quadratic in 1/cos(theta) (Eq. 7)
print("=" * 64)
print("BESS CAPACITY vs 1/cos(theta), quadratic")
coef_b = fit(u, bess, 2)
r2_b = r_squared(bess, np.polyval(coef_b, u))
print(f"  all 12 cities: BESS = {coef_b[0]:.1f} u^2 + {coef_b[1]:.1f} u {coef_b[2]:+.2f}"
      f"   (paper Eq. 7: -823.71, 1810.4, -53.123)")
print(f"  R2 = {r2_b:.3f}   (paper: 0.91)")

coef_b11 = fit(u[no_moscow], bess[no_moscow], 2)
r2_b11 = r_squared(bess[no_moscow], np.polyval(coef_b11, u[no_moscow]))
print(f"  without Moscow: R2 = {r2_b11:.2f}")

loo_b = leave_one_out(u, bess, 2, list(range(len(names))))
print(f"  Moscow predicted when left out: {loo_b['Moscow']:+.1f} % vs HOMER")
print(f"  Atlanta predicted when left out: {loo_b['Atlanta']:+.1f} %")
spread = bess[no_moscow].std() / bess[no_moscow].mean() * 100
print(f"  BESS of the other 11 cities: std = {spread:.1f} % of their mean")

# ------------------- 5. Is Eq.(9)/(10) just a rescaled Eq.(6)/(8)?  (paper coefficients)
print("=" * 64)
print("RATIO OF PUBLISHED COEFFICIENTS (Eq. 9 vs 6, Eq. 10 vs 8)")
eq6 = np.array([-0.1294, 0.6909]);            eq9 = np.array([-0.1372, 0.7324])
eq8 = np.array([-1.554, 3.416, -0.100]);       eq10 = np.array([-1.186, 2.606, -0.0763])
print("  Eq.9 / Eq.6  :", np.round(eq9 / eq6, 3), "  -> same constant for both terms")
print("  Eq.10 / Eq.8 :", np.round(eq10 / eq8, 3), "  -> same constant for all three terms")

# ------------------------------------ 6. Do temperature / wind improve PV fit?
print("=" * 64)
print("EXTRA PREDICTORS FOR PV (11 cities, Moscow excluded)")
def multi_fit_loo(X, y):
    """Linear regression with intercept; returns (in-sample R2, leave-one-out MAPE)."""
    A = np.c_[np.ones(len(y)), X]
    c = np.linalg.lstsq(A, y, rcond=None)[0]
    r2 = r_squared(y, A @ c)
    errs = []
    for i in range(len(y)):
        k = [j for j in range(len(y)) if j != i]
        ck = np.linalg.lstsq(A[k], y[k], rcond=None)[0]
        errs.append(abs(pct_err(A[i] @ ck, y[i])))
    return r2, float(np.mean(errs))

y = pv[no_moscow]
g = ghinh[no_moscow]; T = temp[no_moscow]; W = wind[no_moscow]
for label, X in [("GHInh only", g[:, None]), ("GHInh + temp", np.c_[g, T]),
                 ("GHInh + wind", np.c_[g, W]), ("GHInh + temp + wind", np.c_[g, T, W])]:
    r2, lo = multi_fit_loo(X, y)
    print(f"  {label:<22s} R2 = {r2:.3f}   leave-one-out MAPE = {lo:.2f} %")

# --------------------------------------------- 7. Data-quality observations
print("=" * 64)
print("DATA OBSERVATIONS")
mult = bess / 13.2
print("  BESS / 13.2 kWh (all whole numbers?):", np.round(mult, 2).tolist())
print("  Cities with BESS = 937.2 kWh:", [n for n, b in zip(names, bess) if abs(b - 937.2) < 1e-6])
i_c, i_r = names.index("Cairo"), names.index("Riyadh")
same = (ghi[i_c], temp[i_c], wind[i_c]) == (ghi[i_r], temp[i_r], wind[i_r])
print("  Cairo and Riyadh have identical GHI, temperature and wind in Table I:", same)
