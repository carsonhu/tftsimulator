"""Jinx (champions/Jinx.md): numbers from build rls-19.1.0.5986094; the missile count and damage against the owner's
60 fps VOD6 (18-40-41-766, round 2-7: Jinx's tooltip, 17 missiles of 68 at AS 1.04)."""
import pytest

from buildstore import load_build
from set19champs import Jinx
from simulator import Simulator
from test_timing import dummy
from test_viego import LaunchCounter

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'


def test_missile_count_and_tooltip():
    j = Jinx(1, build=load_build(V))
    assert (j.fullMana.stat, j.curMana, j.aspd.stat, j.attack_range) == (90, 30, 0.8, 4)
    assert j.num_missiles() == 16
    # VOD6 E1: AS 1.04 (+30%) -> "17 = 16 + 1 per 35% bonus"; AD 142%, AP 120% -> 68 per missile
    j.aspd.modify('MultiplyAdditive', 1.3)
    assert j.num_missiles() == 17
    assert j.missile_damage(1, 1.42, 1.2) == pytest.approx(68.26)
    plan = j.plan(17)
    # Round(17 x 0.75 / 0.15 / 0.1) = 13 / 3 / 2, cut to 17: the last 'Other' goes
    assert (plan.count('AATarget'), plan.count('NHexRange'), plan.count('Other')) == (13, 3, 1)
    assert (round(j.timing.mana_lock * 30), round(j.timing.cast_lock * 30)) == (67, 68)


def test_cast():
    j = Jinx(1, build=load_build(V))
    casts, perform = [], j.performAbility

    def logged(o, i, t):
        casts.append(j.tick)
        perform(o, i, t)
    j.performAbility = logged
    counter = LaunchCounter()
    ds = [dummy() for _ in range(3)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([counter], [], j, ds, 12)
    cast = casts[0]
    rockets = [(round(t * 30) - cast, round(d[0], 4)) for t, d, *_ in j.dmgVector
               if cast < round(t * 30) < cast + 70 and round(d[0], 4) == 49]
    assert len(rockets) == 16  # 43 x AD + 6 x AP, no armor
    # the first leaves at 'BeginFiring' (17 ticks), the last 1.2 s later; a simulated launch every 5
    assert len([t for t in counter.launches if cast < t < cast + 60]) == 3
