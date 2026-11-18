"""Neeko end to end (champions/Neeko.md): every number from build rls-19.1.0.5973071, timing against the owner's
PBE VOD of 2026-11-17 (evidence E1-E8 in the worksheet).

The VOD's frame numbers are relative to the combat banner, which is only good to a frame or two, so the timing tests
compare intervals (attack to attack, cast to next attack), not absolute ticks.
"""
import pytest

from buildstore import load_build
import set19buffs
from set19champs import Neeko
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedNeeko(Neeko):
    """Records the tick of every mana payment of 7 (attack mana) and every cast."""

    def __init__(self, level=1, **kw):
        super().__init__(level, build=load_build(V))
        for k, v in kw.items():
            setattr(self, k, v)
        self.attack_mana_ticks, self.cast_ticks = [], []

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        if amount == 7 and self.curMana > before:
            self.attack_mana_ticks.append(self.tick)

    def performAbility(self, opponents, items, time):
        self.cast_ticks.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(n, seconds=10, mr=0, buffs=()):
    d = dummy()
    d.mr.base = mr
    Simulator().simulate([], list(buffs), n, [d], seconds)
    return [(round(t * 30), round(dmg[0], 4)) for t, dmg, *_ in n.dmgVector]


def test_numbers_come_from_the_build():
    n = LoggedNeeko(1)
    assert (n.hp.stat, n.atk.stat, n.fullMana.stat, n.aspd.stat, n.attack_range) == (500, 30, 40, 0.7, 4)  # E1
    assert [n.row('DamageAP', star=s) for s in (1, 2, 3)] == [75, 115, 175]
    # CD_Neeko19_CastAnimWithClone events; every spell missile 2000 units/s (TFTFixedSpeedWithHeightMovement)
    assert [t for t, _, _ in n.throws] == [0.2331, 0.3467, 0.46, 0.5733, 0.6867, 0.8]
    assert {s for _, s, _ in n.throws} == {2000}
    assert [e for _, _, e in n.throws] == [False, False, True, False, True, True]
    # CT_Encore19 RecastEffectiveness: Encore inactive 0, (2) 25%, (4) 50%
    assert [n.trait_value('DA_Encore19', 'RecastEffectiveness', tier=t) for t in (0, 1, 2)] == [0, 0.25, 0.5]
    assert n.timing.cast_cancels_attack and 'GA_Neeko19_SpellUsingVFX' in n.timing.source['cast_cancels_attack']
    assert (n.timing.cast_lock, n.timing.mana_lock) == (0.8333, 0.8)


def test_attack_mana_rhythm_matches_the_vod():
    # E4/E5: first +7 one windup (13) after combat start, then every 1/0.7 s with the fraction carried:
    # VOD gaps 44, 43, 43 frames at 30 fps; engine 43, 43, 43 (42.86 per period) -- within the 1-frame resolution
    n = LoggedNeeko(1)
    fight(n, seconds=6)
    first = n.attack_mana_ticks[:4]
    assert first == [13, 56, 99, 142]
    vod = [3082, 3126, 3169, 3212]
    assert all(abs((a - first[0]) - (b - vod[0])) <= 1 for a, b in zip(first, vod))


def test_cast_then_next_attack_mana_matches_the_vod():
    # E3: cast start to the next attack's +7 = 39 frames in the VOD; engine: cast lock 25 + windup 13 = 38.
    # E7 / T4: the attack under way at the cast is cancelled (the spell cancels Combat.Attacking), so nothing lands
    # between the cast and the fresh attack after the lock.
    n = LoggedNeeko(1)
    rows = fight(n, seconds=10)
    c = n.cast_ticks[0]
    after = [t for t in n.attack_mana_ticks if t > c]
    assert after[0] - c == 38
    assert abs((after[0] - c) - 39) <= 1
    attack_hits = [t for t, dmg in rows if dmg == pytest.approx(33)]
    assert not [t for t in attack_hits if c < t < after[0] + 13]  # first landing after the cast is the fresh attack


def test_spell_three_missiles_without_encore():
    # Throws 1, 2, 4 at ticks 7, 11, 18 after the cast, then 13 ticks of flight (4 hexes x 215 / 2000 = 0.43 s, G4);
    # the Encore missiles (3, 5, 6) deal 0 when Encore is inactive. 75 x AP(1.0) magic, no MR.
    n = LoggedNeeko(1)
    rows = fight(n, seconds=10)
    c = n.cast_ticks[0]
    spell = [(t - c, d) for t, d in rows if d == pytest.approx(75)]
    assert spell == [(20, 75), (24, 75), (31, 75)]


@pytest.mark.parametrize('units,tier,share', [(2, 1, 0.25), (3, 1, 0.25), (4, 2, 0.5)])
def test_encore_missiles_at_the_boards_encore_tier(units, tier, share):
    # B11: the Encore buff (units on the board) sets the tier from the build's thresholds (2, 4); Neeko's Encore
    # missiles (throws 3, 5, 6) then deal RecastEffectiveness at that tier
    n = LoggedNeeko(1)
    rows = fight(n, seconds=10, buffs=[set19buffs.Encore(units)])
    assert n.trait_tier('DA_Encore19') == tier
    c = n.cast_ticks[0]
    spell = sorted((t - c, d) for t, d in rows if t > c and d != pytest.approx(33))
    e = 75 * share
    assert spell == [(20, 75), (24, 75), (27, e), (31, 75), (34, e), (37, e)]


def test_encore_is_offered_at_the_builds_breakpoints_and_preselected_for_members():
    assert set19buffs.Encore.levels == [0, 2, 4]  # CT_Encore19 tiers (2), (4)
    assert LoggedNeeko(1).default_traits == ['Encore', 'KDA', 'Prodigy']  # Neeko is also K/DA and Prodigy
    from build_champion import BuildChampion
    ahri = type('A', (BuildChampion,), {'KEY': 'DA_Ahri19'})(1, build=load_build(V))
    assert 'Encore' not in ahri.default_traits  # not an Encore unit (she is K/DA)


def test_encore_does_nothing_for_a_non_member():
    from build_champion import BuildChampion
    cls = type('A', (BuildChampion,), {'KEY': 'DA_Ahri19'})
    a, b = cls(1, build=load_build(V)), cls(1, build=load_build(V))
    fight(a, seconds=8)
    fight(b, seconds=8, buffs=[set19buffs.Encore(4)])
    assert a.dmgVector == b.dmgVector


@pytest.mark.parametrize('level,dmg', [(2, 115), (3, 175)])
def test_star_levels_and_magic_resist(level, dmg):
    n = LoggedNeeko(level)
    rows = fight(n, seconds=10, mr=25)
    c = n.cast_ticks[0]
    assert [d for t, d in rows if t - c in (20, 24, 31)] == [pytest.approx(dmg * 100 / 125)] * 3
