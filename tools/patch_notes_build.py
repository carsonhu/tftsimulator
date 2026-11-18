"""A build made from patch notes, for a client build that can't be read (ledger B33).

    python tools/patch_notes_build.py builds/patch_notes/<file>.json

The patch file names a base build (an imported snapshot), the curve rows the notes change, each with its old value as
the notes state it, and any script rule the notes change. Every old value must equal the base build's, or nothing is
written: a mismatch means the notes were mapped to the wrong row. The result is builds/<version>.json, the base with
those rows replaced and `patch_notes` recorded in its meta and on each changed champion, listed in builds/index.json
above its base (newest first). Rerunning rewrites it from the base, so the patch file is the only thing to edit.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ROOT, 'builds')


def main(path):
    notes = json.load(open(path, encoding='utf-8'))
    index_path = os.path.join(OUT, 'index.json')
    index = json.load(open(index_path, encoding='utf-8'))
    base_entry = next((b for b in index['builds'] if b['version'] == notes['base']), None)
    if base_entry is None:
        sys.exit(f'base build {notes["base"]} is not imported')
    base = json.load(open(os.path.join(OUT, base_entry['file']), encoding='utf-8'))
    build = copy.deepcopy(base)
    problems = []
    for ch in notes['rows']:
        c = build['champions'].get(ch['champion'])
        rows = (c or {}).get('ability', {}).get('rows')
        if rows is None or ch['row'] not in rows:
            problems.append(f'{ch["champion"]}: no row {ch["row"]} in {notes["base"]}')
            continue
        if [float(x) for x in rows[ch['row']]] != [float(x) for x in ch['old']]:
            problems.append(f'{ch["champion"]} {ch["row"]}: the notes say {ch["old"]}, {notes["base"]} has '
                            f'{rows[ch["row"]]}')
            continue
        rows[ch['row']] = list(ch['new'])
        c.setdefault('patch_notes', []).append({'row': ch['row'], 'old': ch['old'], 'new': ch['new'],
                                                'note': ch.get('note')})
    for r in notes.get('rules', []):
        c = build['champions'].get(r['champion'])
        if c is None:
            problems.append(f'{r["champion"]}: not in {notes["base"]}')
            continue
        c.setdefault('patch_rules', []).append(r['rule'])
        c.setdefault('patch_notes', []).append({'rule': r['rule'], 'note': r.get('note')})
    if problems:
        sys.exit('not written:\n  ' + '\n  '.join(problems))

    meta = build['meta']
    # not a snapshot: no archives of its own (import_build.py sorts it by the notes' date)
    meta.update(version=notes['version'], install=notes.get('install', meta.get('install')), pak_mtime=None,
                snapshot_at=None)
    meta['patch_notes'] = {'base': notes['base'], 'client_build': notes.get('client_build'), 'date': notes.get('date'),
                           'source': notes['source'], 'file': os.path.relpath(path, ROOT).replace(os.sep, '/'),
                           'rows': len(notes['rows']), 'rules': len(notes.get('rules', []))}
    file = notes['version'] + '.json'
    with open(os.path.join(OUT, file), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(build, f, ensure_ascii=False, separators=(',', ':'))

    entry = {'version': notes['version'], 'install': notes.get('install', 'PBE'), 'pak_mtime': None, 'file': file,
             'label': notes.get('label'), 'date': notes.get('date'), 'base': notes['base']}
    builds = [b for b in index['builds'] if b['version'] != notes['version']]
    builds.insert(builds.index(base_entry), entry)  # above its base: the newer client build
    index['builds'] = builds
    with open(index_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(index, f, indent=1)
        f.write('\n')
    print(f'{file}: {len(notes["rows"])} rows, {len(notes.get("rules", []))} rules from the notes; '
          f'index: {[b["version"] for b in builds]}')


if __name__ == '__main__':
    main(sys.argv[1])
