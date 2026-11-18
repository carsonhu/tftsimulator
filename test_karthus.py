"""Karthus end to end (champions/Karthus.md): numbers from build rls-19.1.0.5973071; mana, locks and rhythm against the
owner's 60 fps PBE VOD3 (17-13-37-283, f21643-22148: Karthus 1-star, no items)."""
import pytest

import set19buffs
from buildstore import load_build
from set19champs import Karthus
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedKarthus(Karthus):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.mana_log, self.casts = [], []

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        self.mana_log.append((self.tick, amount, before, self.curMana))

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(c, items=(), buffs=(), seconds=12, mr=0):
    ds = [dummy() for _ in range(8)]
    for d in ds:
        d.armor.base, d.mr.base = 0, mr
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_locks():
    k = LoggedKarthus(1)
    assert (k.curMana, k.fullMana.stat, k.aspd.stat, k.attack_range, k.atk.stat) == (10, 50, 0.75, 4, 30)
    # CD_Karthus19_CastAnim: Damage 1.1269 s, Unlock 1.337 s -> mana lock 41 ticks, cast lock 42
    assert k.damage_at == 1.1269 and (round(k.timing.mana_lock * 30), round(k.timing.cast_lock * 30)) == (41, 42)
    assert k.default_traits == ['Arcanist', 'Pentakill']


def test_vod3_mana_locks_and_rhythm():
    # VOD3: start 10 mana, attacks +7 and 40 ticks apart (f21712, 21793, 21873, 21954, 22034), regen +0.5 a step;
    # the bar fills at f22034; the next attack pays 57 ticks later (f22148): cast + cast lock 42 + a 14-tick windup
    k = LoggedKarthus(1)
    fight(k)
    attacks = [t for t, a, before, after in k.mana_log if a == 7]
    cast = k.casts[0]
    fill = cast - 1  # a full bar casts the next tick (T4)
    before_cast = [t for t in attacks if t < cast]
    assert set(b - a for a, b in zip(before_cast, before_cast[1:])) <= {40, 41}
    assert {round(after - before, 3) for t, a, before, after in k.mana_log if after > before} == {0.5, 7}
    assert next(t for t in attacks if t > fill) - fill == 57
    # mana lock: nothing is gained until 41 ticks after the cast starts
    assert all(after == before for t, a, before, after in k.mana_log if cast <= t < cast + 41)


def test_requiem():
    # 440 x AP magic on the target, 34 ticks after the cast starts (Damage 1.1269 s); Arcanist (2) member +25% AP
    k = LoggedKarthus(1)
    rows = fight(k, seconds=10)
    assert [(t - k.casts[0], d) for t, d in rows if d > 100][:1] == [(34, 440)]
    k = LoggedKarthus(1)
    rows = fight(k, buffs=[set19buffs.Arcanist(2)], seconds=10)
    assert [d for t, d in rows if d > 100][:1] == [pytest.approx(440 * 1.25)]
