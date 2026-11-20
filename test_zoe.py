"""Zoe and Beach Pop (champions/Zoe.md): numbers from build rls-19.1.0.5973071 (no cast seen on a VOD yet: VOD5's
fights ended before her 90 mana filled)."""
import pytest

import set19buffs
import sim_entry
from buildstore import load_build
from set19champs import Ashe, Zoe
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedZoe(Zoe):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.mana_log, self.casts = [], []

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        self.mana_log.append((self.tick, amount, before, self.curMana))

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(c, items=(), buffs=(), seconds=10, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers():
    z = LoggedZoe(1)
    assert (z.curMana, z.fullMana.stat, z.aspd.stat, z.attack_range) == (15, 90, 0.7, 4)
    assert (z.redirect_at, z.ball_spawn) == (1.3167, 0.0291)
    assert (round(z.timing.mana_lock * 30), round(z.timing.cast_lock * 30)) == (55, 56)
    assert sorted(z.default_traits) == ['Arcanist', 'BeachPop']


def test_paddle_ball():
    # the ball: 450 x AP to the target, from 300 units behind her at 2500 units/s after RedirectProjectile (1.3167 s +
    # spawn 0.0291 s = 41 ticks): 300 + 4 x 215 units = 14 ticks
    z = LoggedZoe(1)
    z.curMana = 90
    rows = fight(z, seconds=4)
    cast = z.casts[0]
    assert [(t - cast, d) for t, d in rows if d == 450] == [(41 + 14, 450)]


def test_beach_pop():
    # breakpoints 3/5/7 (the tooltip, VOD5 2:14; the build's are placeholders); empowered members +20/35/35% AS and
    # +5/8/8 mana every 3 s; at 7 also +40 mana every 10 s
    for level, bonus in ((3, 0.2), (4, 0.2), (5, 0.35), (7, 0.35)):
        z = LoggedZoe(1)
        fight(z, buffs=[set19buffs.BeachPop(level)], seconds=1)
        assert z.aspd.stat == pytest.approx(0.7 * (1 + bonus))
    z = LoggedZoe(1)
    fight(z, buffs=[set19buffs.BeachPop(5)], seconds=7)
    assert [t for t, a, before, after in z.mana_log if a == 8] == [90, 180]
    z = LoggedZoe(1)
    fight(z, buffs=[set19buffs.BeachPop(7)], seconds=11)
    assert [t for t, a, before, after in z.mana_log if a == 40] == [300]
    # the card: the tooltip's breakpoints with the build's numbers, not the build's placeholder (owner, 2026-11-20)
    card = sim_entry.get_cards({})["BeachPop"]
    assert [t["threshold"] for t in card["tiers"]] == [3, 5, 7] and "Placeholder" not in str(card)
    # every member is empowered (owner, 2026-11-20: no toggle)
    assert set19buffs.BeachPop.extraParameters() == 0
    # a non-member gets nothing from it here (the Health regen changes no damage)
    a = Ashe(1, build=load_build(V))
    fight(a, buffs=[set19buffs.BeachPop(3)], seconds=1)
    assert a.aspd.stat == pytest.approx(0.75 * 1.2)  # Ashe is a Beach Pop member
