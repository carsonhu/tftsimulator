"""Qiyana (champions/Qiyana.md): numbers from build rls-19.1.0.5986094; the cast rhythm against the owner's 60 fps VOD6
(18-40-41-766, round 1-5: Qiyana 2 stars, three Blue casts)."""
import pytest

from buildstore import load_build
from set19champs import Qiyana
from simulator import Simulator
from test_timing import dummy
from test_viego import LaunchCounter

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'


class LoggedQiyana(Qiyana):
    def __init__(self, level=1, build=V):
        super().__init__(level, build=load_build(build))
        self.casts, self.mana_log = [], []

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(c, items=(), seconds=8, n=3):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), [], c, ds, seconds)
    return [(round(t * 30), round(d[0], 4), mana) for t, d, _, mana, _ in c.dmgVector]


def test_build_numbers():
    q = LoggedQiyana(2)
    assert (q.fullMana.stat, q.aspd.stat, q.attack_range, q.atk.stat, q.hp.stat) == (40, 0.8, 1, 67.5, 1350)
    # CD_Qiyana19_CastAnimNoMove: 'ManaUnlock' 0.8491 s, 'Unlock' 1.0912 s; the wave at 0.3779 s, 1200 units/s
    assert (round(q.timing.mana_lock * 30), round(q.timing.cast_lock * 30)) == (26, 34)
    assert (q.wave_spawn, q.wave_speed) == (0.3779, 1200)
    # the ring (owner, Q17): Red from combat start, then Green, Blue, Red ... every TimeRingChange (1.5 s, 45 ticks)
    assert [q.ring_colour(t) for t in (0, 44, 45, 90, 134, 135)] == ['Red', 'Red', 'Green', 'Blue', 'Blue', 'Red']


def test_wave_and_rhythm():
    q, counter = LoggedQiyana(2), LaunchCounter()
    rows = fight(q, items=[counter])
    cast = q.casts[0]
    assert [q.ring_colour(c) for c in q.casts[:2]] == ['Blue', 'Blue']  # ticks 117, 232
    hit = 290 + 45
    assert q.wave_damage(2, 1, 1, 'Red') == pytest.approx(hit * 1.2)  # RedBonusDamagePercent
    spell = [(t - cast, d) for t, d, _ in rows if d > 100]
    assert spell[0] == (17, pytest.approx(hit))  # the wave spawns 12 ticks in and reaches the target 1 hex away
    assert all(d == pytest.approx(hit / 2) for _, d in spell[1:2])  # the others: SecondaryDamagePercent
    assert cast + 11 in counter.launches  # 'Fire' (0.3498 s): one simulated launch
    # VOD6 E3: the next attack's mana 88 / 88 / 86 frames (44 / 44 / 43 ticks) after the cast; engine 43
    nxt = min(t for t, d, _ in rows if t > cast and d < 100)
    assert nxt - cast == 43
    # Blue's refund is paid at 'ManaUnlock' (26 ticks), inside the cast: the next attack starts from it
    assert [m for t, d, m in rows if t == nxt] == [10]
