"""buildstore reads builds/ without editing numbers, and fails loudly on missing names."""
import pytest

from buildstore import BuildDataError, list_builds, load_build

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


def test_newest_is_default():
    assert load_build().version == list_builds()[0]['version']


def test_ahri_values_match_the_build():
    a = load_build(V).champion('DA_Ahri19')
    assert a.row('APDamage') == (28, 42, 400)
    assert a.row('APDamage', star=3) == 400
    assert a.hp == (850, 1530, 2754)
    assert a.ad == (30, 45, 67.5)
    assert a.attack_speed == 0.8 and a.mana_max == 30 and a.mana_start == 0
    assert a.role == 'MagicCaster'


def test_role_mana():
    b = load_build(V)
    assert b.role('MagicCaster').modifier('ManaPerAttack') == 7
    assert b.role('MagicCaster').modifier('ManaPerSecond') == 2
    assert b.role('AttackMarksman').modifier('ManaPerAttack') == 10


def test_missing_names_raise_with_the_build():
    b = load_build(V)
    with pytest.raises(BuildDataError, match=V):
        b.champion('DA_Ahri19').row('NoSuchRow')
    with pytest.raises(BuildDataError):
        b.champion('DA_NotAChampion')
    with pytest.raises(BuildDataError):
        load_build('no-such-build')


def test_linear_curve_points_are_interpolated():
    # Hyperpop BaseHealth keys are (0,0),(3,300): point 1 must be 100, not 0
    pts = dict(load_build(V).trait('DA_GlitterBomb19').row('BaseHealth'))
    assert pts[1] == 100 and pts[2] == 200 and pts[3] == 300
