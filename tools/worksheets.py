"""Per-champion worksheets (champions/<Name>.md) and the roster check, from a client build.

    python tools/worksheets.py                # newest build; refresh the AUTO block of every in-scope worksheet
    python tools/worksheets.py --build <version>
    python tools/worksheets.py --init-roster  # write roster.json from the build (only if it doesn't exist)

A worksheet has one machine-written block, between the AUTO BEGIN / AUTO END markers: the build's data for that
champion and the client-side timing prediction. It is rewritten on every run. Everything else in the file (questions,
evidence, decisions) is written by people and is never touched after the file is first created.

The roster (roster.json) is edited by hand. This script only reports when a build disagrees with it (a unit's role
changed, a unit appeared or disappeared).
"""
import argparse
import datetime
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, ROOT)
from buildstore import load_build, list_builds  # noqa: E402

SNAPSHOTS = os.environ.get('TFT_SNAPSHOTS', r'F:\tft_projects\tftDatamine\builds')
ROSTER = os.path.join(ROOT, 'roster.json')
SHEETS = os.path.join(ROOT, 'champions')
BEGIN, END = '<!-- AUTO BEGIN', '<!-- AUTO END -->'
# identifiers in a champion's decoded scripts that bear on how a cast interacts with attacks and mana
HINTS = {
    'GE_SimulateLaunchAttack': 'applies the "simulate a launched attack" effect (may count as an attack for on-attack effects)',
    'AppliesOnHit': 'something in the script is flagged as applying on-hit effects',
    'OnHitEffectivenessMultiplier': 'scales on-hit effects',
    'IsAttack': 'damage flagged as an attack (or checked for it)',
    'LaunchAttack': 'launches or listens for attacks',
    'AttackSpeed': 'reads or changes attack speed',
    'GE_ManaLock': 'applies mana lock',
    'ManaPerAttack': 'reads or changes mana per attack',
    'GE_UnitStopAttackingMovingCasting': 'stops the unit attacking/moving/casting',
}


def is_tank(role):
    return 'Tank' in (role or '')


def sheet_name(key):
    """DA_Ahri19 -> Ahri, DA_Akali_TrueDamage19 -> Akali_TrueDamage, DA_19_Foo -> Foo."""
    n = key.removeprefix('DA_')
    n = re.sub(r'^19_', '', n)
    return re.sub(r'19$', '', n)


def n(v):
    if v is None:
        return '–'
    if isinstance(v, float):
        v = round(v, 4)
        if v == int(v):
            v = int(v)
    return str(v)


def slash(vals):
    vals = list(vals or [])
    if not vals:
        return '–'
    return n(vals[0]) if all(x == vals[0] for x in vals) else ' / '.join(n(x) for x in vals)


def tick(t):
    return '–' if t is None else f'{n(t)} s ({round(t * 30, 2):g} ticks)'


def script_hints(build, c):
    """{identifier: [script files]} for the champion's own folder in the build's decoded scripts."""
    z = os.path.join(SNAPSHOTS, build.version, 'ga_scripts.zip')
    if not os.path.exists(z):
        return None
    folder = 'Champions/' + c.d['package'].split('/Champions/')[1].split('/')[0] + '/'
    out = {}
    cancels = []
    with zipfile.ZipFile(z) as zf:
        for name in zf.namelist():
            if not (name.startswith(folder) and name.endswith('.txt')):
                continue
            text = zf.read(name).decode('utf-8', 'replace')
            short = name[len(folder):]
            for k in HINTS:
                if k in text:
                    out.setdefault(k, []).append(short)
            m = re.search(r"'CancelAbilitiesWithTag': \[([^\]]*)\]", text)
            if m and 'Combat.Attacking' in m.group(1) and re.search(r"'TriggerTag': \{'TagName': 'Combat.Event.CastSpell'", text):
                cancels.append(short)
    return out, cancels


def auto_block(build, c, prev):
    d = c.d
    s = d['stats']
    role = build.role(d['role']) if d['role'] in build.data['roles'] else None
    L = [f'{BEGIN}: written by tools/worksheets.py from build {build.version}; edits here are overwritten -->',
         f'## Client data: build `{build.version}`', '']
    if role:
        L.append(f'- **Role** {d["role"]}: "{" ".join((role.d.get("description") or "").split())}" '
                 + '(' + '; '.join(f'{m["attribute"]} {m["op"]} {m["text"]}' for e in role.d.get('effects') or [] if e
                                   for m in e.get('modifiers') or []) + ')')
    L.append(f'- **Cost** {d["cost"]}, pool {n(d.get("pool"))}; traits: {", ".join(d["traits"]) or "–"}')
    L.append(f'- **HP** {slash(d["hp"])} · **AD** {slash(d["ad"])} · **AS** {n(s.get("AttackSpeed"))} · '
             f'**Range** {n(s.get("AttackRange", 1))} · **Armor** {n(s.get("Armor"))} · **MR** {n(s.get("MagicResist"))} · '
             f'**Mana** {n(s.get("ManaStarting", s.get("Mana", 0)))} / {n(s.get("ManaMax"))}')
    other = {k: v for k, v in s.items() if k not in ('HealthMax', 'AttackSpeed', 'AttackRange', 'Armor', 'MagicResist',
                                                     'ManaMax', 'ManaStarting', 'Mana', 'AttackDamage')}
    if other:
        L.append('- Other stats: ' + ', '.join(f'{k} {n(v)}' for k, v in other.items()))
    if d.get('unlock'):
        L.append('- **Unlock**: ' + ' / '.join(re.sub(r'<[^>]+>', '', q.get('html') or '') for q in d['unlock']['conditions']))
    ab = d['ability']
    L += ['', f'### Ability: {ab["name"] or "–"}', '', '> ' + (ab['text'] or '–').replace('\n', '\n> '), '']
    if ab['rows']:
        L += ['| variable | 1★ | 2★ | 3★ |', '|---|---|---|---|']
        L += [f'| {k} | ' + ' | '.join(n(x) for x in v) + ' |' for k, v in ab['rows'].items()]
        L.append('')
    if ab['calcs']:
        L += ['Formulas (as stored; AD and AP are multipliers):', '']
        L += [f'- `{k}` = {v}' for k, v in ab['calcs'].items()]
        L.append('')
    t = d['timing']
    L += ['### Timing the client predicts (unverified for Set 19)', '',
          f'- Attack chrono `{t.get("attack_chrono") or "–"}`: launch {tick(t.get("attack_launch"))}'
          + (f', variants {", ".join(n(x) for x in t.get("attack_launch_variants") or [])}' if len(t.get('attack_launch_variants') or []) > 1 else '')
          + f'; animation length {tick(t.get("attack_len"))}; release at base AS {tick(t.get("attack_release_base_as"))}',
          f'- Attack projectile: {t.get("projectile") or "none (melee or not a fixed projectile)"}'
          + (f', speed {n(t.get("proj_speed"))} units/s' if t.get('proj_speed') else (f' ({t.get("proj_movement")})' if t.get('proj_movement') else ''))]
    for sp in t.get('spells') or []:
        L += [f'- Spell `{sp["ga"]}` (chrono `{sp.get("cast_chrono") or "–"}`): cast ends {tick(sp.get("cast_end"))}, '
              f'next attack can start {tick(sp.get("lockout"))}, mana lock removed {tick(sp.get("manalock_removed"))}'
              + ('; **script reads attack speed**' if sp.get('reads_attack_speed') else '')
              + (f'; ended by `{sp["finish_cause"]}`' if sp.get('finish_cause') else '; **no cast end found**')]
        if sp.get('notes'):
            L.append('  - notes: ' + '; '.join(f'{k} ×{v}' for k, v in sp['notes'].items()))
    if not t.get('spells'):
        L.append('- No spell timeline decoded (no spell ability, or the script never reaches a cast end).')
    casts = {k: v for k, v in (d.get('chronos') or {}).items() if v.get('events')}
    if casts:
        L += ['', 'Every timeline in the champion folder that has events (the spell prediction above follows one path '
              'through the script; a unit with several cast versions has a timeline for each):', '',
              '| chrono | folder | length | events (s) |', '|---|---|---|---|']
        for k, v in casts.items():
            ev = ', '.join(f'{e} {n(x)}' for e, x in v['events'])
            L.append(f'| `{k}` | {v["path"].rsplit("/", 1)[0]} | {n(v["length"])} | {ev} |')
    L += ['', '### Scripts on the unit', '', ', '.join(f'`{a}`' for a in d['abilities']) or '–', '']
    hints = script_hints(build, c)
    if hints is not None:
        found, cancels = hints
        L.append('Script hints (identifiers present in this champion\'s decoded scripts; leads, not evidence):')
        L.append('')
        if cancels:
            L.append(f'- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): {", ".join(cancels)}')
        for k, files in found.items():
            L.append(f'- `{k}`: {HINTS[k]}: {", ".join(sorted(set(files)))}')
        if not found and not cancels:
            L.append('- none')
        L.append('')
    if prev is not None:
        ch = changes(prev, c)
        L += [f'### Changed since `{prev.build.version}`', '']
        L += [f'- {x}' for x in ch] if ch else ['- nothing in this unit\'s data']
        L.append('')
    L.append(END)
    return '\n'.join(L)


def changes(a, b):
    out = []
    for k in sorted(set(a.d['stats']) | set(b.d['stats'])):
        if a.d['stats'].get(k) != b.d['stats'].get(k):
            out.append(f'stat {k}: {n(a.d["stats"].get(k))} -> {n(b.d["stats"].get(k))}')
    ra, rb = a.d['ability']['rows'], b.d['ability']['rows']
    for k in sorted(set(ra) | set(rb)):
        if ra.get(k) != rb.get(k):
            out.append(f'row {k}: {slash(ra.get(k))} -> {slash(rb.get(k))}')
    ta, tb = a.d['timing'], b.d['timing']
    for k in ('attack_launch', 'attack_len', 'proj_speed'):
        if ta.get(k) != tb.get(k):
            out.append(f'timing {k}: {n(ta.get(k))} -> {n(tb.get(k))}')
    sa = {s['ga']: s for s in ta.get('spells') or []}
    sb = {s['ga']: s for s in tb.get('spells') or []}
    for g in sorted(set(sa) | set(sb)):
        for k in ('cast_end', 'lockout', 'manalock_removed', 'reads_attack_speed'):
            if (sa.get(g) or {}).get(k) != (sb.get(g) or {}).get(k):
                out.append(f'spell {g} {k}: {n((sa.get(g) or {}).get(k))} -> {n((sb.get(g) or {}).get(k))}')
    if a.d['ability']['text'] != b.d['ability']['text']:
        out.append('ability text changed')
    return out


HUMAN = """
## Status

- Worksheet status: **not started**
- Keep in the simulator: **undecided** (remove if it can't be simulated realistically; give the reason)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | predicted | |
| Q2 | Mana per attack and per second follow the role | {role_mana} | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | {launch} | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | {proj} | {proj_status} | |
| Q7 | Cast time: cast start to the next attack starting | {lockout} | {cast_status} | |
| Q8 | Does the cast time scale with attack speed? | {reads_as} | {cast_status} | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | {manalock} | {cast_status} | |
| Q10 | Does the mana lock scale with attack speed? | {reads_as} | {cast_status} | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | {cancels} | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted | |
| Q14 | Passives and other mechanics that need modelling | see ability text | open | |
| Q15 | Can this unit be simulated realistically? | | open | |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| Date | Build | Source (VOD URL @ time) | fps | Measured | Frames / values | Result | Question |
|---|---|---|---|---|---|---|---|

## Decisions and notes

"""


def fill_human(c):
    d = c.d
    t = d['timing']
    sp = (t.get('spells') or [{}])[0]
    return HUMAN.format(
        role_mana=d['role'],
        launch=tick(t.get('attack_launch')),
        proj=(f'speed {n(t.get("proj_speed"))}' if t.get('proj_speed') else ('none' if not t.get('projectile') else 'not fixed speed')),
        proj_status='predicted' if t.get('projectile') else 'not applicable?',
        lockout=tick(sp.get('lockout')) if sp else 'no spell timeline',
        manalock=tick(sp.get('manalock_removed')) if sp else 'no spell timeline',
        reads_as=('script reads AS' if sp.get('reads_attack_speed') else 'script does not read AS') if sp else 'no spell timeline',
        cast_status='predicted' if sp and sp.get('lockout') is not None else 'open',
        cancels='see script hints',
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build')
    ap.add_argument('--init-roster', action='store_true')
    a = ap.parse_args()
    b = load_build(a.build)
    builds = [x['version'] for x in list_builds()]
    i = builds.index(b.version)
    prev = load_build(builds[i + 1]) if i + 1 < len(builds) else None
    shop = {k: v for k, v in b.data['champions'].items() if v['in_shop']}

    if a.init_roster:
        if os.path.exists(ROSTER):
            raise SystemExit('roster.json exists; edit it by hand')
        unit = lambda v: {'key': v['key'], 'name': v['name'], 'cost': v['cost'], 'role': v['role']}
        roster = {
            'rule': "In scope: every Set 19 shop unit whose game role is not a Tank role (the role name contains 'Tank'). "
                    'Decided by the owner on 2026-11-17. Units may be removed later if they cannot be simulated '
                    'realistically; each removal goes in "removed" with a date and reason.',
            'decided_on_build': b.version,
            'in_scope': sorted((unit(v) for v in shop.values() if not is_tank(v['role'])), key=lambda u: (u['cost'], u['name'], u['key'])),
            'excluded_tanks': sorted((unit(v) for v in shop.values() if is_tank(v['role'])), key=lambda u: (u['cost'], u['name'], u['key'])),
            'removed': [],
        }
        json.dump(roster, open(ROSTER, 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
        print(f'roster.json: {len(roster["in_scope"])} in scope, {len(roster["excluded_tanks"])} tanks excluded')

    roster = json.load(open(ROSTER, encoding='utf-8'))
    known = {u['key']: u for u in roster['in_scope'] + roster['excluded_tanks'] + roster['removed']}
    warn = []
    for k, v in shop.items():
        if k not in known:
            warn.append(f'new shop unit not in roster.json: {v["name"]} ({k}, {v["role"]})')
        elif is_tank(v['role']) != is_tank(known[k]['role']):
            warn.append(f'{v["name"]}: role {known[k]["role"]} in roster.json, {v["role"]} in this build (tank status changed)')
    for k, u in known.items():
        if k not in shop and u not in roster['removed']:
            warn.append(f'{u["name"]} ({k}) is in roster.json but not in this build\'s shop')

    os.makedirs(SHEETS, exist_ok=True)
    made = updated = 0
    removed = {u['key'] for u in roster['removed']}
    for u in roster['in_scope']:
        if u['key'] in removed or not b.has_champion(u['key']):
            continue
        c = b.champion(u['key'])
        pc = prev.champion(u['key']) if prev and prev.has_champion(u['key']) else None
        block = auto_block(b, c, pc)
        path = os.path.join(SHEETS, sheet_name(u['key']) + '.md')
        if os.path.exists(path):
            text = open(path, encoding='utf-8').read()
            i0, i1 = text.find(BEGIN), text.find(END)
            if i0 < 0 or i1 < 0:
                warn.append(f'{path}: AUTO markers missing, not updated')
                continue
            new = text[:i0] + block + text[i1 + len(END):]
            if new != text:
                open(path, 'w', encoding='utf-8', newline='\n').write(new)
                updated += 1
        else:
            head = f'# {c.name} ({c.d["cost"]}-cost {c.d["role"]}) · `{c.key}`\n\n'
            open(path, 'w', encoding='utf-8', newline='\n').write(head + block + '\n' + fill_human(c))
            made += 1
    print(f'build {b.version}: {made} worksheets created, {updated} updated')
    for w in warn:
        print('WARNING', w)
    return 0


if __name__ == '__main__':
    sys.exit(main())
