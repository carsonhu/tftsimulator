"""Build-driven champions (docs/ASSUMPTIONS.md E11-E13, B1-B8): every number below is checked against the build
(rls-19.1.0.5973071) or the data asset it comes from."""
import pytest

from build_champion import BuildChampion, BuildRole, curve_at
from buildstore import BuildDataError, load_build
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


def make(key, level=2, **attrs):
    cls = type(f'T_{key}', (BuildChampion,), {'KEY': key, **attrs})
    return cls(level, build=load_build(V))


def combat_start(c):
    """Run preCombat (role effects) without simulating."""
    Simulator().itemStats(c.items, c)
    return c


def test_star_values_come_from_the_build():
    # B1: Ahri HealthMax 850 x 1 / 1.8 / 3.24; AD = AutoAttackDamage 30 / 45 / 67.5 (not a global x1.5)
    for level, hp, ad in ((1, 850, 30), (2, 1530, 45), (3, 2754, 67.5)):
        a = make('DA_Ahri19', level)
        assert a.hp.stat == pytest.approx(hp) and a.atk.stat == pytest.approx(ad)
        assert a.level == level and a.row('APDamage') == (28, 42, 400)[level - 1]


def test_base_stats_mana_range_and_cap():
    a = make('DA_Ahri19')
    assert (a.aspd.stat, a.armor.stat, a.mr.stat) == (0.8, 40, 40)
    assert (a.curMana, a.fullMana.stat) == (0, 30)
    a.aspd.modify('MultiplyAdditive', 100)
    assert a.attack_range == 4 and a.aspd.stat == 5  # B4: GE_AttackSpeedMax caps it
    assert a.role.key == 'MagicCaster' and a.role.archetype == 'Caster' and a.role.name == 'Magic Caster'
    assert a.timing.launch == 0.3067 and a.timing.cast_lock == 1


def test_caster_role_mana_from_the_build():
    # B5: MagicCaster: ManaPerAttack + 7, ManaPerSecond + 2 (CT_Role_Stats)
    a = combat_start(make('DA_Ahri19'))
    assert a.manaPerAttack.stat == 7 and a.manaRegen.stat == 2


def test_marksman_and_assassin_mana():
    v = combat_start(make('DA_Vayne19'))
    assert v.role.archetype == 'Marksman' and v.manaPerAttack.stat == 10 and v.manaRegen.stat == 0


@pytest.mark.parametrize('stage,bonus', [(2, 5), (3, 10), (4, 20), (5, 30), (6, 30)])
def test_fighter_attack_speed_by_stage(stage, bonus):
    # B6: FighterAttackSpeed (step curve) at the stage: keys 1 -> 1.05, 3 -> 1.10, 4 -> 1.20, 5 -> 1.30
    k = make('DA_Kayn19')
    assert k.role.archetype == 'Fighter'
    base = k.aspd.stat
    k.stage = stage
    combat_start(k)
    assert k.aspd.stat == pytest.approx(base * (1 + bonus / 100))
    assert k.manaPerAttack.stat == 10


def test_melee_without_attack_range_is_range_1():
    k = make('DA_Kayn19')
    assert k.attack_range == 1 and not k.ranged and 'default 1' in k.sources['attack_range']


def test_base_crit_is_the_owner_confirmed_value():
    # E12: no base crit in data; the owner confirmed 25% / 140% for Set 19
    a = make('DA_Ahri19')
    assert a.crit.stat == 0.25 and a.critDmg.stat == 1.4
    assert 'owner' in a.sources['crit_chance'] and a.excess_crit_ratio == 0.5


def test_missing_data_fails_loudly():
    with pytest.raises(BuildDataError, match='HealthMax'):
        make('DA_Locke19')  # no HealthMax in this build
    with pytest.raises(BuildDataError, match='star level 4'):
        make('DA_Ahri19', level=4)
    with pytest.raises(BuildDataError):
        make('DA_Ahri19').row('NoSuchRow')


def test_role_names_parse():
    assert BuildRole('AttackSpecialist_Ammo').archetype == 'Specialist'
    assert BuildRole('AttackSpecialist_Ammo').variant == 'Ammo'
    assert BuildRole('MagicTank_Manaless').archetype == 'Tank'


def test_curve_at():
    pts = [[1, 1.05], [3, 1.1], [4, 1.2], [5, 1.3], [10, 1.3]]
    assert [curve_at(pts, s) for s in (2, 3, 4, 6)] == [1.05, 1.1, 1.2, 1.3]
    assert curve_at([[0, 0], [3, 300]], 1, 'Linear') == 100


def test_an_itemless_ahri_runs_and_casts():
    # integration: build stats + role mana + build timing. First cast from attack and regen mana only.
    a = make('DA_Ahri19')
    Simulator().simulate([], [], a, [dummy() for _ in range(8)], 10)
    assert a.numCasts >= 1 and a.dmgVector
