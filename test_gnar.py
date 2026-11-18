"""Gnar end to end (champions/Gnar.md): numbers from build rls-19.1.0.5973071; Ammo, attack speed and launch rhythm
against the owner's 60 fps PBE VOD3 (17-13-37-283, f15620-16359: Gnar 2-star with Infinity Edge + Striker's Flail)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from set19champs import Gnar
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedGnar(Gnar):
    def __init__(self, level=2):
        super().__init__(level, build=load_build(V))
        self.releases, self.as_after = [], []

    def onLaunch(self, opponents, items):
        super().onLaunch(opponents, items)
        self.releases.append(self.tick)
        self.as_after.append(round(self.aspd.stat, 3))


def fight(c, items=(), buffs=(), seconds=12, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_animations():
    g = LoggedGnar(2)
    assert (g.aspd.stat, g.attack_range, g.atk.stat, g.fullMana.stat) == (0.7, 4, 60, 3)
    # SequentialAttack: LaunchAttack 0.2678 s of 1.9667 s; SpecialAttack (every 3rd): CustomLaunchAttack1 0.38 of 1.2333
    assert [(v['launch'], v['length']) for v in g.timing.variants] == [(0.2678, 1.9667)] * 2 + [(0.38, 1.2333)]
    assert g.rock_speed == 1800 and g.default_traits == ['Trickshot', 'Pentakill']


def test_vod3_rhythm_and_attack_speed():
    # VOD3 Ammo text 1/3, 2/3, 3/3 (the rock), ... at f15728, 15805, 15892, 15958, 16030, 16108, 16171, (16269: a
    # walk), 16341: gaps 38.5, 43.5, 33, 36, 39, 31.5 ticks; AS 0.77 -> 0.83 -> 0.90 -> 0.96 at each 3/3
    g = LoggedGnar(2)
    fight(g, items=[set19items.InfinityEdge(), set19items.StrikersFlail()])
    assert g.hp.stat == 1050 and g.crit.stat == pytest.approx(0.8)  # VOD3 panel: 1050 HP, 80% crit
    assert g.as_after[0] == 0.77  # 0.7 x 1.1 (Striker's Flail)
    gaps = [b - a for a, b in zip(g.releases, g.releases[1:])][:6]
    assert all(abs(e - v) <= 1.5 for e, v in zip(gaps, [38.5, 43.5, 33, 36, 39, 31.5]))
    assert [round(a, 2) for a in g.as_after[2:9:3]] == [0.83, 0.9, 0.96]


def test_rock_every_third_attack():
    # attacks 60 x 1.1 (average crit 25% x 1.4); the rock 180 x AD, no crit without Precision, replacing the attack
    g = LoggedGnar(2)
    rows = fight(g, seconds=8)
    assert [d for t, d in rows][:6] == [66, 66, 180, 66, 66, 180]
    # with Infinity Edge (Precision): the rock crits too, and AD +35% scales it
    g = LoggedGnar(2)
    rows = fight(g, items=[set19items.InfinityEdge()], seconds=4)
    crit = 0.25 + 0.35
    rock = 180 * 1.35 * (1 + crit * (g.critDmg.stat - 1))
    assert [d for t, d in rows][2] == pytest.approx(rock, abs=1e-3)


def test_rock_ricochets_with_trickshot():
    # Trickshot (2): the rock ricochets once at 22% (its own handler, CD_Gnar19_Projectile_TrickshotBounce 1800 over
    # 1 hex = 4 ticks); the generic attack ricochet does not also fire on it
    g = LoggedGnar(2)
    rows = fight(g, buffs=[set19buffs.Trickshot(2)], seconds=4)
    rock_at = next(t for t, d in rows if d == 180)
    assert [d for t, d in rows if t == rock_at + 4] == [pytest.approx(180 * 0.22)]
    assert [d for t, d in rows].count(pytest.approx(66 * 0.22)) == 2  # the two attacks before it


def test_pentakill():
    # GE_Pentakill19_Stats on members: AD and AP + 15/30/35%
    assert set19buffs.Pentakill.levels == [0, 3, 5, 7]
    for level, v in ((3, 0.15), (5, 0.3), (7, 0.35)):
        g = LoggedGnar(1)
        Simulator().itemStats([set19buffs.Pentakill(level)] + g.items, g)
        assert (g.bonus_ad.stat, g.ap.stat) == (pytest.approx(1 + v), pytest.approx(1 + v))
