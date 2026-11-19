"""Report on client builds that are snapshotted but not yet in the simulator (ledger B34).

    python tools/new_build_report.py              # every Set 19 snapshot not imported here and without a report
    python tools/new_build_report.py <version>    # that snapshot, rewriting its report
    python tools/new_build_report.py <version> --against <version>   # compared with another build (a test run)

For each, writes <snapshot folder>/sim_report.md (F:/tft_projects/tftDatamine/builds/<version>/): what changed against
the simulator's current build in the data the simulator reads (its champions, items, traits and augments), every
results table run on both builds (DPS and Extra DPS moves, and any table that fails on the new build), and new read
problems. Nothing in set19 changes: adopting the build is the commands at the end of the report. The scheduled task
"TFT build snapshot" runs this after each snapshot (tftDatamine/tools/snapshot_task.bat).
"""
import datetime
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import buildstore  # noqa: E402
import import_build  # noqa: E402
import set19buffs  # noqa: E402
import set19champs  # noqa: E402
import set19items  # noqa: E402
import sim_entry  # noqa: E402
import table_dump  # noqa: E402

SRC = import_build.SRC
TEXT_FIELDS = {'text', 'html', 'calcs', 'stat_text'}  # tooltip text: follows the numbers; reported as a count only


# ------------------------------------------------------------------------------------------------ what to report
def pending():
    """Set 19 snapshots that are complete, not imported into set19 and have no report yet."""
    have = {b['version'] for b in buildstore.list_builds()}
    out = []
    for v in sorted(os.listdir(SRC)):
        d = os.path.join(SRC, v)
        if v.endswith('.partial') or not os.path.exists(os.path.join(d, 'manifest.json')):
            continue
        m = json.load(open(os.path.join(d, 'manifest.json'), encoding='utf-8'))
        if str(m.get('set')) == '19' and v not in have and not os.path.exists(os.path.join(d, 'sim_report.md')):
            out.append(v)
    return out


def diff(a, b, path=''):
    """[(path, old, new)] between two JSON values; tooltip text fields only as one line each."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            if k in TEXT_FIELDS:
                if a.get(k) != b.get(k):
                    out.append((f'{path}/{k}', '(text)', '(changed)'))
                continue
            out += diff(a.get(k), b.get(k), f'{path}/{k}')
        return out
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f'{path}[{i}]')
        return out
    return [] if a == b else [(path, a, b)]


def short(v, n=70):
    s = json.dumps(v, ensure_ascii=False, default=str) if not isinstance(v, str) else v
    return s if len(s) <= n else s[:n - 1] + '…'


def simulated_keys():
    champs = set()
    for n in set19champs.champ_list:
        cls = getattr(set19champs, n)
        champs |= {k for k in (cls.KEY, getattr(cls, 'BASE_KEY', None)) if k}
    def keys(mod, names):
        return {getattr(getattr(mod, n), 'KEY', None) for n in names} - {None}
    items = keys(set19items, set19items.offensive_craftables + set19items.artifacts + set19items.radiants
                 + set19items.emblems)
    return {'champions': champs, 'items': items, 'traits': keys(set19buffs, set19buffs.class_buffs),
            'augments': keys(set19buffs, set19buffs.augments)}


# ------------------------------------------------------------------------------------------------ tables
def tables(build):
    """Every table table_dump runs, on `build`: {key: rows or 'ERROR: ...'} (one failure doesn't stop the rest)."""
    catalog = sim_entry.get_catalog()
    out = {}
    for champ in sorted(set19champs.champ_list):
        for level in table_dump.LEVELS:
            for slice_name in catalog['slices']:
                key = f'{champ}/{level}/{slice_name}'
                try:
                    res = sim_entry.run_slice(table_dump.config(champ, level, build, slice_name))
                    out[key] = {r['extra']: {'dps': r['dps'], 'ratio': r['ratio']} for r in res['rows']}
                except Exception as ex:
                    out[key] = f'ERROR: {type(ex).__name__}: {ex}'
    return out


# ------------------------------------------------------------------------------------------------ the report
def report(version, against=None, out_name='sim_report.md'):
    src = os.path.join(SRC, version)
    data = import_build.convert(src)
    new = buildstore.Build(data)
    buildstore._cache[version] = new  # load_build(version) finds it without an index entry: set19 is not touched
    base = buildstore.load_build(against)
    keys = simulated_keys()
    man = json.load(open(os.path.join(src, 'manifest.json'), encoding='utf-8'))
    L = [f'# {version}: simulator report', '',
         f'Written {datetime.datetime.now():%Y-%m-%d %H:%M} by set19/tools/new_build_report.py. Compared with the '
         f'simulator\'s current build `{base.version}`. Nothing in set19 has changed yet (see "Adopt" at the end).', '',
         f'- Client installed: {man.get("pak_mtime")}; snapshot: {man.get("snapshot_at")}',
         f'- Read from: {"an FModel raw export, " + str((man.get("loose_export") or {}).get("path")) if man.get("loose_export") else "the client archives"}',
         f'- Usmap: {man.get("usmap")} ({"this build" if man.get("usmap_is_this_build") else "an older build"})',
         f'- Read problems: {man.get("read_problems")} (current build: {base.meta.get("read_problems")})', '']

    # data the simulator reads
    L += ['## What changed in the data the simulator reads', '']
    any_change = False
    for kind, label in (('champions', 'Champions'), ('items', 'Items'), ('traits', 'Traits'), ('augments', 'Augments')):
        rows = []
        for k in sorted(keys[kind]):
            a, b = base.data[kind].get(k), new.data[kind].get(k)
            if a is None or b is None:
                rows.append(f'- `{k}`: {"missing from the new build" if b is None else "new"}')
                continue
            d = diff(a, b)
            if d:
                rows.append(f'- `{k}`:')
                rows += [f'  - `{p}`: {short(x)} -> {short(y)}' for p, x, y in d[:12]]
                if len(d) > 12:
                    rows.append(f'  - ... {len(d) - 12} more')
        if rows:
            any_change = True
            L += [f'### {label}', ''] + rows + ['']
    for kind in ('roles', 'globals'):
        d = diff(base.data.get(kind), new.data.get(kind))
        if d:
            any_change = True
            L += [f'### {kind.title()}', ''] + [f'- `{p}`: {short(x)} -> {short(y)}' for p, x, y in d[:20]] + ['']
    if not any_change:
        L += ['Nothing: every champion, item, trait and augment the simulator uses is unchanged.', '']

    # tables
    print(f'{version}: tables on {base.version} ...', flush=True)
    t_old = tables(base.version)
    print(f'{version}: tables on {version} ...', flush=True)
    t_new = tables(version)
    errors = sorted(k for k, v in t_new.items() if isinstance(v, str))
    changed = sorted(k for k in t_new if not isinstance(t_new[k], str) and t_new[k] != t_old.get(k))
    L += ['## Results tables', '', f'{len(t_new)} tables run on both builds: {len(changed)} changed, {len(errors)} '
          f'fail on the new build.', '']
    if errors:
        L += ['### Failing on the new build (fix before adopting)', '']
        L += [f'- `{k}`: {t_new[k]}' + (' (also fails on the current build)' if isinstance(t_old.get(k), str) else '')
              for k in errors] + ['']
    if changed:
        L += ['### NoItem DPS (20-30 s), 1 star, and the biggest Extra DPS moves', '',
              '| Champion | NoItem DPS | Biggest Extra DPS moves |', '|---|---|---|']
        champs = sorted({k.split('/')[0] for k in changed})
        for c in champs:
            k = f'{c}/1/Craftable'
            a, b = t_old.get(k), t_new.get(k)
            dps = (f'{a["NoItem"]["dps"]["20-30"]} -> {b["NoItem"]["dps"]["20-30"]}'
                   if isinstance(a, dict) and isinstance(b, dict) and 'NoItem' in a and 'NoItem' in b else '–')
            moves = []
            for kk in [x for x in changed if x.startswith(c + '/')]:
                for row, v in t_new[kk].items():
                    o = (t_old.get(kk) or {}).get(row) if isinstance(t_old.get(kk), dict) else None
                    if o and o['ratio'].get('20-30') != v['ratio'].get('20-30'):
                        moves.append((abs(v['ratio']['20-30'] - o['ratio']['20-30']), f'{row} ({kk.split("/", 1)[1]}) '
                                      f'{o["ratio"]["20-30"]} -> {v["ratio"]["20-30"]}'))
            moves.sort(reverse=True)
            L.append(f'| {c} | {dps} | {"; ".join(m for _, m in moves[:3]) or "ratios unchanged"} |')
        L.append('')

    # read problems
    base_src = os.path.join(SRC, base.version, 'data.json')
    if os.path.exists(base_src):
        old_p = {str(p)[:120] for p in json.load(open(base_src, encoding='utf-8')).get('problems', [])}
        new_p = [str(p) for p in json.load(open(os.path.join(src, 'data.json'), encoding='utf-8')).get('problems', [])]
        fresh = [p for p in new_p if p[:120] not in old_p]
        L += ['## New read problems', '', f'{len(fresh)} not in the current build\'s snapshot'
              + (' (a newer usmap may fix them: tftDatamine/tools/usmap_no_replay.ps1 -Install PBE).' if fresh else '.'),
              ''] + [f'- {short(p, 160)}' for p in fresh[:25]] + (['- ...'] if len(fresh) > 25 else []) + ['']

    L += ['## Adopt', '', 'In set19 (`F:/tft_projects/tftSim/tft_calculator/set19`):', '', '```',
          'python tools/import_build.py      # the build becomes the page\'s default',
          'python tools/worksheets.py        # refresh the generated blocks',
          'python -m pytest -q               # tests that cite build numbers may need the new values',
          'python tools/table_dump.py <out.json>   # the tables, for the record',
          '```', '']
    out = os.path.join(src, out_name)
    open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
    print(f'{version}: wrote {out} ({len(changed)} tables changed, {len(errors)} failing)')
    return out


def main():
    args = sys.argv[1:]
    against = None
    if '--against' in args:
        i = args.index('--against')
        against = args[i + 1]
        del args[i:i + 2]
    versions = args or pending()
    if not versions:
        print('no new builds to report on')
    for v in versions:
        try:
            # a test run against another build writes its own file: the snapshot's real report stays as it is
            report(v, against, f'sim_report_vs_{against}.md' if against else 'sim_report.md')
        except Exception:
            traceback.print_exc()
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
