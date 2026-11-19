"""Katarina (champions/Katarina.md): numbers from build rls-19.1.0.5986094; mana and attack rhythm against the owner's
60 fps VOD6 (18-40-41-766, round 1-2: Katarina 1 star, no items)."""
import pytest

import set19buffs
from buildstore import load_build
from set19champs import Katarina
from simulator import Simulator
from traits.classical import CAPTIVATED
from test_timing import dummy

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'


class LoggedKatarina(Katarina):
    def __init__(self, level=1, build=V):
        super().__init__(level, build=load_build(build))
        self.casts = []

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(c, buffs=(), seconds=8, n=3):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([], list(buffs), c, ds, seconds)
    return ds, [(round(t * 30), round(d[0], 4), d[1]) for t, d, *_ in c.dmgVector]


def test_build_numbers():
    k = LoggedKatarina(1)
    assert (k.curMana, k.fullMana.stat, k.aspd.stat, k.attack_range, k.atk.stat, k.hp.stat) == (0, 40, 0.75, 1, 30, 650)
    # the NoMovement group: 'Eviscerate' 0.835 s, 'Unlock' 1.2743 s (39 / 40 ticks)
    assert (k.spin_at, k.eviscerate_at) == (0, 0.835)
    assert (round(k.timing.mana_lock * 30), round(k.timing.cast_lock * 30)) == (39, 40)


def test_cast_spin_and_eviscerate():
    # VOD6 E2: +10 per attack, no regen, attacks 38 ticks apart at 0.79 AS (stage 1 Fighter), the cast on the 4th
    k = LoggedKatarina(1)
    _, rows = fight(k)
    cast = k.casts[0]
    attacks = [t for t, d, kind in rows if kind == 'physical' and t < cast]
    assert len(attacks) == 4 and {b - a for a, b in zip(attacks, attacks[1:])} == {38}
    assert cast == attacks[-1] + 1  # the bar fills on the 4th hit; the cast is the next tick (T4)
    # the spin on the cast tick: her target and the enemy next to it (G22); the eviscerate 25 ticks later
    assert [(t - cast, d) for t, d, kind in rows if kind == 'magical'] == [(0, 120), (0, 120), (25, 240)]
    # the next attack lands after the 40-tick cast lock and the windup
    assert min(t for t, d, kind in rows if kind == 'physical' and t > cast) - cast == 49


def test_captivate_with_classical():
    # every enemy hit is Captivated for 5 s when Classical is active
    k = LoggedKatarina(2)
    ds, _ = fight(k, buffs=[set19buffs.Classical(2)], seconds=5)
    assert [CAPTIVATED in d.effects for d in ds] == [True, True, False]
    k = LoggedKatarina(2)
    ds, _ = fight(k, seconds=5)
    assert not any(CAPTIVATED in d.effects for d in ds)
    assert k.row('TargetDamageAP') == pytest.approx(360)
