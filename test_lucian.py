"""Lucian and Jazz (champions/Lucian.md): numbers from build rls-19.1.0.5973071; the cast's rhythm against the owner's
30 fps PBE VOD1 (15-16-17-933, f10347-10760: Lucian 1-star with Nashor's Tooth and Guinsoo's Rageblade, Tocker's
Trials)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from events import LAUNCH
from item import Item
from set19champs import Lucian
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedLucian(Lucian):
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


def test_build_numbers():
    c = LoggedLucian(1)
    assert (c.curMana, c.fullMana.stat, c.aspd.stat, c.attack_range, c.atk.stat) == (0, 20, 0.75, 4, 30)
    assert (c.dash_hexes, c.dash) == (1, 4)  # 1 hex x 215 units at 2000 units/s
    assert sorted(c.default_traits) == ['Encore', 'Hitmaker', 'Jazz']


def test_vod1_cast_rhythm():
    # VOD1: +9 per attack (7 + Nashor's 2); after each cast the overflow shows 37-39 ticks after the filling attack,
    # the next attack 46 after it. Engine: lock 32 ticks from the cast (4-tick dash + Unlock 28), the next attack 41:
    # the clip's dashes took ~4 ticks longer (open)
    c = LoggedLucian(1)
    fight(c, items=[set19items.NashorsTooth(), set19items.GuinsoosRageblade()])
    gains = [t for t, a, before, after in c.mana_log if after - before == 9]
    for cast in c.casts[:3]:
        fill = max(t for t in gains if t < cast)
        assert cast == fill + 1 and next(t for t in gains if t > cast) - fill == 41


def test_shots_and_encore():
    # 2 shots of 80 x AD + 8 x AP, each a simulated attack launch; with Encore (2): 2 more at RecastEffectiveness
    c, counter = LoggedLucian(1), LaunchCounter()
    c.curMana = 20
    rows = fight(c, items=[counter], seconds=3)
    cast = c.casts[0]
    assert [d for t, d in rows if t > cast and d == 88] == [88, 88]
    assert len([t for t in counter.launches if t > cast]) >= 2
    e = LoggedLucian(1)
    e.curMana = 20
    rows = fight(e, buffs=[set19buffs.Encore(2)], seconds=3)
    eff = e.trait_value('DA_Encore19', 'RecastEffectiveness')
    shots = sorted(d for t, d in rows if e.casts[0] < t < e.casts[0] + 40)  # the cast's 4 shots
    assert shots == pytest.approx(sorted([88, 88, 88 * eff, 88 * eff]))
    assert round(e.timing.cast_lock * 30) == 4 + 25 + 1  # CD_Lucian19_CastAnim_Encore Unlock 0.8029 s


def test_jazz():
    # Jazz (2): +1% damage amp per active non-unique trait, for the whole team (the count is the parameter)
    for n in (1, 5, 9):
        c = LoggedLucian(1)
        fight(c, buffs=[set19buffs.Jazz(2, n)], seconds=1)
        assert c.dmgMultiplier.stat == pytest.approx(1 + 0.01 * n)
