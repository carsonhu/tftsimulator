"""Ziggs end to end (champions/Ziggs.md): numbers from build rls-19.1.0.5973071; timing and damage against the
owner's 60 fps PBE VOD2 (16-35-16-966, Ziggs 1*, no items, no active trait, round 1-1 minions, f1133-1963)."""
from buildstore import load_build
from set19champs import Ziggs
from simulator import Simulator
from test_timing import dummy
from timing import projectile_ticks, ticks_up

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedZiggs(Ziggs):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.releases, self.casts = [], []

    def onLaunch(self, opponents, items):
        self.releases.append(self.tick)
        super().onLaunch(opponents, items)

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(c, seconds=12, n=3):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = 0
        d.mr.base = 0
    Simulator().simulate([], [], c, ds, seconds)
    return [(round(t * 30), round(d[0], 2)) for t, d, *_ in c.dmgVector]


def test_build_numbers():
    z = LoggedZiggs(1)
    assert (z.curMana, z.fullMana.stat, z.aspd.stat, z.attack_range, z.atk.stat) == (0, 50, 0.7, 4, 10)
    assert z.timing.lock_scales_with_as and z.timing.cast_cancels_attack
    assert (z.timing.cast_lock, z.timing.mana_lock, z.bomb_spawn) == (0.8333, 0.8, 0.3183)


def test_vod2_rhythm_after_the_cast():
    # VOD2: 0/50 at f1476 (the cast, tick 738); the next releases (+10 mana) at f1564, 1648, 1734, 1820 = 44, 86,
    # 129, 172 ticks after it. Engine: cast lock 25 + a fresh attack's windup 18 (0.4 s stretched to the 1.43 s
    # period, G2) = 43 (the VOD's 44 is T10's extra tick, open), then one exact period (42.86 ticks) apart:
    # the rest match the VOD exactly.
    vod = [44, 86, 129, 172]
    z = LoggedZiggs(1)
    fight(z, seconds=15)
    c = z.casts[0]
    assert z.releases.index(c - 1) == 4  # the 5th attack fills the bar; the cast is the next tick (T4)
    after = [r - c for r in z.releases if r > c][:4]
    assert after == [43, 86, 129, 172]  # VOD 44, 86, 129, 172
    assert all(abs(e - v) <= 1 for e, v in zip(after, vod))


def test_attack_and_bomb_damage():
    # VOD2 numbers on round 1-1 minions (armor = MR = 10, shown rounded down): attack 9 physical + 36 magic on the
    # same hit (10 AD, 40 x AP); bomb 163 on the target and 72 on an adjacent minion (180 x AP, 80 x AP)
    z = LoggedZiggs(1)
    rows = fight(z)
    first_hit = z.releases[0] + z.timing.flight_ticks(z.attack_range)
    assert sorted(d for t, d in rows if t == first_hit) == [11, 40]  # 10 x expected crit 1.1; magic can't crit
    c = z.casts[0]
    land = c + ticks_up(0.3183) + projectile_ticks(1900, 4)
    assert sorted(d for t, d in rows if t == land and d > 40) == [80, 180]
    assert not any(d in (80, 180) for t, d in rows if t != land and t < land + 30)


def test_cast_rate_is_clamped_between_1_and_2():
    z = LoggedZiggs(1)
    t = z.timing
    assert t.cast_rate(0.7, 0.7) == 1 and t.cast_rate(0.7, 0.5) == 1  # never slower than the chrono
    assert abs(t.cast_rate(0.7, 1.05) - 1.5) < 1e-12
    assert t.cast_rate(0.7, 2.1) == 2  # never faster than 2x
    lock, mana = t.scaled_locks(0.7, 2.1)
    assert (lock, mana) == (0.8333 / 2, 0.8 / 2)


def stats_with(c, buffs, items=()):
    Simulator().itemStats(list(buffs) + list(items) + c.items, c)
    return c


def test_arcanist_members_and_team():
    # DA_Arcanist19: members get ArcanistAP (25/50/70%) only; everyone else NonArcanistAP (12/18/30%)
    import set19buffs
    from set19champs import Varus
    assert set19buffs.Arcanist.levels == [0, 2, 4, 6]
    for level, member, other in ((2, 1.25, 1.12), (4, 1.5, 1.18), (6, 1.7, 1.3)):
        z = stats_with(LoggedZiggs(1), [set19buffs.Arcanist(level)])
        v = stats_with(Varus(1, build=load_build(V)), [set19buffs.Arcanist(level)])
        assert (round(z.ap.stat, 4), round(v.ap.stat, 4)) == (member, other)
    assert stats_with(LoggedZiggs(1), [set19buffs.Arcanist(0)]).ap.stat == 1
    assert 'Arcanist' in LoggedZiggs(1).default_traits


def test_arcanist_ap_is_multiplied_by_rabadons():
    # Channel1 bonus AP: Rabadon's x1.15 multiplies the trait's AP too (I5)
    import set19buffs
    import set19items
    without = stats_with(LoggedZiggs(1), [], [set19items.RabadonsDeathcap()]).ap.stat
    with_ = stats_with(LoggedZiggs(1), [set19buffs.Arcanist(2)], [set19items.RabadonsDeathcap()]).ap.stat
    assert abs((with_ - without) - 0.25 * 1.15) < 1e-9


def test_arcanist_raises_bomb_damage():
    import set19buffs
    z = LoggedZiggs(1)
    ds = [dummy() for _ in range(3)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([], [set19buffs.Arcanist(2)], z, ds, 12)
    rows = [round(d[0], 2) for t, d, *_ in z.dmgVector]
    assert 225 in rows and 100 in rows and 50 in rows  # 180, 80, 40 x AP 1.25


def test_hyperpop_attack_speed_for_members():
    # DA_GlitterBomb19 (B23): GE_Glitterbomb19_UnitStats, members only: AS x (1 + BaseAttackSpeed) = 10/15/25/40%;
    # Hype doesn't scale it (PercentIncreasePerLevel 0)
    import pytest
    import set19buffs
    from set19champs import Draven
    for level, pct in ((0, 0), (2, 10), (3, 15), (4, 25), (5, 40)):
        z = Ziggs(1, build=load_build(V))
        Simulator().itemStats([set19buffs.Hyperpop(level)] + z.items, z)
        assert z.aspd.total('MultiplyAdditive') * 100 == pytest.approx(pct)
    d = Draven(1, build=load_build(V))
    Simulator().itemStats([set19buffs.Hyperpop(5)] + d.items, d)
    assert d.aspd.total('MultiplyAdditive') * 100 == 0
