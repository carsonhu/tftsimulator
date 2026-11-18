"""Varus end to end (champions/Varus.md): numbers from build rls-19.1.0.5973071, timing against the owner's 60 fps
PBE VOD of 2026-11-17 16:22 (Varus 1★ with Blue Buff + Guinsoo's; combat start f15365, Blue Buff's mana)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from set19champs import Varus
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedVarus(Varus):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.attack_mana, self.casts = [], []

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        if amount == 7 and self.curMana > before:
            self.attack_mana.append(self.tick)

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(v, items=(), buffs=(), seconds=14, armor=0, n=2):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = armor
    Simulator().simulate(list(items), list(buffs), v, ds, seconds)
    return [(round(t * 30), round(d[0], 2)) for t, d, *_ in v.dmgVector]


def test_build_numbers_and_timing_rules():
    v = LoggedVarus(1)
    assert (v.curMana, v.fullMana.stat, v.aspd.stat, v.attack_range) == (30, 70, 0.7, 4)
    assert v.missiles == [(0.4278, 1800, False), (0.6286, 1800, True)]
    assert v.num_targets == 2  # set18 convention: the target + 1 adjacent by default
    assert v.timing.release_scales_with_period  # G19: his attack modules lack bUseRateScalingThreshold
    assert v.timing.cast_cancels_attack and (v.timing.cast_lock, v.timing.mana_lock) == (1.0333, 1)


def test_vod_fight_with_blue_buff_and_guinsoos():
    # VOD (ticks from combat start): first attack mana at 8, casts at 56, 221.5, 378 -> gaps 165.5, 156.5.
    # Engine: 7 and 54, 219, 376. The gaps match to half a tick; the constant ~2-tick offset is the open T10 (+1 on
    # fresh attacks) and G17 (first regen step ~4 ticks after combat start in the VOD, tick 0 in the engine).
    v = LoggedVarus(1)
    fight(v, items=[set19items.BlueBuff(), set19items.GuinsoosRageblade()])
    assert v.attack_mana[0] == 7
    assert v.casts == [54, 219, 376]
    vod = [56, 221.5, 378]
    gaps = [b - a for a, b in zip(v.casts, v.casts[1:])]
    vod_gaps = [b - a for a, b in zip(vod, vod[1:])]
    assert all(abs(g - h) <= 1 for g, h in zip(gaps, vod_gaps))


def test_spell_damage_and_timing():
    # Calc1 = 30 x AP + 230 x AD at 1★ (AD, AP multipliers 1.0): 260 to the target, 130 (AOEDamagePercent 0.5) to
    # one adjacent enemy (num_targets 2), physical, at cast + 13 (Fire 0.4278 s) + 15 (4 hexes at 1800, G4)
    v = LoggedVarus(1)
    rows = fight(v, seconds=8)
    c = v.casts[0]
    assert [(t - c, d) for t, d in rows if d > 100] == [(28, 260), (28, 130)]


def test_items_raise_ad_and_ap_multipliers():
    # Blue Buff (15% AD, 15% AP) + Guinsoo's (10% AP): 30 x 1.25 + 230 x 1.15 = 302, splash 151
    v = LoggedVarus(1)
    rows = fight(v, items=[set19items.BlueBuff(), set19items.GuinsoosRageblade()], seconds=4)
    assert [d for t, d in rows if d > 100][:2] == [302, 151]


def test_encore_missile_and_targets():
    # Encore (2): EncoreHailMain at 0.6286 s (19 ticks) + 15 of flight, 25% of each hit
    v = LoggedVarus(1)
    rows = fight(v, buffs=[set19buffs.Encore(2)], seconds=8)
    c = v.casts[0]
    spell = [(t - c, d) for t, d in rows if t > c and d != 38.5]  # 38.5 = an attack: 35 AD x 1.1 average crit
    assert spell[:4] == [(28, 260), (28, 130), (34, 65), (34, 32.5)]
    v = LoggedVarus(1)
    v.num_targets = 1
    rows = fight(v, seconds=8)
    assert [d for t, d in rows if d > 100] == [260]


@pytest.mark.parametrize('level,dmg', [(2, 45 + 345), (3, 70 + 520)])
def test_star_levels(level, dmg):
    v = LoggedVarus(level)
    rows = fight(v, seconds=12, n=1)
    assert [d for t, d in rows if d > 150][:1] == [dmg]
