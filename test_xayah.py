"""Xayah and Gu Feng (champions/Xayah.md, ledger B35): numbers from build rls-19.1.0.5986094 (Xayah's data is the same
in 5973071); rhythm against the owner's 60 fps PBE VOD4 (19-0-51-650, round 1-10 and 2-1: Xayah 1 star with Infinity
Edge, Quicksilver and Guinsoo's Rageblade, Hitmaker (2) Big Shot)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from events import LAUNCH
from set19champs import Xayah
from simulator import Simulator
from test_timing import dummy
from test_viego import LaunchCounter

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'
VOD_ITEMS = (set19items.Quicksilver, set19items.GuinsoosRageblade, set19items.InfinityEdge)


class LoggedXayah(Xayah):
    def __init__(self, level=1, build=V):
        super().__init__(level, build=load_build(build))
        self.mana_log, self.casts = [], []

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        self.mana_log.append((self.tick, amount, before, self.curMana))

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(c, items=(), buffs=(), seconds=10, n=3):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_feathers():
    x = LoggedXayah(1)
    assert (x.curMana, x.fullMana.stat, x.aspd.stat, x.attack_range, x.atk.stat, x.hp.stat) == (0, 60, 0.75, 4, 55, 850)
    assert (round(x.timing.mana_lock * 30), round(x.timing.cast_lock * 30)) == (64, 65)
    assert x.wave_events == (0.2466, 0.6989) and x.feather_speed == 3200
    f = x.feathers(4)
    assert len(f) == 30
    # wave 1: StartFeathers + k x 0.8 / 30, wait 0.88 s; wave 2: MoreFeathers + k x 0.8 / 30, wait 0.4 s
    assert f[0][2] == pytest.approx(0.2466 + 0.88) and f[15][2] == pytest.approx(0.6989 + 0.4)
    assert f[14][2] - f[0][2] == pytest.approx(14 * 0.8 / 30)
    # the first wave-1 feather sits 100 units to her side: it flies sqrt(860^2 + 100^2)
    assert f[0][0] - f[0][2] == pytest.approx((860 ** 2 + 100 ** 2) ** 0.5 / 3200)
    assert 1.36 < min(t for t, _, _ in f) and max(t for t, _, _ in f) < 1.78
    assert len(LoggedXayah(3).feathers(4)) == 60


def test_feather_damage_and_simulated_launch():
    # 30 feathers on the target, each 20 x AD + 3 x AP at 1 star, 42-53 ticks into the cast at 4 hexes; one simulated
    # attack launch per cast, at StartFeathers (tick 8)
    x, counter = LoggedXayah(1), LaunchCounter()
    rows = fight(x, items=[counter], seconds=12)
    cast = x.casts[0]
    feathers = [(t - cast, d) for t, d in rows if cast < t <= cast + 60 and d == pytest.approx(23)]
    assert len(feathers) == 30 and min(t for t, _ in feathers) == 42 and max(t for t, _ in feathers) == 53
    assert cast + 8 in counter.launches
    x2 = LoggedXayah(2)
    x2.bonus_ad.modify("+", 0.5)
    x2.ap.modify("+", 0.2)
    rows = fight(x2, seconds=12)
    c2 = x2.casts[0]
    assert sorted(d for t, d in rows if c2 + 40 < t <= c2 + 55) == [pytest.approx(30 * 1.5 + 5 * 1.2)] * 30


def test_vod4_panel_and_cast_rhythm():
    # VOD4 19:16 panel: AP 110%, AS 0.94, crit 80%, MR 60; AD 95 there, 91.85 here without the board's Illbeats (2)
    # (owner: 3 AD decibels at half strength for a non-member = 5.1% -> 94.7, E1)
    x = LoggedXayah(1)
    fight(x, items=[c() for c in VOD_ITEMS], buffs=[set19buffs.Hitmaker(2, 1)], seconds=20)
    assert x.casts
    # the attack after a cast pays 71.5 / 72.5 / 70 ticks after the bar empties (E3-E5); engine 72
    for cast in x.casts[:2]:
        after = [t for t, a, before, now in x.mana_log if t > cast and a == 7 and now > before]
        assert after[0] - cast == 72
    # the tooltip's 38 per feather: 20 x 1.72 + 3 x 1.10 = 37.7 in game; 20 x 1.67 + 3 x 1.1 = 36.7 here
    assert x.feather_damage(1, x.bonus_ad.stat, x.ap.stat) == pytest.approx(36.7)

    s = LoggedXayah(1)
    fight(s, items=[c() for c in VOD_ITEMS], buffs=[set19buffs.Hitmaker(2, 1)], seconds=0.04)
    assert (s.ap.stat, round(s.aspd.stat, 4), s.crit.stat, s.mr.stat, s.armor.stat) == (
        pytest.approx(1.1), 0.9375, pytest.approx(0.8), 60, 40)
    assert s.bonus_ad.stat == pytest.approx(1.67)


def test_gu_feng():
    # (2): +2% AD and AP, +2 Armor and MR per player level (default 8); (3) adds 2% max Health per level
    x = LoggedXayah(1)
    fight(x, buffs=[set19buffs.GuFeng(2)], seconds=0.04)
    assert (x.bonus_ad.stat, x.ap.stat, x.armor.stat, x.mr.stat, x.hp.stat) == (
        pytest.approx(1.16), pytest.approx(1.16), 56, 56, 850)
    x = LoggedXayah(1)
    fight(x, buffs=[set19buffs.GuFeng(3, 5)], seconds=0.04)
    assert (x.bonus_ad.stat, x.armor.stat, x.hp.stat) == (pytest.approx(1.10), 50, pytest.approx(850 * 1.10))
    x = LoggedXayah(1)
    fight(x, buffs=[set19buffs.GuFeng(0)], seconds=0.04)
    assert (x.bonus_ad.stat, x.armor.stat) == (1, 40)
    assert set19buffs.GuFeng.levels == [0, 2, 3, 4]


def test_feather_waits_from_the_build():
    # CD_Xayah19_SpellMis: wave 1's missile (no tag) waits 0.88 s, wave 2's (MissileSelector.1) 0.4 s: the projectile
    # modules' Delay, in the build since the 2026-11-18 refresh (no longer typed in)
    assert LoggedXayah(1).wave_delay == (0.88, 0.4)
