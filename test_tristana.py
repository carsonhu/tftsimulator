"""Tristana (champions/Tristana.md): numbers from build rls-19.1.0.5986094; the cast's length against the owner's 60 fps
VOD6 (18-40-41-766, round 2-3: Tristana 2 stars)."""
import pytest

from buildstore import load_build
from set19champs import Tristana
from simulator import Simulator
from test_timing import dummy
from test_viego import LaunchCounter

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'


def test_build_numbers():
    t = Tristana(2, build=load_build(V))
    assert (t.fullMana.stat, t.aspd.stat, t.attack_range, t.hp.stat) == (55, 0.75, 4, 990)
    # Part1 'Unlock' 17 ticks, then shots at rate 1.25, 1.25, 1: 'Unlock' 0.6386 s / rate = 16, 16, 20 ticks
    assert t.shot_starts == [17, 33, 49]
    # VOD6 E2: the banked overflow shows 70 / 70.5 / 70 ticks after the bar empties (69 + the tick after the fill)
    assert (round(t.timing.mana_lock * 30), round(t.timing.cast_lock * 30)) == (69, 70)


def test_bombs():
    t = Tristana(1, build=load_build(V))
    casts, perform = [], t.performAbility

    def logged(o, i, tm):
        casts.append(t.tick)
        perform(o, i, tm)
    t.performAbility = logged
    counter = LaunchCounter()
    ds = [dummy() for _ in range(3)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([counter], [], t, ds, 12)
    cast = casts[0]
    hits = [(round(tm * 30) - cast, round(d[0], 4)) for tm, d, *_ in t.dmgVector
            if cast + 20 < round(tm * 30) <= cast + 90 and d[0] > 100]
    # two detonations of 125 x AD + 15 x AP, then the big one at 2x
    assert [d for _, d in hits] == [pytest.approx(140), pytest.approx(140), pytest.approx(280)]
    assert hits[0][0] < hits[1][0] < hits[2][0] <= 69 + 15
    assert any(cast + 60 < x <= cast + 90 for x in counter.launches)  # the last detonation's simulated launch
