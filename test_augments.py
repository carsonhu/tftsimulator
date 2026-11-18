"""The offensive combat augments (augments/combat.py): each one's numbers from build rls-19.1.0.5973071's augment rows,
its timing from its script (or its own delay row), checked on a simulated unit."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from set19champs import Ezreal, Lucian, Zoe
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


def run(champ, buffs=(), items=(), seconds=1.0, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 100
    Simulator().simulate(list(items), list(buffs), champ, ds, seconds)
    return ds


def lucian():
    c = Lucian(1, build=load_build(V))
    c.fullMana.base = 10 ** 6  # no casts: the stats alone
    return c


@pytest.mark.parametrize("cls, amp", [
    ("GlassCannonI", 0.16), ("GlassCannonII", 0.25), ("StrangeDuetI", 0.05), ("StrangeDuetII", 0.08),
    ("StrangeDuetIII", 0.14), ("ItsMeBaby", 0.15)])
def test_damage_amp(cls, amp):
    c = lucian()
    run(c, [getattr(set19buffs, cls)()])
    assert c.dmgMultiplier.stat == pytest.approx(1 + amp)


@pytest.mark.parametrize("cls, amp", [("Ascension", 0.35), ("PartialAscension", 0.2)])
def test_ascension(cls, amp):
    # +amp at 12 s (the row's ActivationDelay; the augments are effects only)
    c = lucian()
    run(c, [getattr(set19buffs, cls)()], seconds=11.9)
    assert c.dmgMultiplier.stat == pytest.approx(1)
    c = lucian()
    run(c, [getattr(set19buffs, cls)()], seconds=12.05)
    assert c.dmgMultiplier.stat == pytest.approx(1 + amp)


@pytest.mark.parametrize("cls, params, adap", [
    ("BattleOfTheBands", 0, 0.18), ("DoubleTrouble", 0, 0.25), ("HoldTheLine7", 0, 0.77), ("HoldTheLine5", 0, 0.55),
    ("EarlyLearnings", 0, 0.03), ("EarlyLearnings", 2, 0.13), ("EarlyLearnings", 4, 0.23),
    ("NoScoutNoPivot", 0, 0), ("NoScoutNoPivot", 3, 0.15), ("TonsOfStatsI", 0, 0.04), ("TonsOfStatsII", 0, 0.08)])
def test_ad_ap(cls, params, adap):
    c = lucian()
    run(c, [getattr(set19buffs, cls)(1, params)])
    assert (c.bonus_ad.stat, c.ap.stat) == (pytest.approx(1 + adap), pytest.approx(1 + adap))


def test_early_learnings_one_cost_double():
    z = Zoe(1, build=load_build(V))  # a 1-cost
    z.fullMana.base = 10 ** 6
    run(z, [set19buffs.EarlyLearnings(1, 1)])
    assert z.ap.stat == pytest.approx(1 + 2 * 0.08)


def test_tons_of_stats_mana_and_speed():
    c = lucian()
    c.fullMana.base = 10 ** 6
    run(c, [set19buffs.TonsOfStatsII()], seconds=0.1)
    assert c.curMana >= 8 and c.aspd.stat == pytest.approx(0.75 * 1.08)


@pytest.mark.parametrize("cls, at, step, start", [
    ("FocusedFire", 5, 0.04, 0.10), ("BaronsLair", 8, 0.04, 0), ("SubmitToThePit", 1, 0.03, 0)])
def test_timed_stacks(cls, at, step, start):
    # the first step at `at` seconds (WaitOnTimePassedInPhase), then one per interval
    params = 1 if cls == "SubmitToThePit" else 0  # in the center rows
    c = lucian()
    run(c, [getattr(set19buffs, cls)(1, params)], seconds=at - 0.05)
    assert c.bonus_ad.stat == pytest.approx(1 + start)
    c = lucian()
    run(c, [getattr(set19buffs, cls)(1, params)], seconds=at + 0.05)
    assert c.bonus_ad.stat == pytest.approx(1 + start + step)
    if cls != "FocusedFire":
        assert c.ap.stat == pytest.approx(1 + step)
    else:
        assert c.ap.stat == pytest.approx(1)


def test_submit_to_the_pit_by_range():
    c = lucian()  # range 4: outside the center rows by default
    run(c, [set19buffs.SubmitToThePit()], seconds=3)
    assert c.bonus_ad.stat == pytest.approx(1)


def test_soul_awakening():
    # 10 stacks of 1.5% AD and AP, the first 0.8 s in, then 12% of each damage as true damage
    c = lucian()
    run(c, [set19buffs.SoulAwakening()], seconds=9.7)
    assert c.ap.stat == pytest.approx(1 + 9 * 0.015)
    c = lucian()
    run(c, [set19buffs.SoulAwakening()], seconds=12)
    assert c.ap.stat == pytest.approx(1 + 10 * 0.015)


def test_attack_speed_and_mana():
    c = lucian()
    run(c, [set19buffs.Espresso()], seconds=11.9)
    assert c.aspd.stat == pytest.approx(0.75 * 1.1)
    c = lucian()
    run(c, [set19buffs.Espresso()], seconds=12.05)
    assert c.aspd.stat == pytest.approx(0.75 * 1.3)
    c = lucian()
    run(c, [set19buffs.ComebackStory(1, 40)])
    assert c.aspd.stat == pytest.approx(0.75 * (1 + 0.004 * 60))
    c = lucian()
    run(c, [set19buffs.ZekesHerald()])
    assert c.aspd.stat == pytest.approx(0.75 * 1.3)
    c = lucian()
    run(c, [set19buffs.ChaliceOfPower()])
    assert (c.ap.stat, c.manaRegen.stat) == (pytest.approx(1.25), 2 + 1)


def test_seraphims_staff():
    # +2 regen once the holder of Archangel's Staff has 110% bonus AP (an AP multiplier of 2.1)
    c = lucian()
    run(c, [set19buffs.SeraphimsStaff()], items=[set19items.ArchangelsStaff()], seconds=2)
    assert c.manaRegen.stat == 2 + 1  # Archangel's 1 regen, AP not there yet
    c = lucian()
    c.ap.modify("+", 1.2)
    run(c, [set19buffs.SeraphimsStaff()], items=[set19items.ArchangelsStaff()], seconds=1)
    assert c.manaRegen.stat == 2 + 1 + 2
    c = lucian()
    c.ap.modify("+", 1.2)
    run(c, [set19buffs.SeraphimsStaff()], seconds=1)  # no Archangel's: nothing
    assert c.manaRegen.stat == 2


def test_dig_on_this():
    # Jazz (2) with 5 traits: +5%; Dig on This: +150% of that for a Jazz member
    c = lucian()
    run(c, [set19buffs.Jazz(2, 5), set19buffs.DigOnThis()])
    assert c.dmgMultiplier.stat == pytest.approx(1 + 0.05 * 2.5)


def test_heartsteel_augments():
    # Ezreal fielded (bit 3) and a Bias (bit 4) at Heartsteel (3): his crit bonus; Big Solo +150% of it for a Bias;
    # Small Squad +100% with 3 or fewer Heartsteel champions fielded
    def crit(buffs):
        e = Ezreal(1, build=load_build(V))
        e.fullMana.base = 10 ** 6
        run(e, buffs)
        return e.crit.stat - 0.25
    hs = lambda: set19buffs.Heartsteel(3, (1 << 3) | (1 << 4))
    base = crit([hs()])
    assert crit([hs(), set19buffs.BigSolo()]) == pytest.approx(base * (1 + 1.5) / 1)
    assert crit([hs(), set19buffs.SmallSquad()]) == pytest.approx(base * 2)


def test_sunder_and_shred():
    c = lucian()
    ds = run(c, [set19buffs.Sunder30(), set19buffs.Shred30()])
    assert all(d.armor.stat == pytest.approx(70) and d.mr.stat == pytest.approx(70) for d in ds)


@pytest.mark.parametrize("items, n", [
    ((), 0), (("Spatula",), 1), (("FryingPan",), 1), (("TacticiansCrown",), 2), (("TacticiansCape",), 2),
    (("JazzEmblem",), 1), (("Spatula", "TacticiansShield"), 3), (("InfinityEdge",), 0)])
def test_urf_counts_spatula_items(items, n):
    # GE_URF x MMC_NumSpatulaItemsOnHolder: 1 per Spatula, Frying Pan or emblem, 2 per Tactician's item
    c = lucian()
    held = [getattr(set19items, i)() for i in items]
    run(c, [set19buffs.URF()], items=held)
    emblem_as = 0.1 if "JazzEmblem" in items else 0
    assert c.aspd.stat == pytest.approx(0.75 * (1 + emblem_as + 0.2 * n))
    assert c.manaRegen.stat == 2 + 3 * n
