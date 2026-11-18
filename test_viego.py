"""Viego, Slayer and Choreographer (champions/Viego.md): numbers from build rls-19.1.0.5973071; rhythm against the
owner's 60 fps PBE VOD5 (0-57-11-500, f24670-25300: Viego 1-star with Quicksilver and Blue Buff; f33360: 2-star with
Slayer (2) at 504/1530 Health)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from events import LAUNCH
from item import Item
from set19champs import Ashe, Viego
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedViego(Viego):
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


class LaunchCounter(Item):
    LISTENS = {LAUNCH: frozenset()}

    def __init__(self):
        super().__init__("LaunchCounter")
        self.launches = []

    def performAbility(self, phase, time, champion, input_=0):
        self.launches.append(champion.tick)
        return input_


def fight(c, items=(), buffs=(), seconds=10, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_spell_timeline():
    v = LoggedViego(1)
    assert (v.curMana, v.fullMana.stat, v.aspd.stat, v.attack_range, v.atk.stat) == (0, 40, 0.8, 1, 60)
    assert (v.fire_at, v.collapse, v.num_swords) == (1.0579, 0.25, 10)
    assert (round(v.timing.mana_lock * 30), round(v.timing.cast_lock * 30)) == (55, 56)
    assert v.default_traits == ['Pentakill', 'Slayer', 'Choreographer']


def test_vod5_cast_rhythm():
    # VOD5: Quicksilver + Blue Buff (regen 6/s, AS 0.96 at stage 1); the attack after a cast pays 65 ticks after the
    # cast starts (cast lock 56, then a fresh 9-tick windup); the next two 29.5 and 28 later (engine 29, 28)
    v = LoggedViego(1)
    fight(v, items=[set19items.Quicksilver(), set19items.BlueBuff()])
    attacks = [t for t, a, before, after in v.mana_log if a == 10 and after > before and t > 0]
    cast = v.casts[0]
    after = [t for t in attacks if t > cast]
    assert after[0] - cast == 65 and [b - a for a, b in zip(after, after[1:])][:2] == [29, 28]
    assert next(t for t, a, before, after_ in v.mana_log if t > cast and after_ > before) >= cast + 55


def test_swords_and_simulated_launch():
    # 10 swords of 36 x AD + 3 x AP at 1 star (the AD row scales AD: owner, 2026-11-18), 32 + 8 ticks after the
    # cast; one simulated attack launch per cast, at FireSwords
    v, counter = LoggedViego(1), LaunchCounter()
    rows = fight(v, items=[counter])
    cast = v.casts[0]
    assert [d for t, d in rows if t == cast + 40] == [39] * 10
    fired = sum(1 for c in v.casts if c + 32 < 300)  # casts whose swords fire within the 10 s
    assert cast + 32 in counter.launches and len(counter.launches) == v.launches + fired
    v2 = LoggedViego(2)
    v2.ap.modify("+", 0.5)
    rows = fight(v2, seconds=8)
    assert [d for t, d in rows if t == v2.casts[0] + 40] == [pytest.approx(54 + 5 * 1.5)] * 10
    v3 = LoggedViego(2)
    v3.bonus_ad.modify("+", 0.5)
    rows = fight(v3, seconds=8)
    assert [d for t, d in rows if t == v3.casts[0] + 40] == [pytest.approx(54 * 1.5 + 5)] * 10


def test_slayer_and_choreographer():
    # Slayer (2): +20% attack speed at full Health (dummies never hit back); VOD5 at 504/1530 showed 1.11 = 0.8 x
    # (1.05 + 0.2 x 1.67), the missing-Health scaling the simulator never needs
    v = LoggedViego(1)
    fight(v, buffs=[set19buffs.Slayer(2)], seconds=1)
    assert v.aspd.stat == pytest.approx(0.8 * (1.05 + 0.2))
    # Choreographer (2): back-row allies +6% damage amp, Choreographers double; 'By range' puts melee in the front
    for params, amp in ((0, 0), (1, 0), (2, 0.12)):
        v = LoggedViego(1)
        fight(v, buffs=[set19buffs.Choreographer(2, params)], seconds=1)
        assert v.dmgMultiplier.stat == pytest.approx(1 + amp)
    a = Ashe(1, build=load_build(V))  # not a Choreographer, range 5: back row by range, single amp
    fight(a, buffs=[set19buffs.Choreographer(2)], seconds=1)
    assert a.dmgMultiplier.stat == pytest.approx(1.06)
