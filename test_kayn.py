"""Kayn (champions/Kayn.md): numbers from build rls-19.1.0.5986094; against the owner's 60 fps VOD6 (18-40-41-766,
rounds 1-3 and 1-4: Kayn 1 star; at 1-4 the Heartsteel (3) Bias, Shadow Assassin)."""
import pytest

import set19buffs
from buildstore import load_build
from set19champs import Kayn
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'
BIAS = 1 << set19buffs.Heartsteel.BIAS


class LoggedKayn(Kayn):
    def __init__(self, level=1, build=V):
        super().__init__(level, build=load_build(build))
        self.casts = []

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(c, buffs=(), seconds=5, n=3):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([], list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 4), d[1]) for t, d, *_ in c.dmgVector]


def test_build_numbers():
    k = LoggedKayn(1)
    assert (k.curMana, k.fullMana.stat, k.aspd.stat, k.attack_range, k.atk.stat, k.hp.stat) == (0, 30, 0.75, 1, 42, 650)
    assert k.deal_damage_at == 0.4591
    assert (round(k.timing.mana_lock * 30), round(k.timing.cast_lock * 30)) == (22, 23)
    # VOD6 1:57.6 tooltip: 140 = 115 x 1.07 (Heartsteel's Kayn AD) + 15 x 1.10
    assert k.spell_damage(1, 1.07, 1.10) == pytest.approx(139.55)


def test_swipe_and_rhythm():
    k = LoggedKayn(1)
    rows = fight(k)
    cast = k.casts[0]
    attacks = [t for t, d, kind in rows if t < cast]
    assert len(attacks) == 3 and cast == attacks[-1] + 1  # 3 x 10 mana fills 30; the cast the next tick (T4)
    # the swipe 14 ticks into the cast (0.4591 s), not a crit (no Precision); the next attack after 23 + windup
    assert [(t - cast, d) for t, d, kind in rows if t >= cast][:2] == [(14, 130), (33, pytest.approx(46.2))]


def test_swipe_line():
    # the rectangle from him toward the target holds the dummies straight behind it within 429 units
    k = LoggedKayn(1)
    fight(k, seconds=0.04)
    t = k.opponents[0]
    hit = k.swipe_targets(t)
    assert hit[0] is t and all(d in k.opponents for d in hit)


def test_shadow_assassin():
    # Heartsteel (3) with Kayn as the Bias: +7% AD (his own fielded bonus) and, as the Shadow Assassin from combat
    # start (assumed, Q17), 35% of each damage's pre-mitigation amount again as magic damage
    k = LoggedKayn(1)
    rows = fight(k, buffs=[set19buffs.Heartsteel(3, BIAS)])
    assert k.heartsteel_bias and k.bonus_ad.stat == pytest.approx(1.07)
    first = [(d, kind) for t, d, kind in rows if t == rows[0][0]]
    assert first == [(pytest.approx(42 * 1.07 * 1.1), 'physical'), (pytest.approx(42 * 1.07 * 1.1 * 0.35), 'magical')]
    cast = k.casts[0]
    swipe = [(d, kind) for t, d, kind in rows if t == cast + 14]
    assert swipe == [(pytest.approx(130 + 115 * 0.07), 'physical'), (pytest.approx((130 + 115 * 0.07) * 0.35), 'magical')]
    # no Bias: no bonus
    k = LoggedKayn(1)
    rows = fight(k, buffs=[set19buffs.Heartsteel(3, 0)])
    assert not k.heartsteel_bias and {kind for t, d, kind in rows} == {'physical'}
