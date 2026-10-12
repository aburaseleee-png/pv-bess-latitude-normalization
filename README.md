# PV-BESS Latitude Normalization — Reproduction and Extension

**Applicant:** Md. Abu Rasel  
**Target Laboratory:** Matsuo Laboratory, Shizuoka University  
**Proposed Advisor:** Associate Prof. Hironobu Matsuo  

---

## Purpose

This repository contains a Python reproduction of the published PV–BESS sizing framework by Matsuo & Pandey (IEEE PREE 2025), using only the latitude, GHI, and HOMER capacities published in their Table I and Table III (12 cities).

**This is a reproduction and feasibility check, not a claim of novelty.**  
New results are expected only from the proposed HOMER study.

---

## Data

All data used here are from the published paper:

- **Table I:** City latitude, GHI, temperature, wind speed
- **Table III:** HOMER-estimated PV and BESS capacities for 12 cities

No HOMER simulation was run. All "HOMER" values below are the capacities published in the paper.

---

## Results

| Check | Result |
| :--- | :--- |
| PV fit on half-cosine GHI, Moscow excluded (11 cities) | R² = 0.947 (published: 0.946); in-sample MAPE 3.0% |
| PV, leave-one-city-out | MAPE 3.8%; largest error 6.7% (Winnipeg) |
| Moscow predicted from the PV fit that excludes it | about +49% above HOMER |
| BESS quadratic in 1/cosθ, all 12 cities | R² = 0.915 (published: 0.91) |
| BESS fit without Moscow | R² about 0.64 |
| BESS, Moscow predicted when left out | about +34% above HOMER |
| Eq. (9) vs Eq. (6); Eq. (10) vs Eq. (8) | coefficient ratios 1.06 and 0.763 (each constant across all terms) |

---

## Key Observations

### PV

The half-cosine rule predicts new cities well up to about 50° (leave-one-out MAPE 3.8%), but not beyond: Moscow is predicted about 49% too high.

### BESS

R² = 0.91 depends strongly on Moscow; the other 11 cities differ by only about 5% in BESS capacity, so the curve is largely shaped by one point.

### Eqs. (9) and (10)

They appear to be Eqs. (6) and (8) multiplied by one constant, so that they match the equatorial rule at θ = 0. This would imply the same latitude dependence for every load profile, which the proposal would like to test with rural-type night-time shares.

### Temperature and wind

Adding the Table I temperature or wind to the PV fit did not improve leave-one-out error (3.8% rises to 4.1–4.7%).

---

## Limitations

- Only 12 published points
- HOMER BESS values are multiples of 13.2 kWh and five cities share 937.2 kWh, so part of the BESS variation may reflect the search grid
- A HOMER-based study with more sites and rural load profiles is proposed to settle these questions

---

## Files

