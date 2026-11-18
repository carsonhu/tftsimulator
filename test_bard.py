"""Bard (champions/Bard.md): numbers from build rls-19.1.0.5973071; the wave from GA_Bard19_Spell and
GE_Bard19_MeepWaveDamage (client asset)."""
import pytest

from buildstore import load_build
from layout import Layout
from set19champs import Bard
from simulator import Simulator
from test_timing import dummy
from timing import TPS

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


def fight(layout=None, seconds=10):
    b = Bard(1, build=load_build(V))
    ds = [dummy() for _ in range((layout or Layout()).count)]
    for d in ds:
        d.mr.base = 0  # the wave's magic damage as dealt
    Simulator().simulate([], [], b, ds, seconds, layout=layout)
    spells = [(round(t * TPS), round(dmg[0], 6)) for t, dmg, *_ in b.dmgVector if dmg[1] == 'magical']
    return b, ds, spells


def test_cast_locks_follow_the_wave_cast():
    # CD_Bard19_CastAnimMeeps 'Unlock' 0.8402 s -> 26 ticks: mana lock 26, next attack 27 (not the horn's CastAnim)
    b = Bard(1, build=load_build(V))
    assert round(b.timing.mana_lock * TPS) == 26 and round(b.timing.cast_lock * TPS) == 27


def test_wave_falloff_and_timing():
    # 20 mana + 10 per attack (MagicMarksman): releases 6, 46, ..., 206 -> 80 -> cast at 207. FireMeeps 0.4381 s ->
    # 221. The wave starts half a hex behind Bard at 1000 units/s: the target (4 hexes) after (107.5 + 860) / 1000 s
    # = 29 ticks (250); the default 2 targets and the enemy 2 hexes behind stand in a line (layout.py), each a hex
    # further along (257, 263). Each hit 210 x AP x falloff (1, 0.7, 0.49) in two halves 3 ticks apart.
    b, ds, spells = fight()
    assert sorted(spells[:6]) == [(250, 105.0), (253, 105.0), (257, 73.5), (260, 73.5), (263, 51.45), (266, 51.45)]


def test_wave_meets_the_number_of_targets():
    # a line meets every enemy on it: the default 2 targets and the one 2 hexes behind, 6 halves from the first cast
    b, ds, spells = fight()
    assert len([s for s in spells if s[0] < 300]) == 6
    # one target: the target and the one 2 hexes behind, in the line (the spare dummy is out of play)
    b, ds, spells = fight(Layout(1))
    assert spells == [(250, 105.0), (253, 105.0), (263, 73.5), (266, 73.5)]  # one cast in 10 s


def test_falloff_floor():
    # 1, 0.7, 0.49, 0.343, 0.2401, then 0.2 (MinimumDamagePercent) for the rest: 7 targets, the 6 next to the target
    # all within the 600-wide line (centres at most 186 units off it)
    b, ds, spells = fight(Layout(7), seconds=9)
    halves = sorted({v for _, v in spells}, reverse=True)
    assert halves[:3] == [105.0, 73.5, 51.45] and min(halves) == pytest.approx(105 * 0.2)
