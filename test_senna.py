"""Senna end to end (champions/Senna.md): numbers from build rls-19.1.0.5973071; mana locks against the owner's 60 fps
PBE VOD2 (16-35-16-966, f25637-28024)."""
from buildstore import load_build
from set19champs import Senna
from simulator import Simulator
from test_timing import dummy
from timing import projectile_ticks, ticks_up

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedSenna(Senna):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.releases, self.casts = [], []

    def onLaunch(self, opponents, items):
        self.releases.append(self.tick)
        super().onLaunch(opponents, items)

    def performAbility(self, opponents, items, time):
        self.casts.append((self.tick, 'rip' if self.marked else 'blast'))
        super().performAbility(opponents, items, time)
        self.casts[-1] += (self.timing.cast_lock, self.timing.mana_lock)


def fight(c, seconds=20, n=3):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = 0
        d.mr.base = 0
    Simulator().simulate([], [], c, ds, seconds)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_locks():
    s = LoggedSenna(1)
    assert (s.curMana, s.fullMana.stat, s.aspd.stat, s.attack_range, s.atk.stat) == (0, 20, 0.75, 4, 55)
    assert s.timing.crit_animation == (0.6364, 3)
    # CastAnim1 Unlock 1.1984 s -> 36 ticks, CastAnim2 0.9864 s -> 30 ticks; cast lock one tick more
    assert [round(x * 30, 6) for x in s.locks[s.BLAST]] == [37, 36]
    assert [round(x * 30, 6) for x in s.locks[s.RIP]] == [31, 30]


def test_crit_animation_weights_the_windup():
    # B17: normal attack 0.531 s, crit attack 0.6364 s (neither stretches: the animations are 3.3 and 3 s long)
    t = LoggedSenna(1).timing
    period = 40  # 0.75 AS
    assert [t.release_ticks(period, crit=p) for p in (0, 0.25, 1)] == [16, 17, 20]  # 15.93, 16.72, 19.09


def test_casts_alternate_blast_and_detonation():
    s = LoggedSenna(1)
    rows = fight(s)
    kinds = [k for _, k, *_ in s.casts]
    assert kinds[:4] == ['blast', 'rip', 'blast', 'rip']
    (b, _, *bl), (r, _, *rl) = s.casts[:2]
    assert [round(x * 30, 6) for x in bl] == [37, 36] and [round(x * 30, 6) for x in rl] == [31, 30]
    # blast: 140 x AD + 25 x AP = 165 at the missile's arrival (0.7859 s -> 24 ticks, 4000 units/s over 4 hexes)
    assert (b + ticks_up(0.7859) + projectile_ticks(4000, 4), 165) in rows
    # detonation: 1.5 x 165 at the Damage event (0.2851 s -> 9 ticks)
    assert (r + 9, 247.5) in rows
    # after it, +8% damage amp: an attack's expected damage 55 x 1.1 (crit) x 1.08
    later = [d for t, d in rows if r + 9 < t < s.casts[2][0] and d not in (165, 247.5)]
    assert later and all(abs(d - 55 * 1.1 * 1.08) < 1e-6 for d in later)


def test_release_after_each_cast():
    # cast lock then a fresh attack: 37 + 17 after a blast, 31 + 17 after a detonation (25% crit: windup 16.72)
    s = LoggedSenna(1)
    fight(s)
    for c, kind, *_ in s.casts[:4]:
        nxt = min(r for r in s.releases if r > c)
        assert nxt - c == (37 if kind == 'blast' else 31) + 17


def stats_with(c, buffs, items=()):
    Simulator().itemStats(list(buffs) + list(items) + c.items, c)
    return c


def test_hitmaker_base_and_big_shot():
    # DA_Hitmaker19: every member AttackDamage + 12%; a Big Shot also + 20% (2) / 35% (4)
    import set19buffs
    from set19champs import Ziggs
    assert set19buffs.Hitmaker.levels == [0, 2, 4]
    for level, big in ((2, 1.32), (4, 1.47)):
        assert round(stats_with(LoggedSenna(1), [set19buffs.Hitmaker(level, 1)]).bonus_ad.stat, 4) == big
        assert round(stats_with(LoggedSenna(1), [set19buffs.Hitmaker(level, 0)]).bonus_ad.stat, 4) == 1.12
    assert stats_with(LoggedSenna(1), [set19buffs.Hitmaker(0, 1)]).bonus_ad.stat == 1
    z = Ziggs(1, build=load_build(V))  # not a Hitmaker: nothing
    assert stats_with(z, [set19buffs.Hitmaker(2, 1)]).bonus_ad.stat == 1
    assert 'Hitmaker' in LoggedSenna(1).default_traits


def test_hitmaker_ad_is_multiplied_by_deathblade():
    import set19buffs
    import set19items
    base = stats_with(LoggedSenna(1), [], [set19items.Deathblade()]).bonus_ad.stat
    with_ = stats_with(LoggedSenna(1), [set19buffs.Hitmaker(2, 1)], [set19items.Deathblade()]).bonus_ad.stat
    assert abs((with_ - base) - 0.32 * 1.15) < 1e-9


def test_hitmaker_raises_blast_damage():
    # 140 x AD with AD 1.32 + 25 x AP = 209.8
    import set19buffs
    s = LoggedSenna(1)
    ds = [dummy() for _ in range(3)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([], [set19buffs.Hitmaker(2, 1)], s, ds, 10)
    assert any(abs(d[0] - 209.8) < 1e-6 for t, d, *_ in s.dmgVector)


def test_true_damage_a_side():
    # VOD4 1-4 (True Damage (3), A-Side): every damage number is followed by a true one of 18% of it, rounded down
    # (30 -> 5, 22 -> 4, 18 -> 3, 12 -> 2, 35 -> 6, 25 -> 4, magic 7 -> 1). (5): 30% (owner: follow the tooltip).
    import set19buffs
    assert set19buffs.TrueDamage.levels == [0, 3, 5]
    assert 'TrueDamage' in LoggedSenna(1).default_traits
    for level, pct in ((3, 0.18), (5, 0.3)):
        s = LoggedSenna(1)
        ds = [dummy() for _ in range(3)]
        for d in ds:
            d.armor.base = 100  # the bonus is a share of the damage after resistances
        Simulator().simulate([], [set19buffs.TrueDamage(level)], s, ds, 10)
        rows = [(t, d) for t, d, *_ in s.dmgVector]
        phys = [(t, d[0]) for t, d in rows if d[1] == 'physical']
        true = [(t, d[0]) for t, d in rows if d[1] == 'true']
        assert len(phys) == len(true) and phys
        assert all(tt == tp and abs(vt - pct * vp) < 1e-9 for (tp, vp), (tt, vt) in zip(phys, true))
    s = LoggedSenna(1)
    Simulator().simulate([], [set19buffs.TrueDamage(0)], s, [dummy()], 5)
    assert not any(d[1] == 'true' for t, d, *_ in s.dmgVector)
