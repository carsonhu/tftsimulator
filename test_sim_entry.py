"""The site's JSON entry point on the Set 19 registries (E16): catalog, champion info and a run, with a temporary
build-driven champion registered for the test."""
import json

import pytest

import set19champs
import sim_entry
from build_champion import BuildChampion
from simulator import Simulator


class AhriForTest(BuildChampion):
    KEY = 'DA_Ahri19'


@pytest.fixture
def registered(monkeypatch):
    monkeypatch.setattr(set19champs, 'AhriForTest', AhriForTest, raising=False)
    monkeypatch.setattr(set19champs, 'champ_list', ['AhriForTest'])


def cfg(**kw):
    return {'champ': 'AhriForTest', 'level': 2, 'items': [], 'buffs': [], 'enemy': {'hp': 1800, 'armor': 100, 'mr': 100},
            't': 10, 'slice': 'Craftable', 'stage': '4-1'} | kw


def test_catalog_with_no_champions(monkeypatch):
    monkeypatch.setattr(set19champs, 'champ_list', [])
    cat = json.loads(sim_entry.catalog_json())
    assert cat['champions'] == [] and 'blackthorn' not in cat and 'Wisp' not in cat['slices']
    assert cat['defaults']['frameRates'] == [30]


def test_catalog_info_and_run(registered):
    cat = json.loads(sim_entry.catalog_json())
    assert [c['name'] for c in cat['champions']] == ['AhriForTest']
    info = json.loads(sim_entry.champ_info_json(json.dumps(cfg())))
    assert info['stats']['role'] == 'Magic Caster' and info['stats']['castTime'] == 1
    assert info['stats']['build'].startswith('rls-19.1.0')
    out = json.loads(sim_entry.run_json(json.dumps(cfg())))
    import set19items
    listed = {getattr(set19items, c).display_name for c in set19items.offensive_craftables}
    assert {r['extra'] for r in out['rows']} == listed | {'Base'}
    assert out['rows'][0]['dps']['10-20'] > 0


def test_unknown_champion_is_refused():
    with pytest.raises(KeyError, match='not a Set 19 champion'):
        sim_entry.run_slice(cfg(champ='Sett'))  # a tank: out of scope (roster.json)


def test_catalog_lists_the_builds_for_the_picker():
    # B9: the page offers every imported build, newest first; the value is the version cfg["build"] names. A build
    # made from patch notes (B33) would say so and sort by the notes' date
    cat = json.loads(sim_entry.catalog_json())
    assert cat['builds'][:3] == [
        {'version': 'rls-19.1.0.6011486.Set19.Shipping.pbe', 'label': 'PBE 19.1 #6011486 (Nov 20 20:35)'},
        {'version': 'rls-19.1.0.6005555.Set19.Shipping.pbe', 'label': 'PBE 19.1 #6005555 (Nov 20 14:37)'},
        {'version': 'rls-19.1.0.5995286.Set19.Shipping.pbe', 'label': 'PBE 19.1 #5995286 (Nov 19 12:47)'}]


def test_a_run_uses_the_build_it_names(registered):
    out = json.loads(sim_entry.champ_info_json(json.dumps(cfg(build='rls-19.1.0.5973071.Set19.Shipping.pbe'))))
    assert out['stats']['build'] == 'rls-19.1.0.5973071.Set19.Shipping.pbe'
    with pytest.raises(KeyError, match='no-such-build'):
        sim_entry.champ_info_json(json.dumps(cfg(build='no-such-build')))


def test_the_worker_loads_every_module():
    """The browser loads only the modules worker.js lists (PY_FILES): a module missing there fails only on the page."""
    import glob
    import os
    import re
    here = os.path.dirname(os.path.abspath(__file__))
    listed = set(re.findall(r'"([\w/]+\.py)"', open(os.path.join(here, 'worker.js'), encoding='utf-8').read()))
    for pkg in ('items', 'traits', 'helpers'):
        for path in glob.glob(os.path.join(here, pkg, '*.py')):
            assert f'{pkg}/{os.path.basename(path)}' in listed
    assert 'registry.py' in listed

def test_the_worker_loads_every_top_level_module():
    """Every engine module at the top level is in worker.js's PY_FILES (tests, the local server and pytest's setup
    are not loaded)."""
    import glob
    import os
    import re
    here = os.path.dirname(os.path.abspath(__file__))
    listed = set(re.findall(r'"([\w/]+\.py)"', open(os.path.join(here, 'worker.js'), encoding='utf-8').read()))
    for path in glob.glob(os.path.join(here, '*.py')):
        name = os.path.basename(path)
        if not name.startswith(('test_', 'verify_')) and name not in ('conftest.py', 'serve.py', '__init__.py'):
            assert name in listed, name


def test_the_number_of_targets_reaches_an_area_champion_only():
    # the page's 'Number of targets' (layout.py, owner 2026-11-18): the catalog gives the default and which champions
    # show it (AREA); Varus's splash hits each target, so more targets, more damage. Draven's damage doesn't depend
    # on it (no slider): any value runs the default, and Titanic Hydra always hits one enemy next to the target
    cat = json.loads(sim_entry.catalog_json())
    assert cat['defaults']['layout'] == {'targets': 2, 'max': 7}
    area = {c['name'] for c in cat['champions'] if c['area']}
    assert area == {'Varus', 'Ziggs', 'Ezreal', 'Malzahar', 'Kayle', 'Bard', 'RenataGlasc', 'Briar', 'Katarina', 'Kayn', 'Qiyana', 'Yuumi', 'Yone', 'Tristana', 'Mel', 'Jinx', 'Ahri', 'Jhin', 'Vladimir', 'Alune', 'Yasuo', 'Aphelios'}

    def dps(champ, slice_, extra, layout):
        out = json.loads(sim_entry.run_json(json.dumps(cfg(champ=champ, level=1, slice=slice_, layout=layout))))
        return next(r['dps']['20-30'] for r in out['rows'] if r['extra'] == extra)

    assert dps('Varus', 'Craftable', 'Base', {'targets': 5}) > dps('Varus', 'Craftable', 'Base', None) \
        == dps('Varus', 'Craftable', 'Base', {'targets': 2}) > dps('Varus', 'Craftable', 'Base', {'targets': 1})
    assert dps('Draven', 'Artifact', 'Titanic Hydra (1 adjacent)', {'targets': 7}) == dps('Draven', 'Artifact', 'Titanic Hydra (1 adjacent)', None)


def test_trait_rows_name_their_level_and_use_their_own_numbers():
    # owner, 2026-11-18: "Trickshot 2", "Trickshot 3", ...; each row's ratio is its own DPS over NoItem's (rows used to
    # share one by name, so every level of a trait showed the last one's)
    out = json.loads(sim_entry.run_json(json.dumps(cfg(champ='Gnar', level=1, slice='Trait', t=30,
                                                       buffs=[['Pentakill', 0, 0], ['Trickshot', 0, 0]]))))
    rows = {r['extra']: r for r in out['rows']}
    assert {'Pentakill 3', 'Pentakill 5', 'Pentakill 7', 'Trickshot 2', 'Trickshot 3', 'Trickshot 4', 'Base'} == set(rows)
    base = rows['Base']['dps']['20-30']
    for r in rows.values():
        assert r['ratio']['20-30'] == round(r['dps']['20-30'] / base, 2)
    assert len({rows[f'Pentakill {n}']['ratio']['20-30'] for n in (3, 5, 7)}) == 3


def test_dps_columns_average_over_fight_end_times():
    # owner, 2026-11-18: each column is the average of (damage dealt by T) / T for T spread over the window; a hit at t
    # counts ln(b / max(t, a)) / (b - a): fully before the window, partly inside, not at all after it
    hits = [(5.0, (100, 'magical')), (25.0, (300, 'magical')), (31.0, (1000, 'magical'))]
    import math
    expected = (100 * math.log(30 / 20) + 300 * math.log(30 / 25)) / 10
    assert sim_entry._dps_window(hits, 20, 30) == pytest.approx(expected)  # below 10: not truncated
    cat = json.loads(sim_entry.catalog_json())
    assert [w['key'] for w in cat['dpsWindows']] == ['10-20', '20-30'] and cat['headline'] == '20-30'


def test_champion_menu_by_cost_then_name():
    # owner, 2026-11-18: the menu groups champions by shop cost, then name; a hero augment unit takes its base
    # unit's cost (Olaf, 1); the page still opens on the first by name
    cat = json.loads(sim_entry.catalog_json())
    order = [(c['cost'], c['label'].lower()) for c in cat['champions']]
    assert order == sorted(order) and all(c['cost'] > 0 for c in cat['champions'])
    assert next(c['cost'] for c in cat['champions'] if c['name'] == 'OlafHeroAugment') == 1
    assert cat['defaultChampion'] == sorted(c['name'] for c in cat['champions'])[0]


def test_cards_come_from_the_build():
    # hovering an item, augment or trait row shows its card: the build's name, kind, stat line, text and breakpoints
    import set19buffs
    import set19items
    cards = json.loads(sim_entry.cards_json(json.dumps({})))
    assert cards['BlueBuff'] == {'key': 'DA_BlueBuff', 'name': 'Blue Buff', 'kind': 'Craftable',
                                 'stats': [['15%', 'AD'], ['15%', 'AP'], ['6', 'ManaRegen']],
                                 'text': 'Combat Start: Gain 10 Mana.', 'tiers': []}
    # every stat tag has its glyph (tools/icons.py); Steadfast Heart's "250" (not simulated) has no icon in the line
    glyphs = set(json.load(open('icons/stats/index.json')))
    tags = {t for c in cards.values() for v, t in c['stats']}
    assert {t.lower() for t in tags if t} <= glyphs and sim_entry._stat_part('250') == ['250', None]
    assert cards['GlassCannonI']['kind'] == 'Silver' and '16% Damage Amp' in cards['GlassCannonI']['text']
    assert [t['threshold'] for t in cards['Arcanist']['tiers']] == [2, 4, 6]
    rows = (set19items.offensive_craftables + set19items.artifacts + set19items.radiants + set19items.emblems
            + set19buffs.class_buffs + set19buffs.augments)
    # the two generic debuff rows (Sunder / Shred 30%) are not in the client, so they have no card
    assert [c for c in rows if c not in cards] == ['Sunder30', 'Shred30']
    old = json.loads(sim_entry.cards_json(json.dumps({'build': 'rls-19.1.0.5973071.Set19.Shipping.pbe'})))
    assert 'BlueBuff' in old


def test_takedowns_slice_compares_counts_against_the_pages():
    # owner, 2026-11-19: 0, 24, 48 and 96 takedowns, the page's own count as the NoItem row (so not twice)
    cfg = {"champ": "Viego", "level": 1, "items": ["NoItem"] * 3, "buffs": [], "slice": "Takedowns",
           "takedowns": 24, "enemy": {"hp": 1800, "armor": 100, "mr": 100}}
    rows = {r["extra"]: r for r in sim_entry.run_slice(cfg)["rows"]}
    assert set(rows) == {"Base", "0 takedowns", "48 takedowns", "96 takedowns"}
    assert rows["0 takedowns"]["ratio"]["20-30"] < 1 < rows["48 takedowns"]["ratio"]["20-30"]
    assert rows["96 takedowns"]["extraParams"] == 96
    viego = next(c for c in sim_entry.get_catalog()["champions"] if c["name"] == "Viego")
    assert viego["takedowns"] and "Takedowns" in sim_entry.get_catalog()["slices"]
    # a Cappa Juice in a slot reads the row's count too (its stats are applied after the row's)
    cfg.update(champ="Ezreal", items=["CappaJuice", "NoItem", "NoItem"])
    rows = {r["extra"]: r for r in sim_entry.run_slice(cfg)["rows"]}
    assert rows["0 takedowns"]["ratio"]["20-30"] < 1 < rows["96 takedowns"]["ratio"]["20-30"]


def test_neeko_asks_for_her_kill_ap():
    # owner, 2026-11-19: the page highlights the AP box (dummies never die, so her kill passive's AP is the user's)
    champs = {c["name"]: c for c in sim_entry.get_catalog()["champions"]}
    assert list(champs["Neeko"]["askBonus"]) == ["ap"] and champs["Ezreal"]["askBonus"] == {}


def test_emblem_slice():
    # owner, 2026-11-20: no Spatula or Frying Pan; an emblem row runs its trait at a level ("Beach Pop Emblem (3)"), a
    # dropdown of the trait's levels, default the buff bar's level or else the lowest; an emblem of the unit's own trait
    # is left out (the game won't give it one)
    cfg = {"champ": "Ahri", "level": 2, "items": ["NoItem"] * 3, "buffs": [["Pentakill", 5, 0]],
           "enemy": {"hp": 1800, "armor": 100, "mr": 100}, "slice": "Emblem", "rowInputs": {"BeachPopEmblem": 7}}
    rows = {r["extraCls"]: r for r in sim_entry.run_slice(cfg)["rows"]}
    assert "Spatula" not in rows and "FryingPan" not in rows
    assert "KDAEmblem" not in rows  # Ahri is K/DA
    assert rows["BeachPopEmblem"]["extra"] == "Beach Pop Emblem (7)"
    assert rows["BeachPopEmblem"]["input"]["options"] == [3, 5, 7]
    assert rows["PentakillEmblem"]["extra"] == "Pentakill Emblem (5)"  # the bar's level
    assert rows["JazzEmblem"]["extra"] == "Jazz Emblem (2, 5 active traits)"  # its parameter in the name (owner, 2026-11-20)
    assert rows["IllbeatsEmblem"]["extra"] == "IllBeats Emblem (2, Mix: All AP)"  # Ahri is a Magic champion: all AP
    assert rows["IllbeatsEmblem"]["input"]["param"]["options"][0] == "All AD"
    assert rows["RockEmblem"]["input"] is None  # no simulated trait
    assert "TacticiansCrown" not in rows  # only with an augment that reads them (owner): U.R.F.
    cfg["buffs"].append(["URF", 1, 0])
    rows = {r["extraCls"] for r in sim_entry.run_slice(cfg)["rows"]}
    assert {"TacticiansCrown", "TacticiansCape", "TacticiansShield"} <= rows


def test_an_emblem_makes_its_holder_a_member():
    # owner, 2026-11-20: Ahri (not Beach Pop) holding a Beach Pop Emblem gets the members' attack speed
    def member(items):
        c = sim_entry._build_champion({"champ": "Ahri", "level": 2, "items": items, "buffs": [["BeachPop", 3, 0]]})
        Simulator().itemStats(c.items, c)
        return c.has_trait("DA_OceanSong19"), c.aspd.total("MultiplyAdditive")
    assert member(["NoItem"] * 3)[0] is False
    held, with_emblem = member(["BeachPopEmblem", "NoItem", "NoItem"])
    assert held and with_emblem > member(["NoItem"] * 3)[1]
