"""Samira end to end (champions/Samira.md): numbers from build rls-19.1.0.5973071; panel, mana and rhythm against the
owner's 60 fps PBE VOD3 (17-13-37-283, f19253-19772: Samira 1-star with Striker's Flail, Infinity Edge, Deathblade,
Renegade (2))."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from events import LAUNCH
from item import Item
from set19champs import Samira, Varus
from simulator import Simulator
from test_timing import dummy
from traits.classical import CAPTIVATED

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'
VOD_ITEMS = (set19items.StrikersFlail, set19items.InfinityEdge, set19items.Deathblade)


class LoggedSamira(Samira):
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


def fight(c, items=(), buffs=(), seconds=12, n=8, armor=0):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = armor
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return ds, [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_locks():
    s = LoggedSamira(1)
    assert (s.curMana, s.fullMana.stat, s.aspd.stat, s.attack_range, s.atk.stat) == (0, 60, 0.75, 4, 42)
    assert (round(s.timing.mana_lock * 30), round(s.timing.cast_lock * 30)) == (40, 41)
    assert s.begin_fire == 0.1962 and s.num_bullets == 10 and s.bullet_gap == pytest.approx(0.0374933)
    assert s.default_traits == ['Trickshot', 'Renegade', 'Classical']


def test_vod3_panel_mana_and_rhythm():
    # VOD3 panel: 700 HP, AD 85, crit 95%, AS 0.83; mana +7 per attack, +0.5 per regen step, attacks 37, 36 ticks
    # apart; the overflow shows 41.5 ticks after the filling attack (lock lifted at 41)
    s = LoggedSamira(1)
    fight(s, items=[i() for i in VOD_ITEMS], buffs=[set19buffs.Renegade(2)])
    assert (s.hp.stat, round(s.atk.stat * s.bonus_ad.stat), round(s.aspd.stat, 2)) == (700, 85, 0.83)
    assert s.crit.stat == pytest.approx(0.95) and s.canSpellCrit
    assert {round(after - before, 3) for t, a, before, after in s.mana_log if after > before} == {0.5, 7}
    attacks = [t for t, a, before, after in s.mana_log if a == 7]
    assert set([b - a for a, b in zip(attacks, attacks[1:])][:5]) == {36, 37}
    fill = next(t for t, a, before, after in s.mana_log if a == 7 and after >= 60)
    cast = s.casts[0]
    assert cast == fill + 1
    assert next(t for t, a, before, after in s.mana_log if t > cast and after > before) >= cast + 40
    # the attack after the cast: engine 50 ticks after the filling attack; VOD3 showed 54.5 (open question)
    assert next(t for t in attacks if t > fill) - fill == 50


def test_barrage():
    # 10 bullets of 4 x AP + 35 x AD (39 at 1-star), from BeginFire (6 ticks) every 0.0375 s, 1500 units/s over 4 hexes
    s = LoggedSamira(1)
    ds, rows = fight(s, seconds=10)
    cast = s.casts[0]
    bullets = [t - cast for t, d in rows if t > cast and d == 39]
    assert len(bullets) == 10 and bullets[0] == 6 + 18 and bullets[-1] - bullets[0] == 10
    # one simulated launch per cast (GE_SimulateLaunchAttack behind a DoOnce), at the first bullet
    s, counter = LoggedSamira(1), LaunchCounter()
    fight(s, items=[counter], seconds=10)
    assert s.casts[0] + 6 in counter.launches and len(counter.launches) == s.launches + len(s.casts)


def test_bullets_ricochet_with_trickshot():
    s = LoggedSamira(1)
    ds, rows = fight(s, buffs=[set19buffs.Trickshot(2)], seconds=10)
    cast = s.casts[0]
    assert [d for t, d in rows if t > cast].count(pytest.approx(39 * 0.22)) == 10


def test_renegade():
    for level, crit, crit_dmg in ((2, 0.15, 0.12), (5, 0.35, 0.25)):
        s = LoggedSamira(1)
        Simulator().itemStats([set19buffs.Renegade(level)] + s.items, s)
        assert (s.crit.stat, s.critDmg.stat, s.canSpellCrit) == (pytest.approx(0.25 + crit),
                                                                 pytest.approx(1.4 + crit_dmg), True)
    v = Varus(1, build=load_build(V))
    Simulator().itemStats([set19buffs.Renegade(2)] + v.items, v)
    assert v.crit.stat == pytest.approx(0.25) and not v.canSpellCrit  # not a Renegade


def test_classical_captivate_and_amp():
    # Classical (2): 8% amp; each crit Captivates its target for 3 s; while an enemy is Captivated every 0.25 s
    # (the first at once) adds 0.25 x 1% / 6 to every Classical unit's amp, for the rest of combat
    s = LoggedSamira(1)
    ds, rows = fight(s, items=[set19items.InfinityEdge()], buffs=[set19buffs.Classical(2)], seconds=12)
    grown = s.dmgMultiplier.stat - 1 - 0.08
    per_tick = 0.25 * 0.01 / 6
    assert grown > 0 and (grown / per_tick) == pytest.approx(round(grown / per_tick))
    assert grown / per_tick <= 12 / 0.25 + 1  # never more than one target Captivated at a time here
    assert CAPTIVATED in ds[0].effects
    # without Classical active, no Captivate
    s = LoggedSamira(1)
    ds, rows = fight(s, items=[set19items.InfinityEdge()], seconds=6)
    assert all(CAPTIVATED not in d.effects for d in ds) and s.dmgMultiplier.stat == pytest.approx(1)
