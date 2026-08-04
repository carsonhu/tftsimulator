"""Compare simulated Varus mana generation against a real replay clip.

Reference clip: 2026-08-03 15-07-58.mkv, ~t=232.6-240.8s. Varus (3-star,
Rapidfire trait level 2, Guinsoo's Rageblade + QSS) attacks a stationary
target starting at 30/120 mana and casts once mana hits 120.

Usage:
    python verify_varus_mana.py [--real-csv path/to/replay_mana.csv]
"""
import argparse

import set18buffs as buffs
import set18champs
import set18items as items

STARTING_MANA = 30
DURATION = 15
FRAME_TIME = 1 / 30


def build_champion():
    champ = set18champs.Varus(3)
    champ.curMana = STARTING_MANA
    champ.items.append(buffs.Rapidfire(2, 0))
    champ.items.append(items.GuinsoosRageblade())
    champ.items.append(items.QSS())
    return champ


def simulate_with_mana_log(champ, opponents, duration=DURATION):
    """Same loop as Simulator.simulate(), but logs curMana every time it
    changes instead of only at damage events, so it can be compared 1:1
    against the OCR'd replay mana curve.
    """
    all_items = champ.items
    champ.opponents = opponents
    for item in all_items:
        champ.addStats(item)
    for phase in ("prePreCombat", "preCombat", "postPreCombat"):
        for item in all_items:
            item.ability(phase, 0, champ)
    champ.onUpdateItems = [
        i for i in all_items if getattr(i, "phases", None) and "onUpdate" in i.phases
    ]
    for opp in opponents:
        opp.nextAttackTime = duration * 2
        opp.opponents = champ

    t = 0.0
    log = []
    last_mana = None
    while t < duration:
        champ.update(opponents, all_items, t)
        for opp in opponents:
            if opp.statuses and t >= opp.nextStatusUpdate:
                opp.updateStatuses(t)
        if champ.curMana != last_mana:
            log.append((t, champ.curMana, champ.aspd.stat))
            last_mana = champ.curMana
        t += FRAME_TIME
    return log


def attack_intervals(log, jump_threshold=5):
    """Timestamps/intervals of the >=jump_threshold mana jumps (attacks),
    filtering out the smaller regen-tick-only steps.
    """
    events = []
    prev_mana = log[0][1]
    for t, mana, _ in log[1:]:
        if mana < prev_mana:  # cast reset
            break
        if mana - prev_mana >= jump_threshold:
            events.append(t)
        prev_mana = mana
    return events, [b - a for a, b in zip(events, events[1:])]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--real-csv", default=None, help="optional replay_mana.csv to overlay in a plot")
    ap.add_argument("--plot-out", default="varus_mana_compare.png")
    args = ap.parse_args()

    champ = build_champion()
    opponent = set18champs.DummyTank(1)
    log = simulate_with_mana_log(champ, [opponent])

    events, intervals = attack_intervals(log)
    # find the actual cast (first frame mana reaches full)
    cast_time = None
    for t, mana, _ in log:
        if mana >= champ.fullMana.stat:
            cast_time = t
            break

    print("Simulated mana log (t, curMana, aspd):")
    for row in log:
        print(f"  {row[0]:.3f}  {row[1]:.1f}  aspd={row[2]:.3f}")
    print()
    print(f"Time to first cast (mana {STARTING_MANA} -> {champ.fullMana.stat}): "
          f"{cast_time:.2f}s" if cast_time else "No cast within duration")
    print(f"Attack-jump timestamps: {[round(e, 2) for e in events]}")
    print(f"Attack intervals: {[round(i, 2) for i in intervals]}")

    if args.real_csv:
        plot_comparison(log, args.real_csv, args.plot_out)


def plot_comparison(sim_log, real_csv_path, out_path):
    import csv
    import matplotlib.pyplot as plt

    with open(real_csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Real window: last frame still at 30 mana before the climb, through the
    # cast back to (near) 0. Hand-picked from the 2026-08-03 clip.
    real_pts = [
        (float(r["time_s"]), int(r["cur_mana"]))
        for r in rows
        if r["cur_mana"] and 232.6 <= float(r["time_s"]) <= 241.0
    ]
    t0 = real_pts[0][0]
    real_t = [t - t0 for t, _ in real_pts]
    real_m = [m for _, m in real_pts]

    sim_t = [t for t, _, _ in sim_log if t <= 8.5]
    sim_m = [m for t, m, _ in sim_log if t <= 8.5]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.step(real_t, real_m, where="post", marker=".", label="real replay (OCR)")
    ax.step(sim_t, sim_m, where="post", marker=".", label="simulator")
    ax.set_xlabel("time since combat start (s)")
    ax.set_ylabel("mana")
    ax.set_title("Varus mana: real replay vs simulator")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
