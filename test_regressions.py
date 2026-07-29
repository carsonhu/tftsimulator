"""Regression tests for bugs found while tuning the simulator.

Each of these reproduces a defect that was live in set 17; keep them green when
porting to a new set.
"""
import pytest

import set17buffs
import set17champs
import set17items
import status
from simulator import Simulator


def make_dummy(armor=100, mr=100):
    d = set17champs.DummyTank(1)
    d.armor.base = armor
    d.mr.base = mr
    return d


class TestShredCrossover:
    """ArmorReduction/MRReduction used to clamp against the *other* resist's
    multiplier, so an armor shred landing after a bigger MR shred inherited the
    MR value (and vice versa)."""

    def test_armor_shred_ignores_existing_mr_shred(self):
        opp = make_dummy()
        attacker = make_dummy()
        opp.applyStatus(status.MRReduction("big"), attacker, 0, 30, 0.5)
        opp.applyStatus(status.ArmorReduction("small"), attacker, 0, 30, 0.8)
        assert opp.armor.stat == pytest.approx(80.0)
        assert opp.mr.stat == pytest.approx(50.0)

    def test_mr_shred_ignores_existing_armor_shred(self):
        opp = make_dummy()
        attacker = make_dummy()
        opp.applyStatus(status.ArmorReduction("big"), attacker, 0, 30, 0.5)
        opp.applyStatus(status.MRReduction("small"), attacker, 0, 30, 0.8)
        assert opp.mr.stat == pytest.approx(80.0)
        assert opp.armor.stat == pytest.approx(50.0)

    def test_strongest_armor_shred_wins(self):
        # Distinct names, i.e. two different shred sources - the real case.
        opp = make_dummy()
        attacker = make_dummy()
        opp.applyStatus(status.ArmorReduction("weak"), attacker, 0, 30, 0.8)
        opp.applyStatus(status.ArmorReduction("strong"), attacker, 0, 30, 0.6)
        assert opp.armor.stat == pytest.approx(60.0)

    @pytest.mark.xfail(
        reason="reapplicationEffect clamps to the stored self.reduction and "
        "never stores the new params, so re-applying a STRONGER shred under an "
        "existing name keeps the weaker value. Latent today because every "
        "source uses its own status name; would bite if a set-18 source "
        "refreshes itself at varying magnitudes.",
        strict=True,
    )
    def test_stronger_reapplication_under_same_name_wins(self):
        opp = make_dummy()
        attacker = make_dummy()
        opp.applyStatus(status.ArmorReduction("same"), attacker, 0, 30, 0.8)
        opp.applyStatus(status.ArmorReduction("same"), attacker, 0, 30, 0.6)
        assert opp.armor.stat == pytest.approx(60.0)


class TestIoniaEnlightenedOverride:
    """extraBuff referenced a `champion` name that does not exist at
    construction time, so any non-zero Lvl Override crashed the app."""

    def test_zero_override_constructs(self):
        set17buffs.IoniaEnlightened(3, 0)

    def test_nonzero_override_constructs(self):
        buff = set17buffs.IoniaEnlightened(3, 2)
        assert buff.level_override == 2

    def test_override_applies_to_champion(self):
        champ = set17champs.DummyTank(1)
        set17buffs.IoniaEnlightened(3, 5).performAbility("preCombat", 0, champ)
        assert champ.level == 5

    def test_no_override_leaves_level_alone(self):
        champ = set17champs.DummyTank(3)
        set17buffs.IoniaEnlightened(3, 0).performAbility("preCombat", 0, champ)
        assert champ.level == 3


class TestNumTraitsDefault:
    """Trait-count-scaling buffs read champion.num_traits, which only the
    Champion Selector page used to set."""

    def test_champion_has_num_traits(self):
        assert set17champs.DummyTank(1).num_traits == 6


class TestItemHash:
    """Item.__hash__ called a hash_function() that never existed."""

    def test_item_is_hashable(self):
        assert isinstance(hash(set17items.InfinityEdge()), int)


class TestOpponentsStayInert:
    """The frame loop skips work for opponents on the grounds that they never
    act. Assert that stays true."""

    def test_opponents_never_attack_or_cast(self):
        champ = set17champs.Jinx(2)
        opponents = [make_dummy() for _ in range(8)]
        Simulator().simulate([], [], champ, opponents, 10.0, frameRate=30)
        for opp in opponents:
            assert opp.numAttacks == 0
            assert opp.numCasts == 0

    def test_shred_still_reaches_every_opponent(self):
        champ = set17champs.Jinx(2)
        opponents = [make_dummy() for _ in range(8)]
        Simulator().simulate(
            [], [set17buffs.Shred30(1, 0)], champ, opponents, 10.0, frameRate=30
        )
        for opp in opponents:
            assert opp.armor.stat == pytest.approx(70.0)
            assert opp.mr.stat == pytest.approx(70.0)

    def test_corrosion_still_ticks_down_resists(self):
        champ = set17champs.Jinx(2)
        opponents = [make_dummy() for _ in range(8)]
        Simulator().simulate(
            [], [set17buffs.Corrosion(1, 0)], champ, opponents, 10.0, frameRate=30
        )
        # 4 armour/MR per 2s tick, so it must have dropped well below 100
        for opp in opponents:
            assert opp.armor.stat < 100
            assert opp.mr.stat < 100
