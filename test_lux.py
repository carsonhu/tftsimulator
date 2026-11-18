"""Lux end to end (champions/Lux.md): numbers from build rls-19.1.0.5973071; mana and cast rhythm against the owner's
60 fps PBE VOD3 (17-13-37-283, f28998-29630: Lux 1-star with Spear of Shojin + Adaptive Helm)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from layout import Layout
from set19champs import Lux
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedLux(Lux):
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


def fight(c, items=(), buffs=(), seconds=12, n=8, layout=None):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds, layout=layout)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_locks():
    c = LoggedLux(1)
    assert (c.curMana, c.fullMana.stat, c.aspd.stat, c.attack_range, c.atk.stat) == (0, 40, 0.75, 4, 30)
    # CD_Lux19_Spell_new: DamageAndBeam 1.0416 s; Unlock 1.5625 s -> mana lock 47 ticks, cast lock 48
    assert c.beam_at == 1.0416 and (round(c.timing.mana_lock * 30), round(c.timing.cast_lock * 30)) == (47, 48)
    assert c.timing.cast_cancels_attack and c.default_traits == ['IonicSpark', 'Prodigy']


def test_vod3_mana_with_shojin_and_adaptive_helm():
    # VOD3 mana text: regen 1.725 a step ((2 role + 1 Shojin + 3 Helm) x 1.15 = 6.9/s, shown 7/s), attacks +13.8
    # ((7 + 5) x 1.15); after casts the overflow 1.4, then 1.075, then 0.75 (shown 1, then 1 and 2.8, then 2.475)
    c = LoggedLux(1)
    fight(c, items=[set19items.SpearOfShojin(), set19items.AdaptiveHelm()])
    steps = {round(after - before, 3) for t, a, before, after in c.mana_log if after > before}
    assert steps == {1.725, 13.8}
    overflow = [round(next(before for t, a, before, after in c.mana_log if t > cast), 3) for cast in c.casts]
    assert overflow[:3] == [1.4, 1.075, 0.75]
    # cast rhythm: VOD3 cast-filling attacks at f29116, 29319, 29512 = 0, 101.5, 198 ticks; engine 99 + 99
    assert [b - a for a, b in zip(c.casts, c.casts[1:])][:2] == [99, 99]
    # the attack after a cast pays its mana 59 ticks after the filling attack's (VOD3: 59.5, 56.5, 59)
    fills = [t for t, a, before, after in c.mana_log if a == 12 and after >= 40]
    attacks = [t for t, a, before, after in c.mana_log if a == 12]
    assert [next(x for x in attacks if x > f) - f for f in fills[:2]] == [59, 59]


def test_beams():
    # 1-star at AP 1.0: 330 on the target, 170 on the enemy nearest Lux, both at DamageAndBeam (cast + 32 ticks)
    c = LoggedLux(1)
    rows = fight(c, seconds=8)
    cast = c.casts[0]
    assert [r for r in rows if r[1] > 100] == [(cast + 32, 330), (cast + 32, 170)]
    # one dummy: the secondary beam hits the target again (0x5b4)
    c = LoggedLux(2)
    rows = fight(c, seconds=8, n=1)
    assert [d for t, d in rows if d > 100][:2] == [500, 255]


def test_secondary_is_nearest_lux():
    # TR_Add_N_NearestEnemiesWithoutTags from Lux: on the default layout the dummy behind the target (5 hexes);
    # with a dummy beside the target, that one (4 hexes from Lux, nearer than the one behind)
    c = LoggedLux(1)
    fight(c, seconds=1)
    assert c.nearest(1, exclude=[c.opponents[0]]) == [c.opponents[1]]
    c = LoggedLux(1)
    fight(c, seconds=1, layout=Layout(adjacent=3))
    target = c.opponents[0]
    (other,) = c.nearest(1, exclude=[target])
    assert c.target_hexes(other) == 4


def test_prodigy_mana_regen():
    # CT_Prodigy19: members 2/3/6/7 + 1, everyone else 1 (GE_19_Prodigy_Trait / _NonTrait)
    for level, regen in ((2, 2 + 2 + 1), (3, 2 + 3 + 1), (4, 2 + 6 + 1), (5, 2 + 7 + 1)):
        c = LoggedLux(1)
        Simulator().itemStats([set19buffs.Prodigy(level)] + c.items, c)
        assert c.manaRegen.stat == pytest.approx(regen)
    from set19champs import Varus
    v = Varus(1, build=load_build(V))
    Simulator().itemStats([set19buffs.Prodigy(2)] + v.items, v)
    assert v.manaRegen.stat == pytest.approx(2 + 1)  # an AttackCaster (2 regen), not a Prodigy: the team's 1
