"""Kayle end to end (champions/Kayle.md): numbers from build rls-19.1.0.5973071; the cast's cycle against the owner's
60 fps PBE VOD5 (0-57-11-500, f39525-40104: Kayle 1-star with Quicksilver and two Blue Buffs, Pentakill (5))."""
import pytest

import set19items
from buildstore import load_build
from set19champs import Kayle
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedKayle(Kayle):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.mana_log, self.casts, self.releases, self.sword_counts = [], [], [], []

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        self.mana_log.append((self.tick, amount, before, self.curMana))

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)

    def onLaunch(self, opponents, items):
        super().onLaunch(opponents, items)
        self.releases.append(self.tick)


def fight(c, items=(), buffs=(), seconds=12, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_timeline():
    k = LoggedKayle(1)
    assert (k.curMana, k.fullMana.stat, k.aspd.stat, k.attack_range, k.atk.stat) == (0, 50, 0.8, 4, 10)
    assert (k.buff_at, k.begin_unlock, k.begin_len, k.big_hit, k.finale_unlock, k.aoe) == (
        0.1324, 0.4929, 0.5, 1.048, 1.4532, 2)
    assert k.timing.proj_speed == 2250 and not k.timing.lock_scales_with_as
    assert sorted(k.default_traits) == ['Pentakill', 'Swiftstriker']


def test_vod5_cycle():
    # VOD5: regen 12/s (two Blue Buffs), +10 per attack; the mana lock ends 183.5 ticks after the attack that fills
    # the bar (engine 181: cast +1, Buff 4, 4.375 s of buff, the 1.4532 s finale); the buff is +80% (0.94 -> 1.58)
    k = LoggedKayle(1)
    fight(k, items=[set19items.Quicksilver(), set19items.BlueBuff(), set19items.BlueBuff()])
    attacks = [t for t, a, before, after in k.mana_log if a == 10 and after > before and t > 0]
    cast = k.casts[0]
    fill = max(t for t in attacks if t < cast)
    assert cast == fill + 1
    during = [t for t in k.releases if cast < t < cast + 140]
    assert len(during) == 6  # attacks during the buff: no mana (locked), one sword each
    lift = next(t for t, a, before, after in k.mana_log if t > cast and after > before)
    assert 181 <= lift - fill <= 188  # the lift at 181, the first regen step after it at 188


def test_finale_damage():
    # the finale: 180 x AP to the target and every enemy within 2 hexes at BigHit, then one 37 x AP sword per attack
    # made during the buff on the target, 0.1 s apart; the passive adds 40 x AP magic to every attack
    k = LoggedKayle(1)
    k.curMana = 50
    rows = fight(k, seconds=8)
    cast = k.casts[0]
    swords = [t for t in k.releases if cast < t < cast + 140]
    blast = [(t, d) for t, d in rows if d == 180]
    assert len(blast) == 3  # the target and the two dummies within 2 hexes on the default layout
    t0 = blast[0][0]
    assert [t for t, d in rows if d == 37] == [t0 + 3 * i for i in range(1, len(swords) + 1)]
    assert sum(1 for t, d in rows if d == 40) == len(k.releases) - sum(1 for t in k.releases if t > rows[-1][0] - 1)
