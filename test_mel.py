"""Mel (champions/Mel.md): numbers from build rls-19.1.0.5986094; the cast's length against the owner's 60 fps VOD6
(18-40-41-766, round 2-5: Mel)."""
import pytest

from buildstore import load_build
from set19champs import Mel
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'


def test_build_numbers():
    m = Mel(1, build=load_build(V))
    assert (m.fullMana.stat, m.aspd.stat, m.attack_range, m.hp.stat, m.num_missiles) == (40, 0.75, 4, 850, 30)
    # 'Fire' 0.5076 s + 30 x 0.04 s (OnFinished one interval after the 30th, T15) + CastAnimOut 'Unlock' 0.3214 s:
    # VOD6 E2 shows the banked overflow 63 ticks after the bar empties (62 + the tick after the fill)
    assert (round(m.timing.mana_lock * 30), round(m.timing.cast_lock * 30)) == (62, 63)
    assert m.missile_speed == 2100 and m.per_stack == pytest.approx(0.05 / 3)


def test_missiles_and_blues():
    m = Mel(1, build=load_build(V))
    casts, perform = [], m.performAbility

    def logged(o, i, t):
        casts.append(m.tick)
        perform(o, i, t)
    m.performAbility = logged
    ds = [dummy() for _ in range(3)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([], [], m, ds, 15)
    assert len(casts) >= 2
    # 3 of every 5 missiles on the target, the rest split over the other two: 18 / 6 / 6 per cast
    stacks = sorted(m.blues.get(id(d), 0) for d in ds)
    assert stacks == [6 * len(casts), 6 * len(casts), 18 * len(casts)]
    first = [round(d[0], 4) for t, d, *_ in m.dmgVector if d[1] == 'magical'][:1]
    assert first == [18]  # 18 x AP, no stacks yet
    # a missile on the target at the start of the 2nd cast: 18 stacks -> x (1 + 18 / 60)
    second = [d[0] for t, d, *_ in m.dmgVector if d[1] == 'magical' and round(t * 30) > casts[1]]
    assert any(d == pytest.approx(18 * (1 + 18 * 0.05 / 3)) for d in second[:3])
