"""Renata Glasc (champions/RenataGlasc.md): numbers from build rls-19.1.0.5973071; the cast's locks against the owner's
60 fps PBE VOD2 (16-35-16-966, f22888-23387: Renata 1-star with Guinsoo's Rageblade and Blue Buff)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from set19champs import RenataGlasc
from simulator import Simulator
from test_timing import dummy
from traits.classical import CAPTIVATED
from layout import Layout

# the layout these numbers were taken on: the target and 2 enemies behind it, in a line (the old default, before
# the page's targets became every enemy in play, owner 2026-11-19)
OLD_LINE = Layout(3, "line")


V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedRenata(RenataGlasc):
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


def fight(c, items=(), buffs=(), seconds=10, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds, layout=OLD_LINE)
    return ds, [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_locks():
    r = LoggedRenata(1)
    assert (r.curMana, r.fullMana.stat, r.aspd.stat, r.attack_range) == (0, 45, 0.75, 4)
    assert (r.launch, r.end_unlock, r.period, r.toxin_ticks) == (0.1974, 0.6578, 0.25, 60)
    assert sorted(r.default_traits) == ['Choreographer', 'Classical']


def test_vod2_locks():
    # VOD2: both casts filled by regen; the overflow shows 42 and 41.5 ticks after the filling step: cast 1 tick
    # later, LaunchChains 6, the chain's 15-tick flight (4 hexes at 1800), SpellEnd's Unlock 20 -> 42 after the fill;
    # the next attack's mana 53.5 after it (engine 53)
    r = LoggedRenata(1)
    fight(r, items=[set19items.GuinsoosRageblade(), set19items.BlueBuff()])
    cast = r.casts[0]
    assert round(r.timing.mana_lock * 30) == 41 and round(r.timing.cast_lock * 30) == 42
    lift = next(t for t, a, before, after in r.mana_log if t > cast and after > before)
    assert cast + 41 <= lift <= cast + 49  # the lock ends at +41; the first regen step after it
    attack = next(t for t, a, before, after in r.mana_log if t > cast and a == 7 and after > before)
    assert attack - (cast - 1) == 53


def test_toxin_and_captivate():
    # 2 stacks on the target, 1 on each of 2 others; each stack 160 x AP over 15 s in 60 ticks; Captivates with Classical
    r = LoggedRenata(1)
    r.curMana = 45
    ds, rows = fight(r, buffs=[set19buffs.Classical(2)], seconds=20)
    cast = r.casts[0]
    amp = 1.08  # Classical (2), before its Captivate growth
    first = [(t, d) for t, d in rows if t > cast]
    assert first[0][1] == pytest.approx(2 * 160 * amp / 60, rel=0.01)
    r2 = LoggedRenata(1)
    r2.curMana = 45
    ds2, rows2 = fight(r2, buffs=[set19buffs.Classical(2)], seconds=2)
    hit = [d for d in ds2 if CAPTIVATED in d.effects]
    assert len(hit) == 3  # the target and the 2 secondary targets
    # one cast, no Classical: no Captivate, and the toxin's total is 4 stacks x 160 x AP over its 60 ticks
    r3 = OneCast(1)
    r3.curMana = 45
    ds3, rows3 = fight(r3, seconds=17)
    assert all(CAPTIVATED not in d.effects for d in ds3)
    toxin = [d for t, d in rows3 if t > r3.casts[0] and d < 10]
    assert len(toxin) == 3 * 60 and sum(toxin) == pytest.approx(4 * 160, rel=1e-4)  # rows are rounded


class OneCast(LoggedRenata):
    def canCast(self, time=None):
        return not self.casts and super().canCast(time)
