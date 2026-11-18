"""Malzahar end to end (champions/Malzahar.md): numbers from build rls-19.1.0.5973071; mana and mana lock against the
owner's 60 fps PBE VOD3 (17-13-37-283, f24365-24869: Malzahar 1-star with Striker's Flail, Infinity Edge and Spear
of Shojin)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from layout import Layout
from set19champs import Malzahar, Varus
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedMalzahar(Malzahar):
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


def fight(c, items=(), buffs=(), seconds=10, mr=0, layout=None):
    ds = [dummy() for _ in range((layout or Layout()).count)]
    for d in ds:
        d.armor.base, d.mr.base = 0, mr
    Simulator().simulate(list(items), list(buffs), c, ds, seconds, layout=layout)
    return ds, [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_spell_timeline():
    m = LoggedMalzahar(1)
    assert (m.curMana, m.fullMana.stat, m.aspd.stat, m.attack_range) == (0, 50, 0.8, 4)
    # CD_Malzahar19_CastAnim_new: BeginBeam 0.3523 s and 3 Bursts; Unlock 2.4688 s (the build's 75 / 76 ticks)
    assert m.bursts == [0.3523, 0.9923, 1.6323, 2.2723] and m.beam_ticks == 9
    assert (round(m.timing.mana_lock * 30), round(m.timing.cast_lock * 30)) == (75, 76)
    assert m.default_traits == ['Prodigy', 'Composer']


def test_vod3_mana_and_lock():
    # VOD3 mana text: regen +0.75 a step (2 + 1 Shojin = 3/s), attacks +12 (7 + 5), attacks 34 ticks apart at AS 0.88
    # (0.8 x 1.1, Flail); the overflow shows 151 frames (75.5 ticks) after the filling attack
    m = LoggedMalzahar(1)
    fight(m, items=[set19items.StrikersFlail(), set19items.InfinityEdge(), set19items.SpearOfShojin()])
    assert m.hp.stat == 950 and round(m.aspd.stat, 2) == 0.88 and m.crit.stat == pytest.approx(0.8)
    steps = {round(after - before, 3) for t, a, before, after in m.mana_log if after > before}
    assert steps == {0.75, 12}
    attacks = [t for t, a, before, after in m.mana_log if a == 12]
    assert [b - a for a, b in zip(attacks, attacks[1:])][:3] == [34, 34, 34]
    cast = m.casts[0]
    regen_after = next(t for t, a, before, after in m.mana_log if t > cast and after > before)
    assert cast + 75 <= regen_after <= cast + 75 + 8  # mana flows again once the 75-tick lock is over


def test_beam_and_bursts():
    # 1-star at AP 1.0 on 0-MR dummies: 4 bursts of 40 on the 2 targets (cast + 11, 30, 49, 69 ticks),
    # 9 beam ticks of 380 / 9 on the target from cast + 11, every 0.25 s
    m = LoggedMalzahar(1)
    ds, rows = fight(m, seconds=12)
    cast = m.casts[0]
    spell = [(t - cast, d) for t, d in rows if t >= cast and d != round(35 * 1.1, 4)]
    bursts = sorted(t for t, d in spell if d == 40)
    assert bursts == [11] * 2 + [30] * 2 + [49] * 2 + [69] * 2
    beam = [t for t, d in spell if d == pytest.approx(380 / 9)]
    assert beam == [11, 19, 26, 34, 41, 49, 56, 64, 71]
    # the shred: 30% for 4 s on everyone a burst hits (MR x 0.7): with 2 targets, the target and its neighbour, not
    # the one 2 hexes behind
    m = LoggedMalzahar(1)
    ds, rows = fight(m, seconds=7.5, mr=100, layout=Layout(2))
    assert [d.mr.stat for d in ds] == [70, 70, 100]


def test_bursts_hit_every_neighbour():
    m = LoggedMalzahar(1)
    ds, rows = fight(m, seconds=8, layout=Layout(4))
    cast = m.casts[0]
    assert [d for t, d in rows if t == cast + 30].count(40) == 4


def test_composer():
    # 3% AP per instrument for the team, Malzahar double (GE_Malzahar19_TeamwideAP + _MalzaharAP)
    for n in (0, 2, 5):
        m = LoggedMalzahar(1)
        Simulator().itemStats([set19buffs.Composer(1, n)] + m.items, m)
        assert m.ap.stat == pytest.approx(1 + 0.06 * n)
        v = Varus(1, build=load_build(V))
        Simulator().itemStats([set19buffs.Composer(1, n)] + v.items, v)
        assert v.ap.stat == pytest.approx(1 + 0.03 * n)


def test_vod5_cast_lock():
    # VOD5 (0-57-11-500, f21295 combat start): Blue Buff + Quicksilver, AS 0.92; the attack that fills the bar, then
    # the next attack's mana 90.5 ticks later (cast 1 tick after the fill, cast lock 76, then the windup): engine 91
    m = LoggedMalzahar(1)
    fight(m, items=[set19items.BlueBuff(), set19items.Quicksilver()], seconds=7)
    assert m.manaRegen.stat == 8  # 2 + 6 (Blue Buff), the panel's 8/s
    attacks = [t for t, a, before, after in m.mana_log if a == 7]
    fill = next(t for t, a, before, after in m.mana_log if a == 7 and after >= 50)
    assert m.casts[0] == fill + 1
    assert next(t for t in attacks if t > fill) - fill == 91
