"""Copy client builds from the datamining snapshots into set19/builds/ in the form the simulator reads.

    python tools/import_build.py            # import every snapshotted Set 19 build not already here
    python tools/import_build.py --force    # re-import all (after a change to this script)

Source: F:/tft_projects/tftDatamine/builds/<version>/ (written by tftDatamine/tools/snapshot_build.py, one folder
per client build, never overwritten). Each build becomes builds/<version>.json; builds/index.json lists them,
newest first. The numbers are copied, not edited: if the simulator needs a value the build doesn't have, that is a
question for docs/ASSUMPTIONS.md, not something to patch in here.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
SRC = os.environ.get('TFT_SNAPSHOTS', r'F:\tft_projects\tftDatamine\builds')
OUT = os.path.join(ROOT, 'builds')
SCHEMA = 1


def plain(html):
    s = re.sub(r'<br\s*/?>', '\n', html or '')
    s = re.sub(r'<[^>]+>', '', s)
    return (s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
            .replace('&#x27;', "'").strip())


def champion(c):
    t = c.get('timing') or {}
    return {
        'key': c['key'], 'name': c['name'], 'cost': c['cost'], 'role': c['role'], 'in_shop': c['in_shop'],
        'pool': c.get('pool'), 'traits': [x['name'] for x in c['traits']], 'trait_keys': [x['key'] for x in c['traits']],
        'stats': c['stats'], 'hp': c['hp'], 'ad': c['ad'],
        'ability': {'name': c['ability']['name'], 'text': plain(c['ability']['html']), 'html': c['ability']['html'],
                    'curve_table': c['ability']['curve_table'], 'rows': c['ability']['rows'],
                    'calcs': c['ability']['calcs']},
        'timing': {k: t.get(k) for k in ('attack_chrono', 'attack_launch', 'attack_launch_variants', 'attack_len',
                                         'attack_release_base_as', 'projectile', 'proj_speed', 'proj_movement')}
        | {'spells': [{k: s.get(k) for k in ('ga', 'cast_chrono', 'cast_end', 'lockout', 'manalock_removed',
                                             'finish_cause', 'reads_attack_speed', 'cancels_attack', 'notes',
                                             'log')}
                      for s in t.get('spells') or []]},
        'abilities': [a['ga'] for a in c['abilities']],
        'effects': c.get('effects') or [],
        'unlock': c.get('unlock'),
        'chronos': c.get('chronos') or {},
        'package': c['package'],
    }


def simple(x, keep):
    return {k: x.get(k) for k in keep} | {'text': plain(x.get('html'))}


def convert(src_dir):
    d = json.load(open(os.path.join(src_dir, 'data.json'), encoding='utf-8'))
    m = json.load(open(os.path.join(src_dir, 'manifest.json'), encoding='utf-8'))
    return {
        'schema': SCHEMA,
        'meta': {k: m.get(k) for k in ('version', 'install', 'set', 'snapshot_at', 'pak_mtime', 'usmap',
                                       'usmap_is_this_build', 'tools', 'counts', 'read_problems',
                                       'cosmetic_read_problems')},
        'champions': {c['key']: champion(c) for c in d['champions']},
        'roles': {r['key'].removeprefix('DA_Role_'): r for r in d.get('roles', [])},
        'traits': {t['key']: simple(t, ('key', 'name', 'kind', 'rows', 'calcs', 'curve_table'))
                   | {'tiers': [{'threshold': x['threshold'], 'text': plain(x['html']), 'unlock': x.get('unlock')}
                                for x in t['tiers']]} for t in d['traits']},
        'items': {i['key']: simple(i, ('key', 'name', 'kind', 'tags', 'rows', 'calcs', 'recipes'))
                  | {'stat_text': plain(i.get('stat_html'))} for i in d['items']},
        'augments': {a['key']: simple(a, ('key', 'name', 'tier', 'round_variant', 'rows', 'calcs', 'never_select'))
                     for a in d['augments']},
        'globals': d.get('globals') or {},
        'read_problems': d.get('problems', []),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    done = 0
    for v in sorted(os.listdir(SRC)):
        src = os.path.join(SRC, v)
        if v.endswith('.partial') or not os.path.exists(os.path.join(src, 'manifest.json')):
            continue
        m = json.load(open(os.path.join(src, 'manifest.json'), encoding='utf-8'))
        if str(m.get('set')) != '19':
            continue
        dst = os.path.join(OUT, f'{v}.json')
        if os.path.exists(dst) and not a.force:
            continue
        json.dump(convert(src), open(dst, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False,
                  separators=(',', ':'))
        done += 1
        print('imported', v, f'{os.path.getsize(dst) / 1e6:.2f} MB')
    index = []
    for f in os.listdir(OUT):
        if f.endswith('.json') and f != 'index.json':
            meta = json.load(open(os.path.join(OUT, f), encoding='utf-8'))['meta']
            index.append({'version': meta['version'], 'install': meta['install'], 'pak_mtime': meta['pak_mtime'],
                          'file': f})
    index.sort(key=lambda x: x['pak_mtime'], reverse=True)
    json.dump({'builds': index}, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8', newline='\n'), indent=1)
    print(f'{done} imported, {len(index)} builds in builds/index.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
