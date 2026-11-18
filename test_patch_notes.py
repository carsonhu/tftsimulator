"""Builds made from patch notes (ledger B33, tools/patch_notes_build.py): the 2026-11-18 Day 1 PBE notes on top of
rls-19.1.0.5973071, standing in for rls-19.1.0.5983251 (its archives are encrypted)."""
import json
import os
import subprocess
import sys

import set19champs
from buildstore import load_build
from set19champs import RenataGlasc
from test_timing import dummy

BASE = 'rls-19.1.0.5973071.Set19.Shipping.pbe'
NOTES = 'rls-19.1.0.5983251.Set19.Shipping.pbe.notes'
HERE = os.path.dirname(os.path.abspath(__file__))
PATCH = os.path.join(HERE, 'builds', 'patch_notes', 'rls-19.1.0.5983251.json')


def test_only_the_noted_rows_change():
    base, notes = load_build(BASE), load_build(NOTES)
    patch = json.load(open(PATCH, encoding='utf-8'))
    noted = {(r['champion'], r['row']): r for r in patch['rows']}
    for key, c in base.data['champions'].items():
        after = notes.data['champions'][key]
        for row, vals in c['ability']['rows'].items():
            if (key, row) in noted:
                assert list(vals) == noted[(key, row)]['old'] and after['ability']['rows'][row] == noted[(key, row)]['new']
            else:
                assert after['ability']['rows'][row] == vals, (key, row)
    assert notes.champion('DA_Ziggs19').row('InitialDamage') == (155, 235, 355)
    assert notes.data['meta']['patch_notes']['base'] == BASE


def test_renata_long_captivate_needs_a_lower_star_target():
    # the notes: the long Captivate needs a target below her star level (was: at or below), and lasts 9 s (was 6)
    for version, level, expected in ((BASE, 1, 6), (NOTES, 1, 3), (NOTES, 2, 9)):
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


def test_a_wrong_old_value_writes_nothing(tmp_path):
    patch = json.load(open(PATCH, encoding='utf-8'))
    patch['version'] = 'test-wrong-old'
    patch['rows'][0]['old'] = [1, 2, 3]
    bad = tmp_path / 'bad.json'
    bad.write_text(json.dumps(patch), encoding='utf-8')
    run = subprocess.run([sys.executable, os.path.join(HERE, 'tools', 'patch_notes_build.py'), str(bad)],
                         capture_output=True, text=True)
    assert run.returncode != 0 and 'not written' in run.stderr
    assert not os.path.exists(os.path.join(HERE, 'builds', 'test-wrong-old.json'))
