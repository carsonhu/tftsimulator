"""The icons the page shows beside items, augments, traits and champions (square portraits), from the game
client's own art.

    python tools/icons.py            # from set19/: writes icons/<group>/<Class>.png + index.json, traits/tiers.json

Source: the datamining side's set dump (tftDatamine/runs/set19/data.json, tools/set_dump.py there), which names each
item's, augment's and trait's icon texture, and the textures TftExport exported (tftDatamine/runs/set19/textures,
`TftExport --textures`). Each class is matched by its data key (`KEY`), never by display name. Augment icons are
masks the game tints by tier; tftDatamine/tools/augment_tint.py colours them as its set page does.

Output follows set18's icons.py, which app.js reads: one 48x48 PNG per class, an index.json listing them, and for
traits a tiers.json ({tiers: {Class: {level: tier}}, colours}) so the page colours a trait's hexagon by the tier its
breakpoint sits at (the build's tier `prestige`; the colours are the client UI's, not data: set18's values).
Classes without a key (Sunder30 / Shred30, NoItem) get no icon; anything else unmatched is reported.

Stat glyphs (icons/stats/<tag>.png, tag lower-cased, + index.json): the client's rich-text icon table
(/UI_Shared/RichText/DT_RichTextIcons, tftDatamine/runs/set19/rich_text_icons.json: tag -> texture and tint), each
glyph in its tint, as tftDatamine's set page draws them. An item card's stat line ("15%AD") names its tag.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
DATAMINE = os.environ.get('TFT_DATAMINE', r'F:\tft_projects\tftDatamine')
DATA = os.path.join(DATAMINE, 'runs', 'set19', 'data.json')
TEX = os.path.join(DATAMINE, 'runs', 'set19', 'textures')
OUT = os.path.join(ROOT, 'icons')
SIZE = 48
RICH = os.path.join(DATAMINE, 'runs', 'set19', 'rich_text_icons.json')
STAT_SIZE = 32

# set18's tier colours (icons.py there): the hexagon is drawn by the client UI, so these are not in the data
TIER_COLOURS = {
    "bronze": "#b06c3f",
    "silver": "#9fb0c0",
    "gold": "#e3bb63",
    "prismatic": "linear-gradient(135deg, #7ee8e0, #b48be4, #f0c27b)",
    "unique": "linear-gradient(135deg, #7ee8e0, #b48be4, #f0c27b)",
}


def texture(soft):
    """Object path (/Plugin/Path/T_X.T_X) -> the exported PNG, or None."""
    if not soft:
        return None
    p = os.path.join(TEX, soft.split('.', 1)[0].lstrip('/').replace('/', os.sep) + '.png')
    return p if os.path.exists(p) else None


_tinter = None


def tint(im, tier):
    global _tinter
    if _tinter is None:
        sys.path.insert(0, os.path.join(DATAMINE, 'tools'))
        from augment_tint import Tinter
        ui = os.path.join(TEX, 'UI_Augments', 'Textures')
        _tinter = Tinter(os.path.join(ui, 'CVA_AugmentIconColor.png'), os.path.join(ui, 'Tier3.png'))
    return _tinter.tint(im, tier)


def classes():
    """{group: {Class: class object}} for every class the page can show."""
    import set19buffs
    import set19champs
    import set19items
    from registry import REGISTRIES
    items = {n: getattr(set19items, n) for k in ('craftable', 'radiant', 'artifact', 'emblem') for n in REGISTRIES[k]}
    augments = {n: getattr(set19buffs, n) for n in REGISTRIES['augment']}
    traits = {n: getattr(set19buffs, n) for n in REGISTRIES['trait']}
    champions = {n: getattr(set19champs, n) for n in set19champs.champ_list}
    return {'items': items, 'augments': augments, 'traits': traits, 'champions': champions}


def trait_tiers(cls, entry):
    """{level: tier} for the levels the simulator offers: the highest breakpoint at or below the level, else the
    first (a level below the first breakpoint means 'on', as in set18)."""
    steps = sorted((t['threshold'], (t.get('prestige') or '').lower()) for t in entry.get('tiers') or []
                   if t.get('threshold') is not None)
    if not steps:
        return None
    out = {}
    for level in cls.levels:
        if not level:
            continue
        tier = next((t for units, t in reversed(steps) if units <= level), steps[0][1])
        if tier in TIER_COLOURS:
            out[str(level)] = tier
    return out


def main():
    data = json.load(open(DATA, encoding='utf-8'))
    by_key = {g: {e['key']: e for e in data[g]} for g in ('items', 'augments', 'traits', 'champions')}
    for group, found in classes().items():
        out_dir = os.path.join(OUT, group)
        os.makedirs(out_dir, exist_ok=True)
        written, missing, tiers = [], [], {}
        for name, cls in sorted(found.items()):
            key = getattr(cls, 'KEY', None)
            if not key:
                continue  # page entries that are not game objects (Sunder30, Shred30)
            entry = by_key[group].get(key)
            src = texture(entry and entry.get('icon'))
            if src is None:
                missing.append(f'{name} ({key}: {"not in data.json" if entry is None else "texture not exported"})')
                continue
            im = Image.open(src).convert('RGBA')
            if group == 'augments':
                im = tint(im, entry.get('tier') or 'Silver')
            im = im.resize((SIZE, SIZE), Image.LANCZOS)
            im.save(os.path.join(out_dir, name + '.png'), optimize=True)
            written.append(name)
            if group == 'traits':
                t = trait_tiers(cls, entry)
                if t:
                    tiers[name] = t
        with open(os.path.join(out_dir, 'index.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump(sorted(written), f, indent=0)
        if group == 'traits':
            with open(os.path.join(out_dir, 'tiers.json'), 'w', encoding='utf-8', newline='\n') as f:
                json.dump({'tiers': tiers, 'colours': TIER_COLOURS}, f, indent=0, sort_keys=True)
        size = sum(os.path.getsize(os.path.join(out_dir, f)) for f in os.listdir(out_dir))
        print(f'{group}: {len(written)} icons ({size / 1024:.0f} KB)')
        for m in missing:
            print('  missing:', m)


def stat_icons():
    """Every rich-text tag whose texture is exported -> icons/stats/<tag>.png, the glyph in the game's tint."""
    out_dir = os.path.join(OUT, 'stats')
    os.makedirs(out_dir, exist_ok=True)
    written, missing = [], []
    for tag, row in sorted(json.load(open(RICH, encoding='utf-8'))['icons'].items(), key=lambda kv: kv[0].lower()):
        name = tag.lower()
        src = texture(row.get('texture'))
        if src is None or name in written:
            if src is None:
                missing.append(tag)
            continue
        colour = (row.get('tint') or '#ffffff').lstrip('#')
        glyph = Image.open(src).convert('RGBA')
        im = Image.new('RGBA', glyph.size, tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
        im.putalpha(glyph.getchannel('A'))
        im.thumbnail((STAT_SIZE, STAT_SIZE), Image.LANCZOS)
        im.save(os.path.join(out_dir, name + '.png'), optimize=True)
        written.append(name)
    with open(os.path.join(out_dir, 'index.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(sorted(written), f, indent=0)
    print(f'stats: {len(written)} icons; no texture: {", ".join(missing) or "none"}')


if __name__ == '__main__':
    main()
    stat_icons()
