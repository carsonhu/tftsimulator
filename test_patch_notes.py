"""Builds made from patch notes (ledger B33, tools/patch_notes_build.py). The 2026-11-18 Day 1 PBE notes stood in for
the encrypted client until it was read (FModel raw export): rls-19.1.0.5986094 carries them. The notes file stays as
the record and as the tool's test data."""
import json
import os
import subprocess
import sys

import set19champs
from buildstore import Build, load_build
from set19champs import RenataGlasc
from test_timing import dummy

BASE = 'rls-19.1.0.5973071.Set19.Shipping.pbe'
REAL = 'rls-19.1.0.5986094.Set19.Shipping.pbe'
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, 'tools', 'patch_notes_build.py')
PATCH = os.path.join(HERE, 'builds', 'patch_notes', 'rls-19.1.0.5983251.json')


def patch():
    return json.load(open(PATCH, encoding='utf-8'))


def test_the_notes_match_the_client_build():
    # every row the notes changed: the old value is the base snapshot's, the new one the client build's
    base, real = load_build(BASE), load_build(REAL)
    for r in patch()['rows']:
        assert list(base.champion(r['champion']).row(r['row'])) == r['old']
        assert list(real.champion(r['champion']).row(r['row'])) == r['new'], r['note']


def test_the_tool_changes_only_the_noted_rows(tmp_path):
    p = patch()
    p.pop('superseded_by', None)
    src = tmp_path / 'notes.json'
    src.write_text(json.dumps(p), encoding='utf-8')
    subprocess.run([sys.executable, TOOL, str(src), str(tmp_path / 'out')], check=True, capture_output=True)
    notes = Build(json.load(open(tmp_path / 'out' / (p['version'] + '.json'), encoding='utf-8')))
    base = load_build(BASE)
    noted = {(r['champion'], r['row']): r for r in p['rows']}
    for key, c in base.data['champions'].items():
        after = notes.data['champions'][key]
        for row, vals in c['ability']['rows'].items():
            expect = noted[(key, row)]['new'] if (key, row) in noted else vals
            assert after['ability']['rows'][row] == expect, (key, row)
    assert notes.data['champions']['DA_RenataGlasc19']['patch_rules'] == ['CaptivateLongIfStarBelow']
    assert json.load(open(tmp_path / 'out' / 'index.json'))['builds'][0]['label'] == 'patch notes'


def test_a_wrong_old_value_or_a_superseded_file_writes_nothing(tmp_path):
    p = patch()
    p.pop('superseded_by', None)
    p['rows'][0]['old'] = [1, 2, 3]
    bad = tmp_path / 'bad.json'
    bad.write_text(json.dumps(p), encoding='utf-8')
    run = subprocess.run([sys.executable, TOOL, str(bad), str(tmp_path / 'out')], capture_output=True, text=True)
    assert run.returncode != 0 and 'not written' in run.stderr and not (tmp_path / 'out').exists()
    run = subprocess.run([sys.executable, TOOL, PATCH], capture_output=True, text=True)  # into builds/: refused
    assert run.returncode != 0 and 'superseded' in run.stderr


def test_renata_long_captivate_needs_a_lower_star_target_from_5986094():
    # GA_RenataGlasc19_Spell: LessEqual_IntInt to 5973071, Less_IntInt from 5986094; CaptivateDurationLong 6 -> 9
    for version, level, expected in ((BASE, 1, 6), (REAL, 1, 3), (REAL, 2, 9)):
        r = RenataGlasc(level, build=load_build(version))
        got = []
        r.tick = 0
        r.items = []
        orig = set19champs.captivate
        set19champs.captivate = lambda unit, target, seconds: got.append(seconds)
        try:
            r._toxin(dummy(), 1)
        finally:
            set19champs.captivate = orig
        assert got == [expected], (version, level, got)
