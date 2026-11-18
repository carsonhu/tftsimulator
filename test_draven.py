"""Draven end to end (champions/Draven.md): numbers from build rls-19.1.0.5973071; Trickshot (set19buffs)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from set19champs import Draven, Varus
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedDraven(Draven):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.casts = []

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(c, items=(), buffs=(), seconds=12, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 2)) for t, d, *_ in c.dmgVector]


def spell_rows(c, rows):
    k = c.casts[0]
    return [(t - k, d) for t, d in rows if t >= k and d not in (49.5, 10.89, 16.34, 5.39)]  # drop attacks


def test_build_numbers():
    d = LoggedDraven(1)
    assert (d.curMana, d.fullMana.stat, d.aspd.stat, d.attack_range) == (0, 60, 0.75, 4)
    assert d.throw_at == 0.6566 and d.vortex_hits == 6
    assert d.chrono_projectile_ticks('CD_Draven19_Spell', 'Blade', 4) == 14  # 1500 + 2000/s over 860 units
    assert (d.timing.cast_lock, d.timing.mana_lock) == (1.7, 1.6667)


def test_record_and_vortex():
    # record at cast + 20 (0.6566 s) + 14 (flight): 140 x AD; vortex 6 x (100 AD + 15 AP) x 0.5 s, every 15 ticks
    d = LoggedDraven(1)
    assert spell_rows(d, fight(d))[:7] == [(34, 140), (34, 57.5), (49, 57.5), (64, 57.5), (79, 57.5), (94, 57.5),
                                           (109, 57.5)]


def test_items_scale_ad_and_ap():
    d = LoggedDraven(1)
    rows = [r for r in spell_rows(d, fight(d, items=[set19items.Deathblade(), set19items.RabadonsDeathcap()]))
            if r[1] not in (80.81,)]  # attacks here are 45 x 1.63 x 1.1 = 80.8
    ad, ap = 1 + 0.55 * 1.15, 1 + 0.55 * 1.15
    assert rows[0] == (34, pytest.approx(140 * ad, abs=0.01)) and rows[1] == (34, pytest.approx((100 * ad + 15 * ap) / 2, abs=0.01))


def test_trickshot_spell_ricochet():
    # Trickshot (2): 1 ricochet at 22%, 4 ticks later (2000 units/s over 1 hex), with its own vortex
    d = LoggedDraven(1)
    rows = spell_rows(d, fight(d, buffs=[set19buffs.Trickshot(2)], seconds=14))
    assert (38, 30.8) in rows and rows.count((38, 12.65)) == 1 and len([r for r in rows if r[1] == 12.65]) == 6
    # Trickshot (4): 2 ricochets, 33% of the previous
    d = LoggedDraven(1)
    rows = spell_rows(d, fight(d, buffs=[set19buffs.Trickshot(4)]))
    assert (38, 46.2) in rows and (42, pytest.approx(15.25, abs=0.01)) in rows


def test_trickshot_attack_ricochet():
    # an attack (45 AD x 1.1 average crit = 49.5) ricochets 4 ticks later (1600 units/s, 1 hex) at 22%
    d = LoggedDraven(1)
    rows = fight(d, buffs=[set19buffs.Trickshot(2)], seconds=4)
    hits = [t for t, v in rows if v == 49.5]
    assert hits and all((t + 4, 10.89) in rows for t in hits)
    assert d.numAttacks == len(hits)  # a ricochet is not an attack


def test_trickshot_needs_membership_and_a_tier():
    d = LoggedDraven(1)
    assert all(v != 10.89 for _, v in fight(d, buffs=[set19buffs.Trickshot(0)], seconds=4))
    v = Varus(1, build=load_build(V))  # not a Trickshot
    rows = fight(v, buffs=[set19buffs.Trickshot(4)], seconds=4)
    assert all(round(x / 38.5, 2) in (1.0,) or x > 100 for _, x in rows)


def test_single_dummy_ricochets_return_to_it():
    d = LoggedDraven(1)
    rows = spell_rows(d, fight(d, buffs=[set19buffs.Trickshot(2)], n=1))
    assert (34, 30.8) in rows  # the bounce computer re-picks the hit enemy: 0 hexes


def test_illbeats_mix_values():
    # VOD4 (19-0-51-650) 17:04-17:44, Illbeats (3), the mixer's rounded readouts per decibel (members): AD 4, 7, 10,
    # 13, 16, 19, 22, 24, -, 28%; AP 3, 6 (1, 2 dB), 17 (6), 26 (10); the trait tooltip at 15:16 (Illbeats (2)):
    # "Attack Damage: 16.2%" at 5 dB. (4): x1.5. Non-members: x0.5.
    import set19buffs
    from set19champs import Draven, Ezreal
    from simulator import Simulator
    t = set19buffs.Illbeats(3, 0)
    d = Draven(1, build=load_build(V))
    Simulator().itemStats([t] + d.items, d)
    ad = [t.channel_value(d, 'PercentAD', n) * 100 for n in range(1, 11)]
    assert [round(x + 1e-9) for x in ad] == [4, 7, 10, 13, 16, 19, 22, 24, 26, 28]
    assert abs(ad[4] - 16.2) < 1e-9
    ap = [t.channel_value(d, 'PercentAP', n) * 100 for n in (1, 2, 6, 10)]
    assert [round(x) for x in ap] == [3, 6, 17, 26]
    hp = [t.channel_value(d, 'PercentHealth', n) * 100 for n in (1, 2, 6, 7, 8, 9)]
    assert [round(x) for x in hp] == [2, 4, 10, 12, 13, 15]
    # All AD at (3): 14 decibels, 10 on AD (the channel cap): +28% AD
    assert abs(d.bonus_ad.stat - 1.28) < 1e-9
    for level, mix, member, ad_pct, ap_pct in ((2, 0, True, 0.28, 0), (4, 0, True, 0.42, 0), (2, 0, False, 0.14, 0),
                                                (3, 2, True, 0.215, 0.197), (2, 1, False, 0, 0.13), (3, 3, True, 0, 0)):
        c = Draven(1, build=load_build(V)) if member else Ezreal(1, build=load_build(V))
        Simulator().itemStats([set19buffs.Illbeats(level, mix)] + c.items, c)
        assert abs(c.bonus_ad.stat - 1 - ad_pct) < 1e-9 and abs(c.ap.stat - 1 - ap_pct) < 1e-9, (level, mix, member)
    assert 'Illbeats' in Draven(1, build=load_build(V)).default_traits
