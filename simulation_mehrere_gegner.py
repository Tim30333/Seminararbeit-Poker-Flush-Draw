"""
Simulation: Flush Draw gegen m Gegner (W-Seminar Poker)
Annahme: Jeder der m Gegner hat B in den Pot gezahlt. Wir gewinnen genau dann, wenn der Flush kommt.
Theorie: E = P*p - (1 - (m+1)*p) * B
"""
import json
from math import comb
import numpy as np

rng = np.random.default_rng(11)
N = 1_000_000
P = 100
p = 1 - comb(38, 2) / comb(47, 2)

a = rng.integers(0, 47, N)
b = rng.integers(0, 46, N)
b = b + (b >= a)
flush = (a < 9) | (b < 9)

out = {"ev": [], "fold": []}
print("=== Erwartungswert des Calls gegen m Gegner (Pot 100 €) ===")
print(f"{'m':>2} {'B':>5} {'Simulation':>11} {'Theorie':>9}")
for m in (1, 2, 3):
    for B in (50, 100):
        sim = np.where(flush, P + m * B, -B).mean()
        th = P * p - (1 - (m + 1) * p) * B
        print(f"{m:>2} {B:>4}€ {sim:>10.2f}€ {th:>8.2f}€")
        out["ev"].append({"m": m, "B": B, "sim": float(sim), "th": float(th)})

f = 0.30
print("\n=== Alle m Gegner folden (je 30 %, unabhängig) ===")
for m in (1, 2, 3):
    alle = (rng.random((N, m)) < f).all(axis=1).mean()
    print(f"m = {m}: Simulation {alle*100:.2f} %, Theorie {f**m*100:.2f} %")
    out["fold"].append({"m": m, "sim": float(alle), "th": f ** m})

json.dump(out, open("/home/claude/results_multi.json", "w"), indent=1)
