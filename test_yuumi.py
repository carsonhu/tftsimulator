"""Yuumi (champions/Yuumi.md): numbers from build rls-19.1.0.5986094; the mana lock against the owner's 60 fps VOD6
(18-40-41-766, rounds 1-8 and 1-9: Yuumi 1 star)."""
import pytest

import set19buffs
from buildstore import load_build
from set19champs import Yuumi
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'


def fight(buffs=(), seconds=22, level=1):
    y = Yuumi(level, build=load_build(V))
    ds = [dummy() for _ in range(3)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([], list(buffs), y, ds, seconds)
    return y, [(round(t * 30), round(d[0], 4)) for t, d, *_ in y.dmgVector if d[1] == 'magical']


def test_build_numbers():
    y = Yuumi(1, build=load_build(V))
    assert (y.fullMana.stat, y.aspd.stat, y.attack_range, y.hp.stat) == (20, 0.75, 4, 850)
    # VOD6 E2: the banked overflow shows 62-63 frames (31-31.5 ticks) after the bar empties: 'Unlock' 30 + the tick
    # after the fill
    assert (round(y.timing.mana_lock * 30), round(y.timing.cast_lock * 30)) == (30, 31)
    assert (y.disk_at, y.encore_at, y.self_bounce) == (0.365, 0.4615, 18)


def test_discs_and_topple():
    y, rows = fight()
    discs = [d for _, d in rows]
    assert discs[:5] == [175] * 5
    # the 5th disc topples: 0.4 x 5 discs to the target, 0.4 / 4 x 5 to each of the others (2 here)
    assert sorted(discs[5:8]) == [87.5, 87.5, 350]
    assert rows[7][0] - rows[4][0] == 18  # the self-bounce, 0.5997 s


def test_encore_discs():
    # with Encore every cast adds a disc at RecastEffectiveness, which counts toward the 5 at that proportion
    y, rows = fight(buffs=[set19buffs.Encore(2)])
    e = y.encore_effectiveness()
    assert 0 < e < 1
    assert rows[1] == (rows[0][0] + 3, pytest.approx(175 * e))
    main = max(d for _, d in rows[:10])
    assert main == pytest.approx(0.4 * (3 + 2 * e) * 175)
