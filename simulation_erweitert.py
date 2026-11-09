"""
Erweiterte Simulation (W-Seminar Poker)
1) Treffer-Wahrscheinlichkeit fuer verschiedene Outs-Zahlen (Flop und Turn)
2) Strategievergleich: Welche Call-Regel bringt am Flop den hoechsten Erwartungswert?
"""
import json
from math import comb
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
OUT = "/mnt/user-data/outputs/"
N = 1_000_000
P = 100  # Pot vor dem Gegner-Einsatz (Flop)


def treffer_flop(n_outs):
    """Zwei Karten (Turn, River) aus 47 unbekannten; Indizes 0..n_outs-1 sind Outs."""
    a = rng.integers(0, 47, N)
    b = rng.integers(0, 46, N)
    b = b + (b >= a)
    return (a < n_outs) | (b < n_outs)


def treffer_turn(n_outs):
    """Eine Karte (River) aus 46 unbekannten."""
    return rng.integers(0, 46, N) < n_outs


results = {"outs": [], "strategien": []}

print("=== Outs-Tabelle ===")
print(f"{'Outs':>5} {'Flop Theorie':>13} {'Flop Sim':>9} {'Turn Theorie':>13} {'Turn Sim':>9} {'Faustformel':>12}")
for n in [4, 8, 9, 12, 15]:
    p_th = 1 - comb(47 - n, 2) / comb(47, 2)
    p_sim = treffer_flop(n).mean()
    t_th = n / 46
    t_sim = treffer_turn(n).mean()
    print(f"{n:>5} {p_th*100:>12.2f}% {p_sim*100:>8.2f}% {t_th*100:>12.2f}% {t_sim*100:>8.2f}% {n*4:>11d}%")
    results["outs"].append({"n": n, "p_th": p_th, "p_sim": float(p_sim),
                            "t_th": t_th, "t_sim": float(t_sim)})

# ---------------------------------------------------------------- Strategievergleich
p = 1 - comb(38, 2) / comb(47, 2)
x_stern = p / (1 - 2 * p)
print(f"\nExaktes p = {p*100:.3f} %, x* = {x_stern*100:.1f} % des Pots -> {x_stern*P:.1f} EUR")

xs = np.array([0.25, 0.5, 0.75, 1.0, 1.5, 2.0])  # Gegner-Einsatz als Bruchteil des Pots
idx = rng.integers(0, len(xs), N)
x = xs[idx]
B = x * P
flush = treffer_flop(9)
gewinn_call = np.where(flush, P + B, -B)

strategien = {
    "Immer callen": np.ones(N, dtype=bool),
    "Nie callen (immer folden)": np.zeros(N, dtype=bool),
    "Nur bis 50 % des Pots callen": x <= 0.5,
    f"Unsere Regel (bis {x_stern*100:.0f} % des Pots)": x <= x_stern,
}

print("\n=== Strategievergleich (Gegner-Einsatz zufällig 25/50/75/100/150/200 % des Pots) ===")
print(f"{'Strategie':<38} {'Erwartungswert/Hand':>20} {'Theorie':>9} {'Calls':>7}")
labels, werte = [], []
for name, call in strategien.items():
    ev = np.where(call, gewinn_call, 0.0).mean()
    # Theorie: Mittel ueber die sechs Einsatzgroessen
    th = np.mean([(P * p - (1 - 2 * p) * xi * P) if (name == "Immer callen" or
                  (name.startswith("Nur bis 50") and xi <= 0.5) or
                  (name.startswith("Unsere") and xi <= x_stern)) else 0.0 for xi in xs])
    print(f"{name:<38} {ev:>18.2f} € {th:>8.2f}€ {call.mean()*100:>6.1f}%")
    results["strategien"].append({"name": name, "ev": float(ev), "th": float(th),
                                  "calls": float(call.mean())})
    labels.append(name)
    werte.append(ev)

plt.figure(figsize=(8, 4.5))
farben = ["#c0392b", "#7f8c8d", "#e67e22", "#27ae60"]
balken = plt.bar(range(len(labels)), werte, color=farben)
plt.xticks(range(len(labels)), ["Immer\ncallen", "Nie callen", "Nur bis 50 %\ndes Pots", "Unsere Regel"])
plt.axhline(0, color="black", linewidth=0.8)
plt.ylabel("Erwartungswert pro Hand in €")
plt.title("Strategievergleich am Flop (1 Mio. Hände)")
for b_, w in zip(balken, werte):
    plt.text(b_.get_x() + b_.get_width() / 2, w + (0.5 if w >= 0 else -1.5), f"{w:.2f} €", ha="center")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(OUT + "grafik_strategievergleich.png", dpi=200)
plt.close()

with open("/home/claude/results.json", "w") as f:
    json.dump(results, f, indent=1)
print("\nfertig")
