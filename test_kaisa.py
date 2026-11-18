"""Kai'Sa end to end (champions/Kaisa.md) and K/DA: numbers from build rls-19.1.0.5973071; timing against the
owner's 60 fps PBE VOD3 (17-13-37-283, Kai'Sa 1* with Infinity Edge + 2 Deathblades, Trickshot (2), f40506-42300)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from set19champs import Kaisa, Neeko, Varus
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedKaisa(Kaisa):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.releases, self.casts, self.as_at_cast = [], [], []

    def onLaunch(self, opponents, items):
        self.releases.append(self.tick)
        super().onLaunch(opponents, items)

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)
        self.as_at_cast.append(round(self.aspd.stat, 4))


def fight(c, items=(), buffs=(), seconds=30, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 2)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_timing():
    k = LoggedKaisa(1)
    assert (k.curMana, k.fullMana.stat, k.aspd.stat, k.attack_range) == (0, 30, 0.75, 5)
    t = k.timing
    assert t.animations == 4 and len(t.variants) == 8 and t.cast_keeps_rhythm and not t.cast_cancels_attack
    # below 1.75 AS the LowAS animations: windups 0.3255, 0.4242, 0.3578, 0.4242 s; from 1.75 the fast ones
    assert [t.variant(s, 0.75)[0] for s in (1, 2, 3, 4)] == [0.3255, 0.4242, 0.3578, 0.4242]
    assert [t.variant(s, 1.75)[0] for s in (1, 2, 3, 4)] == [0.1361, 0.3219, 0.169, 0.3425]


def test_vod3_release_rhythm():
    # VOD3 mana steps (attack releases) relative to the first, in ticks; the 4th fell while the panel was hidden.
    # Starts are a period apart and each release is its own animation's windup later (B13), so release gaps differ:
    # 44, 38 at 0.75 AS. Exact through the first 11 releases; the engine then drifts up to +4 ticks by the 20th (T13)
    vod = [0, 44, 82, None, 156, 193, 226, 258, 286, 319, 345, 374, 398.5, 425.5, 449.5, 474.5, 495.5, 520.5, 541.5,
           563.5, 582.5, 605.5, 623.5, 644.5, 662, 682]
    k = LoggedKaisa(1)
    fight(k, items=[set19items.InfinityEdge(), set19items.Deathblade(), set19items.Deathblade()],
          buffs=[set19buffs.Trickshot(2)])
    eng = [t - k.releases[0] for t in k.releases]
    diffs = [e - v for e, v in zip(eng, vod) if v is not None]
    assert all(abs(d) <= 1 for d in diffs[:11]) and all(abs(d) <= 4 for d in diffs)
    assert k.releases[0] == 10  # first attack: Attack1LowAS, 0.3255 s


def test_casts_stack_attack_speed_and_keep_the_rhythm():
    # VOD3 panel AS after each cast: 0.86, 0.97, 1.09, 1.20, 1.31, 1.42, 1.54, 1.65, 1.76 = 0.75 x (1 + 0.15 k)
    k = LoggedKaisa(1)
    fight(k, seconds=30)
    assert k.as_at_cast[:9] == [round(0.75 * (1 + 0.15 * i), 4) for i in range(1, 10)]
    # every third release fills the bar (10 mana each) and the cast does not restart the attack
    assert all(c - 1 in k.releases or c in k.releases for c in k.casts)
    gaps = [b - a for a, b in zip(k.releases, k.releases[1:])]
    assert min(gaps[:6]) > 30


def test_missiles_every_third_launch():
    # 3 missiles of 36 x AD + 6 x AP every 3 launches, at 1900 units/s: the target's two land 17 ticks later (5
    # hexes), the one to the dummy next to the target 21 (6 hexes on the default layout; owner, 2026-11-17)
    k = LoggedKaisa(1)
    rows = fight(k, seconds=6)
    missiles = [(t, d) for t, d in rows if d == 42]
    third = k.releases[2]
    assert missiles[:3] == [(third + 17, 42)] * 2 + [(third + 21, 42)]


def test_missiles_ricochet_with_trickshot():
    k = LoggedKaisa(1)
    rows = fight(k, buffs=[set19buffs.Trickshot(2)], seconds=6)
    third = k.releases[2]
    # each missile bounces once at 22%, 1 hex (4 ticks) on: the target's two onto its neighbour, the neighbour's on
    # down the line
    bounce = round(42 * 0.22, 2)
    assert rows.count((third + 17 + 4, bounce)) == 2 and rows.count((third + 21 + 4, bounce)) == 1


def test_kda_mana_and_decaying_attack_speed():
    n = Neeko(1, build=load_build(V))
    Simulator().itemStats([set19buffs.KDA(3)] + n.items, n)
    assert n.fullMana.stat == 36  # VOD2: Neeko 40 -> 36 at K/DA (3)
    k = LoggedKaisa(1)
    seen = {}
    orig = k.update

    def update(o, i, t):
        seen[k.tick] = k.aspd.stat
        return orig(o, i, t)

    k.update = update
    fight(k, buffs=[set19buffs.KDA(7)], seconds=10)
    assert k.fullMana.stat == 27
    assert seen[1] == pytest.approx(0.75 * 1.6) and seen[9] == pytest.approx(0.75 * (1 + 0.6 * 31 / 32))
    k = LoggedKaisa(1)
    fight(k, buffs=[set19buffs.KDA(10)], seconds=2)
    assert k.fullMana.stat == pytest.approx(30 * 0.875)


def test_kda_needs_membership():
    v = Varus(1, build=load_build(V))
    Simulator().itemStats([set19buffs.KDA(10)] + v.items, v)
    assert v.fullMana.stat == 70
