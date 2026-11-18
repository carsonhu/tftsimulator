"""The site's JSON entry point on the Set 19 registries (E16): catalog, champion info and a run, with a temporary
build-driven champion registered for the test."""
import json

import pytest

import set19champs
import sim_entry
from build_champion import BuildChampion


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
    assert info['stats']['role'] == 'MagicCaster' and info['stats']['castTime'] == 1
    assert info['stats']['build'].startswith('rls-19.1.0')
    out = json.loads(sim_entry.run_json(json.dumps(cfg())))
    import set19items
    listed = {getattr(set19items, c).display_name for c in set19items.offensive_craftables}
    assert {r['extra'] for r in out['rows']} == listed | {'NoItem'}
    assert out['rows'][0]['dps']['5'] > 0


def test_unknown_champion_is_refused():
    with pytest.raises(KeyError, match='not a Set 19 champion'):
        sim_entry.run_slice(cfg(champ='Ahri'))


def test_catalog_lists_the_builds_for_the_picker():
    # B9: the page offers every imported build, newest first; the value is the version cfg["build"] names
    cat = json.loads(sim_entry.catalog_json())
    assert cat['builds'][0] == {'version': 'rls-19.1.0.5973071.Set19.Shipping.pbe',
                                'label': 'PBE 19.1 #5973071 (Nov 17 13:28)'}


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
    assert cat['defaults']['layout'] == {'targets': 3, 'max': 7}
    area = {c['name'] for c in cat['champions'] if c['area']}
    assert area == {'Varus', 'Ziggs', 'Ezreal', 'Malzahar', 'Kayle', 'Bard', 'RenataGlasc'}

    def dps(champ, slice_, extra, layout):
        out = json.loads(sim_entry.run_json(json.dumps(cfg(champ=champ, level=1, slice=slice_, layout=layout))))
        return next(r['dps']['25'] for r in out['rows'] if r['extra'] == extra)

    assert dps('Varus', 'Craftable', 'NoItem', {'targets': 5}) > dps('Varus', 'Craftable', 'NoItem', None) \
        == dps('Varus', 'Craftable', 'NoItem', {'targets': 3}) > dps('Varus', 'Craftable', 'NoItem', {'targets': 1})
    assert dps('Draven', 'Artifact', 'Titanic Hydra', {'targets': 7}) == dps('Draven', 'Artifact', 'Titanic Hydra', None)


def test_trait_rows_name_their_level_and_use_their_own_numbers():
    # owner, 2026-11-18: "Trickshot 2", "Trickshot 3", ...; each row's ratio is its own DPS over NoItem's (rows used to
    # share one by name, so every level of a trait showed the last one's)
    out = json.loads(sim_entry.run_json(json.dumps(cfg(champ='Gnar', level=1, slice='Trait', t=30,
                                                       buffs=[['Pentakill', 0, 0], ['Trickshot', 0, 0]]))))
    rows = {r['extra']: r for r in out['rows']}
    assert {'Pentakill 3', 'Pentakill 5', 'Pentakill 7', 'Trickshot 2', 'Trickshot 3', 'Trickshot 4', 'NoItem'} == set(rows)
    base = rows['NoItem']['dps']['25']
    for r in rows.values():
        assert r['ratio']['25'] == round(r['dps']['25'] / base, 2)
    assert len({rows[f'Pentakill {n}']['ratio']['25'] for n in (3, 5, 7)}) == 3
