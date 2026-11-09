"""
Simulation der Flush-Draw-Situation (W-Seminar Poker)

Situation: Hand K♥ Q♥, Flop 2♥ 7♥ A♠ -> 47 unbekannte Karten, davon 9 Herzkarten (Outs).
Modellannahme: Der Spieler gewinnt genau dann, wenn bis zum River eine Herzkarte kommt.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
OUT = "/mnt/user-data/outputs/"

P_EXAKT = 1 - (38 / 47) * (37 / 46)  # theoretische Flush-Wahrscheinlichkeit


def austeilen(n):
    """Zieht n-mal Turn und River (zwei verschiedene Karten aus 47). Index 0-8 = Herzkarten."""
    a = rng.integers(0, 47, n)
    b = rng.integers(0, 46, n)
    b = b + (b >= a)  # garantiert b != a
    return (a < 9) | (b < 9)


N = 1_000_000
flush = austeilen(N)

# ---------------------------------------------------------------- 1. Konvergenz
print("=== 1. Relative Häufigkeit des Flushs ===")
print(f"Theorie: {P_EXAKT*100:.2f} %")
ns = [50, 500, 5_000, 50_000, 500_000, 1_000_000]
for n in ns:
    print(f"n = {n:>9,}: {flush[:n].mean()*100:6.2f} %   (Abweichung {abs(flush[:n].mean()-P_EXAKT)*100:5.2f} Prozentpunkte)")

# Spieleabend: 50 Versuche, 10.000-mal wiederholt
reps = np.array([austeilen(50).mean() for _ in range(10_000)])
print("\n=== Spieleabend mit 50 Versuchen (10.000 Wiederholungen) ===")
print(f"Mittelwert {reps.mean()*100:.1f} %, Standardabweichung {reps.std()*100:.1f} Prozentpunkte")
print(f"Mittlere 95 % der Ergebnisse: {np.percentile(reps,2.5)*100:.0f} % bis {np.percentile(reps,97.5)*100:.0f} %")
print(f"Theoretische Standardabweichung: {np.sqrt(P_EXAKT*(1-P_EXAKT)/50)*100:.1f} Prozentpunkte")

# ---------------------------------------------------------------- 2. Call am Flop
print("\n=== 2. Erwartungswert des Calls am Flop (Pot 100 €) ===")
print(f"{'Einsatz':>8} {'Simulation':>11} {'Theorie':>9}")
einsaetze = [20, 50, 80, 100, 120, 150]
sim_ev, th_ev = [], []
for B in einsaetze:
    gewinn = np.where(flush, 100 + B, -B)
    th = P_EXAKT * (100 + B) - (1 - P_EXAKT) * B
    sim_ev.append(gewinn.mean()); th_ev.append(th)
    print(f"{B:>6} € {gewinn.mean():>10.2f}€ {th:>8.2f}€")
g50 = np.where(flush, 150, -50)
print(f"\nCall bei 50 €: Standardabweichung Simulation {g50.std():.1f} €, Theorie "
      f"{np.sqrt(P_EXAKT*(150-(P_EXAKT*150-(1-P_EXAKT)*50))**2 + (1-P_EXAKT)*(-50-(P_EXAKT*150-(1-P_EXAKT)*50))**2):.1f} €")

# ---------------------------------------------------------------- 3. Bluff-Raise am River
print("\n=== 3. Bluff-Raise am River (Pot 200 €, Raise auf 2B, Gegner foldet mit f = 30 %) ===")
f = 0.30
print(f"{'B':>5} {'Raise':>6} {'f*':>7} {'EV Sim':>9} {'EV Theorie':>11}")
for B in [20, 40, 60, 80, 100, 150, 200]:
    R = 2 * B
    folds = rng.random(N) < f
    gewinn = np.where(folds, 200 + B, -R)
    th = f * (200 + B) - (1 - f) * R
    fstern = R / (200 + B + R)
    print(f"{B:>3} € {R:>4} € {fstern*100:>6.1f}% {gewinn.mean():>8.2f}€ {th:>10.2f}€")

# ---------------------------------------------------------------- 4. GTO-Modell am River
print("\n=== 4. GTO-River-Modell (Pot 200 €, Bet 100 €) ===")
P, S = 200, 100
q_star = P_EXAKT * (S / (P + S)) / (1 - P_EXAKT)
print(f"Theoretische GTO-Bluffquote unter den Nieten: {q_star*100:.1f} %")
print(f"{'Bluffquote q':>13} {'Bluff-Anteil b':>15} {'EV Call des Gegners':>20}")
for q in [0.0, 0.10, q_star, 0.30, 0.50]:
    bluff = (~flush) & (rng.random(N) < q)
    bet = flush | bluff
    if bet.sum() == 0:
        print(f"{q*100:>12.1f}% {'-':>15} {'-':>20}")
        continue
    b = bluff.sum() / bet.sum()
    ev_call = np.where(flush[bet], -S, P + S).mean()
    print(f"{q*100:>12.1f}% {b*100:>14.1f}% {ev_call:>18.2f} €")
print("\nEV eines Bluffs in Abhängigkeit der Call-Quote c des Gegners:")
for c in [0.50, 2 / 3, 0.80]:
    calls = rng.random(N) < c
    ev = np.where(calls, -S, P).mean()
    print(f"c = {c*100:5.1f} %: EV Bluff = {ev:7.2f} €")

# ---------------------------------------------------------------- Grafiken
# Grafik 1: Konvergenz
laufend = np.cumsum(flush) / np.arange(1, N + 1)
idx = np.unique(np.logspace(1, np.log10(N), 400).astype(int)) - 1
plt.figure(figsize=(8, 4.5))
plt.semilogx(idx + 1, laufend[idx] * 100, label="Simulation (relative Häufigkeit)")
plt.axhline(P_EXAKT * 100, color="red", linestyle="--", label=f"Theorie: {P_EXAKT*100:.1f} %")
plt.xlabel("Anzahl der simulierten Hände")
plt.ylabel("Anteil Flush in %")
plt.title("Konvergenz der Flush-Häufigkeit")
plt.ylim(20, 50)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(OUT + "grafik_konvergenz.png", dpi=200)
plt.close()

# Grafik 2: EV des Calls
bs = np.linspace(0, 200, 201)
plt.figure(figsize=(8, 4.5))
plt.plot(bs, P_EXAKT * (100 + bs) - (1 - P_EXAKT) * bs, label="Theorie")
plt.scatter(einsaetze, sim_ev, color="orange", zorder=3, label="Simulation (1 Mio. Hände)")
plt.axhline(0, color="black", linewidth=0.8)
b_be = 100 * P_EXAKT / (1 - 2 * P_EXAKT)
plt.axvline(b_be, color="red", linestyle="--", label=f"Break-even ≈ {b_be:.0f} €")
plt.xlabel("Einsatz des Gegners am Flop in €")
plt.ylabel("Erwartungswert des Calls in €")
plt.title("Erwartungswert des Calls in Abhängigkeit vom Gegner-Einsatz")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(OUT + "grafik_erwartungswert_call.png", dpi=200)
plt.close()
print("\nGrafiken gespeichert.")
