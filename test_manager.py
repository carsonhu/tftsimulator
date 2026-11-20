"""Manager (DA_Manager19), a team trait: the ally starting in the Spotlight Hex gains 6% AD and AP at combat start and
every 5 s (stacking), and from (3) 8 mana each time (CT_Manager19; GA_Manager19_StatGain, traits/manager.py)."""
import pytest

import set19buffs
import sim_entry
from set19champs import Draven, Varus
from simulator import Simulator
from test_timing import dummy


def pulses(level, place=0, seconds=11):
    """(tick, bonus AD %, AP %) whenever they change, and the mana grants (tick, amount), for Varus (not a Manager)."""
    v = Varus(1)
    log, mana, orig_update, orig_add = [], [], v.update, v.addMana

    def upd(opp, items, time):
        before = (v.bonus_ad.total('+'), v.ap.total('+'))
        orig_update(opp, items, time)
        if (v.bonus_ad.total('+'), v.ap.total('+')) != before:
            log.append((v.tick, round(v.bonus_ad.total('+') * 100, 6), round(v.ap.total('+') * 100, 6)))

    def add(amount, time=None):
        if amount == 8:
            mana.append((v.tick, amount))
        orig_add(amount, time)

    v.update, v.addMana = upd, add
    start = (round(v.bonus_ad.total('+') * 100, 6), round(v.ap.total('+') * 100, 6))
    Simulator().simulate([], [set19buffs.Manager(level, place)], v, [dummy()], seconds)
    return start, log, mana


def test_stacking_ad_ap_every_five_seconds():
    start, log, mana = pulses(2)
    # combat start's pulse lands before the first update; then 5 s (150 ticks) and 10 s
    assert [(t, ad - start[0], ap - start[1]) for t, ad, ap in log] == [(150, 12, 12), (300, 18, 18)]
    assert mana == []  # (2): no mana


def test_mana_from_three():
    _, _, mana = pulses(3)
    assert mana == [(0, 8), (150, 8), (300, 8)]


def test_outside_the_hex_nothing():
    start, log, mana = pulses(4, place=1)
    assert log == [] and mana == []


def test_offered_as_team_traits():
    team = {t['cls']: t for t in sim_entry.get_catalog()['teamBuffs']}
    for cls in ('Arcanist', 'Choreographer', 'Swiftstriker', 'Composer', 'Prodigy', 'Jazz', 'Manager'):
        assert cls in team
    assert team['Composer']['number'] == {'min': 0, 'max': 5, 'default': 0}
    assert team['Jazz']['number']['default'] == 5
    assert team['Manager']['options'] == ['Yes', 'No']
    assert team['Arcanist']['scales'] and not team['Swiftstriker']['scales']


@pytest.mark.parametrize('cls, stat, value', [
    ('Arcanist', 'ap', 0.12), ('Prodigy', 'manaRegen', 1), ('Choreographer', 'dmgMultiplier', 0.06)])
def test_team_halves_reach_a_non_member(cls, stat, value):
    # Draven is none of these (Illbeats, Trickshot): the non-member numbers at the first breakpoint (CT_<trait>19)
    def stat_with(buffs):
        v = Draven(1)
        Simulator().itemStats(buffs + v.items, v)  # role stats and the like apply here too: compare like with like
        return getattr(v, stat).stat

    trait = getattr(set19buffs, cls)
    assert stat_with([trait(trait.levels[1])]) - stat_with([]) == pytest.approx(value)


def test_team_traits_slice_only_what_changes_a_non_member():
    rows = {sim_entry._row_label(b): (b.level, b.params) for b in sim_entry.team_sweep_buffs(
        [('Heartsteel', 1, 0), ('Swiftstriker', 2, 0), ('Arcanist', 2, 0), ('Composer', 0, 0)])}
    # Heartsteel: each member fielded, the level unchanged; Swiftstriker: only off; Arcanist: its other levels;
    # Composer (off): on
    assert rows == {'Heartsteel (+Kayn)': (1, 1), 'Heartsteel (+Alune)': (1, 2), 'Heartsteel (+Aphelios)': (1, 4),
                    'Heartsteel (+Ezreal)': (1, 8), 'Swiftstriker 0': (0, 0), 'Arcanist 0': (0, 0),
                    'Arcanist 4': (4, 0), 'Arcanist 6': (6, 0), 'Composer': (1, 0)}
    # a ticked member's row unticks it
    assert sim_entry._row_label(sim_entry.team_sweep_buffs([('Heartsteel', 1, 8)])[3]) == 'Heartsteel (-Ezreal)'


def test_trait_slice_leaves_team_traits_to_their_own():
    cfg = {'buffs': [['Classical', 0, 0], ['Arcanist', 2, 0]], 'team': ['Arcanist']}
    _, trait = sim_entry._slice_inputs('Trait', cfg)
    _, team = sim_entry._slice_inputs('Team Traits', cfg)
    assert {type(b).__name__ for b in trait} == {'Classical'}
    assert {type(b).__name__ for b in team} == {'Arcanist'}


def test_heartsteel_member_rows():
    # Ezreal (a member) at Heartsteel 3 with Ezreal + Bias ticked: the other levels that differ (0, 7), the Bias
    # unticked, and each other member fielded; never his own tick box, never (1) or (5)
    rows = [(sim_entry._row_label(b), b.level, b.params) for b in
            sim_entry.trait_sweep_buffs([('Heartsteel', 3, 24)], champ_key='DA_Ezreal19')]
    assert rows == [('Heartsteel 0', 0, 24), ('Heartsteel 7', 7, 24), ('Heartsteel 3 (No Bias)', 3, 8),
                    ('Heartsteel 3 (+Kayn)', 3, 25), ('Heartsteel 3 (+Alune)', 3, 26), ('Heartsteel 3 (+Aphelios)', 3, 28)]
    # below (3) the Bias row is at (3)
    assert ('Heartsteel 3 (No Bias)', 3, 8) in [(sim_entry._row_label(b), b.level, b.params) for b in
                                                sim_entry.trait_sweep_buffs([('Heartsteel', 0, 24)], 'DA_Ezreal19')]
