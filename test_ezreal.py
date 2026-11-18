"""Ezreal end to end (champions/Ezreal.md): numbers from build rls-19.1.0.5973071; timing against the owner's 60 fps
PBE VOD4 (19-0-51-650, round 2-2: Ezreal 1*, Infinity Edge, Guinsoo's Rageblade, Titan's Resolve; combat start
f75964 from Guinsoo's stacks)."""
import set19buffs
import set19items
from buildstore import load_build
from set19champs import Ezreal
from simulator import Simulator
from test_timing import dummy
from timing import projectile_ticks, ticks_up

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedEzreal(Ezreal):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.releases, self.casts = [], []

    def onLaunch(self, opponents, items):
        self.releases.append(self.tick)
        super().onLaunch(opponents, items)

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(c, items=(), buffs=(), seconds=12, n=3):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = 0
        d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def test_build_numbers():
    e = LoggedEzreal(1)
    assert (e.curMana, e.fullMana.stat, e.aspd.stat, e.attack_range, e.atk.stat) == (0, 35, 0.75, 4, 40)
    assert (e.second_stage, e.shot_spawn, e.encore_spawn) == (0.6663, 0.1729, 0.319)
    assert (e.timing.cast_lock, e.timing.mana_lock) == (1.2, 1.1667)  # 36 and 35 ticks


def test_vod4_releases_before_the_first_cast():
    # VOD4 2-2: +7 mana at f75988, 76052, 76114 (12, 44, 75 ticks after combat start); 0/35 at f76174 (105).

    e = LoggedEzreal(1)

    fight(e, items=[set19items.TitansResolve(), set19items.InfinityEdge(), set19items.GuinsoosRageblade()])
    assert all(abs(x - v) <= 1 for x, v in zip(e.releases[:3], [12, 44, 75]))
    assert abs(e.casts[0] - 105) <= 2  # engine 107: the bar fills at the 4th release (106) and casts a tick later


def test_detonation_damage_and_splash():
    # Calc1 = 190 x AD + 30 x AP = 220 on the target, 0.33 x 220 on one adjacent enemy, at stage 2 (0.6663 s -> 20
    # ticks) + the missile's spawn (0.1729 s -> 6) + its flight (2200 units/s over 4 hexes)
    e = LoggedEzreal(1)
    rows = fight(e)
    c = e.casts[0]
    land = c + 20 + 6 + projectile_ticks(2200, 4)
    assert sorted(d for t, d in rows if t == land) == [round(0.33 * 220, 4), 220]
    assert not any(d == 220 for t, d in rows if t != land and t < land + 20)


def test_encore_adds_a_weaker_second_detonation():
    # Encore (2): CastAnim2's SecondCast missile at 0.319 s, x RecastEffectiveness 0.25
    e = LoggedEzreal(1)
    rows = fight(e, buffs=[set19buffs.Encore(2)])
    c = e.casts[0]
    second = c + 20 + ticks_up(0.319) + projectile_ticks(2200, 4)
    assert sorted(d for t, d in rows if t == second) == [round(0.33 * 220 * 0.25, 4), 55]


def stats_with(cls, trait):
    c = cls(1, build=load_build(V))
    Simulator().itemStats([trait] + c.items, c)
    return c


def test_heartsteel_team_bonuses():
    # DA_Heartsteel19 (1) SelflessBonus per fielded member, to every ally: Kayn +7% AD, Alune +7% AP, Aphelios +6% AS,
    # Ezreal +10% crit. (7): members also get StanBonus, the row x 1.5 (Ezreal's crit by the tooltip, owner ruling).
    from set19champs import Draven
    base = stats_with(Draven, set19buffs.Heartsteel(0, 0))
    every = 0b1111
    for level in (1, 7):  # a non-member gets the same at every level
        d = stats_with(Draven, set19buffs.Heartsteel(level, every))
        assert abs(d.bonus_ad.stat - base.bonus_ad.stat - 0.07) < 1e-9
        assert abs(d.ap.stat - base.ap.stat - 0.07) < 1e-9
        assert abs(d.crit.stat - base.crit.stat - 0.1) < 1e-9
        assert not d.heartsteel_bias
    nothing = stats_with(Draven, set19buffs.Heartsteel(3, 0))
    assert (nothing.bonus_ad.stat, nothing.crit.stat) == (base.bonus_ad.stat, base.crit.stat)
    e0 = stats_with(Ezreal, set19buffs.Heartsteel(0, 0))
    e1 = stats_with(Ezreal, set19buffs.Heartsteel(1, 0))  # he counts himself as fielded
    assert abs(e1.crit.stat - e0.crit.stat - 0.1) < 1e-9
    e7 = stats_with(Ezreal, set19buffs.Heartsteel(7, 0b0001))  # Kayn + himself, at (7)
    assert abs(e7.bonus_ad.stat - e0.bonus_ad.stat - 0.07 * 2.5) < 1e-9
    assert abs(e7.crit.stat - e0.crit.stat - 0.1 * 2.5) < 1e-9
    assert e7.trait_tier('DA_Heartsteel19') == 4  # (7) is level 4 (StanPercentIncrease 1.5)


def test_heartsteel_aphelios_attack_speed():
    from set19champs import Draven
    base = stats_with(Draven, set19buffs.Heartsteel(0, 0))
    d = stats_with(Draven, set19buffs.Heartsteel(1, 0b0100))
    assert abs(d.aspd.stat - base.aspd.stat - 0.06 * d.aspd.base) < 1e-6, (d.aspd.stat, base.aspd.stat, d.aspd.base)


def test_heartsteel_bias_upgrade():
    # GA_Ezreal19_Spell: a Bias at (3)+ deals x 1.25 (HeartsteelStan_PercentIncreasedAbilityDamage) on both hits;
    # casts 3, 6, ... (spell Stack % 3 == 0) also hit the enemies within 2 hexes (the extra-targets slider, 1)
    def detonations(trait, n=4):
        e = LoggedEzreal(1)
        rows = fight(e, buffs=[trait], seconds=30, n=n)
        land = [c + 20 + 6 + projectile_ticks(2200, 4) for c in e.casts]
        return [sorted(d for t, d in rows if t == x) for x in land[:4]]

    bias = 1 << set19buffs.Heartsteel.BIAS
    up = detonations(set19buffs.Heartsteel(3, bias))
    hit, splash = 220 * 1.25, round(0.33 * 220 * 1.25, 4)
    assert up[0] == up[1] == up[3] == [splash, hit]
    assert up[2] == [splash, splash, hit]
    for trait in (set19buffs.Heartsteel(3, 0), set19buffs.Heartsteel(1, bias)):  # not a Bias / below (3)
        assert detonations(trait)[2] == [round(0.33 * 220, 4), 220]
