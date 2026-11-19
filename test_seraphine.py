"""Seraphine and her forms (champions/SeraphineIndie.md): numbers from build rls-19.1.0.5986094; the mana lock against
the owner's 60 fps VOD6 (18-40-41-766, round 1-6: Seraphine 1 star, Indie)."""
import collections

import pytest

from buildstore import load_build
from set19champs import Seraphine, SeraphineRisingStar, SeraphineSuperstar
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'


def logged(cls, level=1):
    class Logged(cls):
        def performAbility(self, opponents, items, time):
            self.casts.append(self.tick)
            super().performAbility(opponents, items, time)
    c = Logged(level, build=load_build(V))
    c.casts = []
    return c


def cast_hits(cls, level=1, n=3):
    c = logged(cls, level)
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([], [], c, ds, 14)
    cast = c.casts[0]
    nxt = c.casts[1] if len(c.casts) > 1 else 10 ** 9
    return c, cast, [(round(t * 30) - cast, round(d[0], 4)) for t, d, *_ in c.dmgVector
                     if cast <= round(t * 30) < min(nxt, cast + 120) and d[1] == 'magical']


def test_build_numbers():
    s = logged(Seraphine)
    assert (s.fullMana.stat, s.aspd.stat, s.attack_range, s.hp.stat) == (50, 0.75, 4, 700)
    # VOD6 E2: the banked 2 mana shows 82 ticks after the bar empties (81 + the tick after the fill)
    assert (round(s.timing.mana_lock * 30), round(s.timing.cast_lock * 30)) == (81, 82)
    assert (s.num_fires, s.note_divisor, s.bonus_volleys) == (15, 30, (4, 4))


def test_indie_stream():
    s, cast, hits = cast_hits(Seraphine)
    # 30 notes at the target, each 570 x AP / 30; the first fire at 'BeginFire' (9 ticks) + the flight over 4 hexes
    assert len(hits) == 30 and all(d == pytest.approx(570 / 30) for _, d in hits)
    # the last: fire 15's right note leaves at 0.2997 + 14 x 0.15 + 0.075 = 2.4747 s (tick 75), lands 14 ticks later
    assert hits[0][0] == 9 + 14 and hits[-1][0] == 75 + 14


def test_rising_star_and_superstar():
    _, _, hits = cast_hits(SeraphineRisingStar)
    c = collections.Counter(round(d, 2) for _, d in hits)
    assert c[round(570 / 30, 2)] == 30 and c[20] == 8  # 4 + 4 bonus notes at ExtraNoteDamageAP
    _, _, hits = cast_hits(SeraphineSuperstar)
    c = collections.Counter(round(d, 2) for _, d in hits)
    assert c[60] == 3 and c[20] == 8  # a high note at each of the 3 dummies
    assert SeraphineSuperstar.display_name == 'Seraphine (Superstar)'
