"""Alune (champions/Alune.md): GA_Alune19_Spell (D1) on build rls-19.1.0.6011486, checked against the owner's 60 fps
VOD7 (22-23-46-350: Alune 1-star at 3-3, 3-5 and 3-6 with no items, Prodigy (4) / (5) / (5); at 4-1 with Nashor's Tooth
and two Jeweled Gauntlets)."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from layout import Layout
from set19champs import Alune
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.6011486.Set19.Shipping.pbe'


class LoggedAlune(Alune):
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


def fight(a, buffs=(), seconds=15, targets=3, mr=0, items=()):
    lay = Layout(targets)
    ds = [dummy() for _ in range(lay.count)]
    for d in ds:
        d.armor.base, d.mr.base = 0, mr
    Simulator().simulate(list(items), list(buffs), a, ds, seconds, layout=lay)
    rows = {}
    for t, d, *_ in a.dmgVector:
        rows.setdefault(round(t * 30), []).append(round(d[0], 4))
    return ds, rows


def test_build_numbers():
    a = LoggedAlune(1)
    assert (a.curMana, a.fullMana.stat, a.aspd.stat, a.attack_range) == (20, 65, 0.75, 4)
    assert (round(a.timing.mana_lock * 30), round(a.timing.cast_lock * 30)) == (39, 40)  # 'Unlock' 1.2952 s
    assert round(a.damage_at * 30, 3) == 31.818 and a.missile_speed == 1900


@pytest.mark.parametrize('tier, regen', [(4, 8), (5, 9)])
def test_vod7_mana_and_cast_lock(tier, regen):
    # VOD7: 8/s at 3-3 (Prodigy (4)), 9/s at 3-5 / 3-6 (5); attacks +7 every 80 frames (40 ticks); the banked overflow shows
    # 80-81 frames (40 ticks = 39 + T4) after the filling mana; the next attack's mana 104-105 frames (52 ticks)
    # after the fill, every cast of both fights
    a = LoggedAlune(1)
    fight(a, buffs=[set19buffs.Prodigy(tier)])
    assert a.manaRegen.stat == regen
    attacks = [t for t, amt, before, after in a.mana_log if amt == 7]
    assert attacks[1] - attacks[0] == 40
    for cast in a.casts[:2]:
        fill = max(t for t, amt, before, after in a.mana_log if t <= cast and after > before)
        assert cast == fill + 1
        assert next(t for t in attacks if t > cast) - fill == 52
        gain = next(t for t, amt, before, after in a.mana_log if t > cast and after > before)
        assert fill + 40 <= gain <= fill + 40 + 8  # lock over, then the next regen step (overflow 0 here)


def test_spotlight_splits_with_the_target():
    # 'Damage' (1.0606 s -> 32 ticks): N enemies within 2 hexes besides the target; each takes Calc3 / (N + 1), the
    # target Calc3 / (N + 1) + Calc1
    for targets in (1, 3):
        a = LoggedAlune(1)
        ds, rows = fight(a, buffs=[set19buffs.Prodigy(4)], targets=targets)
        cast = a.casts[0]
        split = 1 / targets
        ap = a.ap.stat
        expect = [round(340 * ap * split, 4)] * (targets - 1) + [round(340 * ap * split + 315 * ap, 4)]
        assert sorted(rows[cast + 32]) == pytest.approx(sorted(expect))


def test_heartsteel_bias_blasts():
    # a Bias at Heartsteel (3)+: 5 blasts of HeartsteelStan_APDamage x AP at the target from 'FireHeartsteelMissiles'
    # (0.9616 s), 0.04 s apart, 1900 units/s; without the Bias, none
    def blasts(params):
        a = LoggedAlune(1)
        ds, rows = fight(a, buffs=[set19buffs.Prodigy(4), set19buffs.Heartsteel(3, params)], seconds=6, targets=1)
        one = round(a.row('HeartsteelStan_APDamage', star=1) * a.ap.stat, 4)
        return a, sorted(t - a.casts[0] for t, hits in rows.items() for d in hits if d == one)

    a, hits = blasts(1 << set19buffs.Heartsteel.BIAS)
    assert a.heartsteel_bias and len(hits) == 5
    assert hits[0] >= 29 and hits[-1] - hits[0] in (4, 5)  # 0.16 s of spacing, rounded up to ticks
    a, hits = blasts(0)
    assert not a.heartsteel_bias and hits == []


def test_vod7_four_one_nashors_and_two_gauntlets():
    # VOD7 4-1 (f66849-68600): AS 0.83, crit 100%, 9/s. Attacks +9 (7 + Nashor's ManaPerAttack 2) 72-76 frames apart,
    # +2 more when a critical attack lands (GA_NashorsTooth, I6: f67021 release, f67054 +2); a cycle gains ~22 mana.
    # The next attack's mana 104-105 frames (52 ticks) after each fill, as without items: the windup barely moves
    a = LoggedAlune(1)
    fight(a, items=[set19items.NashorsTooth(), set19items.JeweledGauntlet(), set19items.JeweledGauntlet()],
          buffs=[set19buffs.Prodigy(5)])
    assert round(a.aspd.stat, 3) == 0.825 and a.manaRegen.stat == 9 and a.crit.stat >= 1
    attacks = [t for t, amt, before, after in a.mana_log if amt == 9]
    assert attacks[1] - attacks[0] in (36, 37)
    crits = [t for t, amt, before, after in a.mana_log if amt == 2]
    assert crits[0] - attacks[0] == 15  # the projectile's flight to a target 4 hexes away, 1750 units/s
    for cast in a.casts[:3]:
        fill = max(t for t, amt, before, after in a.mana_log if t <= cast and after > before)
        assert next(t for t in attacks if t > cast) - fill == 52
