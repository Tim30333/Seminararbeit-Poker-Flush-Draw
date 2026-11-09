"""
Realistische Simulation (W-Seminar Poker)
Wir geben dem Gegner echte Hände und vergleichen die Blätter am Showdown mit einem Pokerblatt-Auswerter.
So pruefen wir, wie weit das Modell "Wir gewinnen nur mit Flush" von der Realitaet abweicht.

Spieler: K♥ Q♥, Flop: 2♥ 7♥ A♠, Turn und River zufaellig.
Gegnertypen:
  A) zufaellige Hand
  B) Hand mit einem Ass (A♥, A♦ oder A♣ plus beliebige Karte) -> entspricht unserer Modellannahme
"""
import json
import random
import eval7

random.seed(2026)
N = 300_000

hero = [eval7.Card("Kh"), eval7.Card("Qh")]
flop = [eval7.Card("2h"), eval7.Card("7h"), eval7.Card("As")]
bekannt = set(map(str, hero + flop))
rest = [c for c in eval7.Deck().cards if str(c) not in bekannt]
assert len(rest) == 47
asse = [c for c in rest if str(c)[0] == "A"]  # Ah, Ad, Ac


def simuliere(typ):
    sieg_flush = sieg_ohne = verl_flush = verl_ohne = remis = 0
    flush_total = 0
    for _ in range(N):
        deck = rest[:]
        if typ == "ass":
            a = random.choice(asse)
            deck.remove(a)
            b = random.choice(deck)
            deck.remove(b)
            opp = [a, b]
        else:
            opp = random.sample(deck, 2)
            for c in opp:
                deck.remove(c)
        turn_river = random.sample(deck, 2)
        board = flop + turn_river
        h = eval7.evaluate(hero + board)
        o = eval7.evaluate(opp + board)
        hat_flush = eval7.handtype(h) in ("Flush", "Straight Flush")
        flush_total += hat_flush
        if h > o:
            if hat_flush: sieg_flush += 1
            else: sieg_ohne += 1
        elif h < o:
            if hat_flush: verl_flush += 1
            else: verl_ohne += 1
        else:
            remis += 1
    return {
        "flush_kommt": flush_total / N,
        "sieg_mit_flush": sieg_flush / N,
        "sieg_ohne_flush": sieg_ohne / N,
        "verlust_trotz_flush": verl_flush / N,
        "verlust_ohne_flush": verl_ohne / N,
        "remis": remis / N,
        "equity": (sieg_flush + sieg_ohne + remis / 2) / N,
    }


res = {}
for typ, name in [("zufall", "Zufällige Gegnerhand"), ("ass", "Gegner hält ein Ass")]:
    r = simuliere(typ)
    res[typ] = r
    print(f"\n=== {name} ({N:,} Durchläufe) ===")
    for k, v in r.items():
        print(f"{k:<22} {v*100:6.2f} %")

# Erwartungswert des Calls (Pot 100, Gegner setzt 50) mit echter Gewinnchance
P, B = 100, 50
for typ in ("zufall", "ass"):
    e = res[typ]["equity"]
    ev = e * (P + B) - (1 - e) * B
    xs = e / (1 - 2 * e) if e < 0.5 else None
    res[typ]["ev_call50"] = ev
    res[typ]["x_stern"] = xs
    print(f"{typ}: E(Call 50) = {ev:.2f} EUR, x* = {xs}")

json.dump(res, open("/home/claude/results_real.json", "w"), indent=1)
