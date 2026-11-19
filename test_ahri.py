"""Ahri (champions/Ahri.md): numbers from build rls-19.1.0.5986094; the three cast lengths against the owner's 60 fps
VOD6 (18-40-41-766, round 2-8: basic casts, the one that reaches 14 fox-fires, then the flow)."""
import collections

from buildstore import load_build
from set19champs import Ahri
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'


def fight(seconds=25):
    a = Ahri(1, build=load_build(V))
    casts, perform = [], a.performAbility

    def logged(o, i, t):
        casts.append((a.tick, a.fox))
        perform(o, i, t)
        locks.append((round(a.timing.mana_lock * 30), round(a.timing.cast_lock * 30)))
    locks = []
    a.performAbility = logged
    ds = [dummy() for _ in range(3)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([], [], a, ds, seconds)
    return a, casts, locks


def test_cast_lengths():
    # VOD6 E2: the banked overflow 31 ticks after a basic cast, 54 after the one that reaches 14 (+ the pose), 30
    # after an empowered one (each the lock + the tick after the fill)
    a, casts, locks = fight()
    assert [n for _, n in casts[:5]] == [6, 8, 10, 12, 14]
    assert locks[:5] == [(30, 31), (30, 31), (30, 31), (53, 54), (29, 30)]


def test_damage():
    a, casts, _ = fight()
    by_cast = []
    for (t0, n), (t1, _) in zip(casts, casts[1:] + [(10 ** 9, 0)]):
        by_cast.append(collections.Counter(round(d[0], 4) for t, d, *_ in a.dmgVector
                                           if t0 <= round(t * 30) < t1 and d[1] == 'magical'))
    assert by_cast[0] == {28: 6}  # 6 fox-fires of 28 x AP
    assert by_cast[4] == {28: 14, 235: 1}  # the flow: the heart and 14 fox-fires
