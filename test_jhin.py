"""Jhin (champions/Jhin.md): numbers from build rls-19.1.0.5986094; the AS -> AD conversion, the Ammo rhythm and the
ascension against the owner's 60 fps VOD6 (18-40-41-766, round 1-10: Jhin 1 star with two items)."""
import collections

import pytest

import set19buffs
from buildstore import load_build
from set19champs import Jhin
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'


class LoggedJhin(Jhin):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.launch_log = []

    def onLaunch(self, opponents, items):
        self.launch_log.append((self.tick, self.seq, self.ascended))
        super().onLaunch(opponents, items)


def fight(seconds=22, buffs=()):
    j = LoggedJhin(1)
    ds = [dummy() for _ in range(3)]  # in a line behind the target (test_timing)
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([], list(buffs), j, ds, seconds)
    hits = collections.defaultdict(list)
    for t, d, *_ in j.dmgVector:
        hits[round(t * 30)].append(round(d[0], 2))
    return j, ds, hits


def test_attack_speed_becomes_ad():
    # GE_Jhin19_ASToADConverter; VOD6 E1: AS 0.84 all fight, AD 16% with two +10% AS items
    j = LoggedJhin(1)
    assert (j.aspd.stat, j.bonus_ad.stat, j.ammo, j.attack_range) == (0.84, 1.0, 4, 5)
    j.aspd.modify('MultiplyAdditive', 1.1)
    j.aspd.modify('MultiplyAdditive', 1.1)
    assert j.aspd.stat == 0.84 and j.bonus_ad.stat == pytest.approx(1.16)
    j.aspd.modify('MultiplyAdditive', 1.5)  # a later bonus is followed at once (not a snapshot)
    assert j.bonus_ad.stat == pytest.approx(1.56)


def test_rhythm_ammo_and_ascension():
    j, ds, hits = fight()
    ticks = [t for t, _, _ in j.launch_log]
    gaps = [b - a for a, b in zip(ticks, ticks[1:])]
    # VOD6 E2: launches 70 / 72 frames apart (35 / 36 ticks) at AS 0.84, Ammo or not
    assert set(gaps[:11]) == {35, 36}
    assert [s for _, s, _ in j.launch_log[:8]] == [1, 2, 3, 4, 1, 2, 3, 4]
    # the 3rd 4th shot ascends him: UltDelay / scalar (18 ticks) + CD_Jhin19_CastAnim (26 + 1) + the piercing
    # windup 0.2508 s (8): 53 ticks to the next launch; VOD6 E2: 108 frames (54 ticks)
    assert gaps[11] == 53 and not j.launch_log[11][2] and j.launch_log[12][2]
    assert set(gaps[12:]) == {35, 36}


def test_damage():
    j, ds, hits = fight()
    first = j.launch_log[0][0]
    # the first cycle: violins 1..4 x 25 (Calc1 x NumViolins), attacks 33 (30 AD, 25% crit x 1.4 averaged), the 4th
    # shot 80 x AD + 14 x AP = 94 (no attack), all at the target
    cycle = sorted(d for t, ds_ in hits.items() if first <= t < j.launch_log[4][0] for d in ds_)
    assert cycle == sorted([25, 50, 75, 100, 33, 33, 33, 94])
    # ascended: each launch pierces the line: the target x1, the two behind x0.4; each of the 4 violins too
    asc = j.launch_log[12][0]
    after = sorted(d for t, ds_ in hits.items() if asc <= t < j.launch_log[13][0] for d in ds_)
    assert after == sorted([33, 13.2, 13.2] + [25] * 4 + [10] * 8)


def test_encore():
    # Encore (2): RecastEffectiveness 0.25: each violin volley fires again for Calc1 x r x NumViolins (the terms
    # multiply), the 4th shot again for Calc2 x r
    j, ds, hits = fight(seconds=6, buffs=[set19buffs.Encore(2)])
    dmg = sorted(d for t, ds_ in hits.items() if t < j.launch_log[4][0] for d in ds_)
    assert sorted(d for d in dmg if d not in (33,)) == sorted([25, 50, 75, 100, 94, 6.25, 12.5, 18.75, 25, 23.5])
