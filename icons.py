"""Download the icons the results table shows, from CommunityDragon.

    python icons.py                       # build icons/ from the cached dump
    python icons.py --refresh             # re-download the dump first
    python icons.py augments              # just one group
    python icons.py --contact-sheet       # write a labelled sheet to check by eye

Writes one 48x48 PNG per class into icons/<group>/, named after the class in
set18items / set18buffs (Archangels.png, GlassCannonI.png, ...), plus an
index.json listing what exists. app.js reads those indexes and only renders an
<img> for a row whose class is in one, so the trait and wisp rows -- which have
no icon -- cost no failed requests.

Matching is by display name against CommunityDragon's en_us.json, normalised to
ignore case, punctuation and the parenthetical qualifiers this project adds
("Giant Slayer (no Giant)" is Giant Slayer's icon, "Hold The Line (5 units)" is
Hold the Line's). Names Riot spells differently, or that are shorthand, are
pinned by apiName in each group's OVERRIDES. Anything else that fails to match
is reported rather than skipped silently, so a renamed entry shows up as a line
to fix rather than a missing icon nobody notices.

The two things that make blind name matching dangerous, both caught by eye on a
contact sheet and both now guarded against:

  * a name can collide with something that is not the kind of thing you asked
    for -- "Red (no burn)" reduces to "red" and matched a Set 11 encounter item
    literally called Red, whose art is a transparent placeholder. Hence
    ALLOWED_PATHS per group.
  * Riot ships placeholder art in-band: fully transparent icons, and files
    literally named Missing-T2 / Missing-T3. Both are refused.

An augment additionally gets its rarity cross-checked against the tier suffix
on its art, which catches a match landing on the wrong tier's picture without
anyone having to notice by eye. Exactly one Set 18 augment disagrees, and it is
Riot's own data rather than a bad match -- see the TonsOfStatsPris override.

Two quirks worth knowing rather than rediscovering. The asset path for
Flickerblades really is misspelled "Flickerplade", and Red Buff is filed under
RapidFireCannon -- matching on the item's name rather than its icon path is
what makes both survivable. And Riot's augment art is numbered by tier in a way
that does not line up with the augment's own tier: Jeweled Lotus I's icon file
is Jeweled-Lotus-II.tex. The apiName is the authority, not the filename.
"""

import argparse
import collections
import io
import json
import os
import re
import sys
import urllib.request

from PIL import Image, ImageDraw

CHANNEL = "pbe"
CACHE = os.path.join(".tft_cache", CHANNEL, "en_us.json")
DATA_URL = f"https://raw.communitydragon.org/{CHANNEL}/cdragon/tft/en_us.json"
GAME_URL = f"https://raw.communitydragon.org/{CHANNEL}/game/"
SIZE = 48

# raw.communitydragon.org answers 403 to a request with no User-Agent.
HEADERS = {"User-Agent": "tftsimulator-icons/1.0"}


def item_entries():
    """(class name, display name) for every item the sidebar can offer."""
    import set18items

    groups = (
        set18items.offensive_craftables
        + set18items.artifacts
        + set18items.radiants
        + set18items.emblems
        + set18items.animas
    )
    return _entries(set18items, dict.fromkeys(groups))  # the radiant list repeats one


def augment_entries():
    """(class name, display name) for every row of the Augment/Buff slice."""
    import set18buffs

    return _entries(set18buffs, set18buffs.augments)


def _entries(module, names):
    out = []
    for cls_name in names:
        cls = getattr(module, cls_name)
        out.append((cls_name, getattr(cls, "display_name", None) or cls_name))
    return out


GROUPS = {
    "items": {
        "entries": item_entries,
        # Item art lives in one of two trees: Icons/Items for the standard
        # ones, Particles/.../Item_Icons for artifacts, region items and trait
        # emblems.
        "allowed_paths": ("/icons/items/", "/item_icons/"),
        # The same icon is published under several apiNames; they point at one
        # file, so any is fine -- prefer Riot's canonical item namespace.
        "prefer": "TFT_Item_",
        "overrides": {
            "HextechGunblade": "TFT_Item_HextechGunblade",
            "Archangels": "TFT_Item_ArchangelsStaff",
            "Morellos": "TFT_Item_Morellonomicon",
            "Flickerblade": "TFT_Item_Artifact_NavoriFlickerblades",
            # Riot files Red Buff under RapidFireCannon; see the module note on
            # what "Red (no burn)" matched before this pin existed.
            "Red": "TFT_Item_RapidFireCannon",
            "RadiantArchangels": "TFT5_Item_ArchangelsStaffRadiant",
            "RadiantTitans": "TFT5_Item_TitansResolveRadiant",
            "RadiantRed": "TFT5_Item_RapidFirecannonRadiant",
            "RadiantMorellos": "TFT5_Item_MorellonomiconRadiant",
        },
        "no_icon": {},
    },
    "augments": {
        "entries": augment_entries,
        "allowed_paths": ("/icons/augments/",),
        # An augment that has run in several sets appears once per set
        # (TFT6_Augment_Ascension, TFT9_Augment_Commander_Ascension, ...) with
        # the same name. DA_ is the current set's data, so it is the one whose
        # art the game is showing right now; the older entries are the fallback
        # for augments this set did not re-file.
        "prefer": "DA_",
        "overrides": {
            # Gold and Prismatic Tons of Stats share a name, so the name alone
            # cannot separate them. Both end up on the gold art anyway: the
            # Prismatic augment is real (DA_TonsOfStatsII, tagged prismatic)
            # but Riot never drew it a tons-of-stats-iii, and points it at the
            # gold file instead. rarity_mismatch() reports that every run.
            "TonsOfStatsPris": "DA_TonsOfStatsII",
        },
        # Not augments at all -- bare effects the sweep offers for comparison,
        # with nothing in Riot's data to point at.
        "no_icon": {
            "Shred30": "a raw shred value, not an augment",
            "Shred20": "a raw shred value, not an augment",
        },
    },
}


def fetch(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request) as response:
        return response.read()


def load_catalog(refresh):
    if refresh or not os.path.exists(CACHE):
        print(f"downloading {DATA_URL} ...")
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "wb") as handle:
            handle.write(fetch(DATA_URL))
    with open(CACHE, encoding="utf-8") as handle:
        return json.load(handle)["items"]


def normalise(name):
    name = re.sub(r"\([^)]*\)", " ", name.lower())
    return re.sub(r"[^a-z0-9]+", "", name)


# An augment's rarity is a hashed tag on the item, and its art is filed with a
# matching tier suffix -- Ascension1 / GlassCannon_I / jeweled-lotus-iii. The
# two agree for every Set 18 augment except one, so comparing them is a cheap
# way to notice when a match landed on the wrong tier's art. It is reported as
# a note rather than a failure: the one disagreement is Riot's, not a bad
# match, and no override can fix art that was never drawn.
RARITY_TAGS = {"{d11fd6d5}": "silver", "{ce1fd21c}": "gold", "{cf1fd3af}": "prismatic"}
RARITY_SUFFIXES = {
    "i": "silver", "1": "silver",
    "ii": "gold", "2": "gold",
    "iii": "prismatic", "3": "prismatic",
}


# Each rarity paints its art in one narrow band of hue, which is what makes
# the recolour below possible: sampled as the median over the opaque, coloured
# pixels of several icons per rarity, they cluster at silver 191-192, gold
# 53-54, prismatic 253-278. Saturation is a band too, but a much looser one --
# individual gold icons range from 0.41 to 0.75 -- so the target below is a
# level to normalise onto rather than a ratio to scale by.
RARITY_LOOK = {
    "silver": (191 / 360.0, 0.30),
    "gold": (53 / 360.0, 0.45),
    "prismatic": (272 / 360.0, 0.30),
}

# Below this saturation a pixel is a grey -- a shadow or a white highlight --
# and carries no hue worth measuring.
COLOURED = 64


def rarity_mismatch(match):
    """('prismatic', 'gold') when the tag and the icon's tier disagree."""
    tags = [RARITY_TAGS[t] for t in match.get("tags", []) if t in RARITY_TAGS]
    suffix = re.search(r"[-_]?(i{1,3}|[123])\.(?:tex|dds)$", match["icon"].lower())
    if len(tags) != 1 or not suffix:
        return None
    art = RARITY_SUFFIXES[suffix.group(1)]
    return None if art == tags[0] else (tags[0], art)


def median_saturation(sats, alpha):
    """Median saturation, 0-1, over this icon's opaque coloured pixels."""
    opaque = alpha.point(lambda level: 255 if level > 128 else 0)
    counts = sats.histogram(mask=opaque)[COLOURED + 1:]
    total = sum(counts)
    seen = 0
    for offset, count in enumerate(counts):
        seen += count
        if seen * 2 >= total:
            return (COLOURED + 1 + offset) / 255
    return None


def recolour(image, want, got):
    """Repaint art drawn for one rarity in the colours of another.

    Only reached when Riot tagged an augment one rarity and pointed it at
    another's picture, which as of Set 18 is Prismatic Tons of Stats alone: the
    Prismatic augment is real but no tons-of-stats-iii was ever drawn, so both
    it and the Gold version would otherwise sit in the table as the same yellow
    hexagon under near-identical names.

    Hue is replaced rather than rotated -- a rarity's art is one narrow band,
    so there is no spread worth preserving. Saturation is normalised onto the
    target rarity's level using this icon's own median, not scaled by a ratio
    between the two rarities: gold icons are individually anywhere from 0.41 to
    0.75 saturated, so a fixed ratio leaves a vivid source still vivid after it
    turns purple, which is exactly what it looked like on the first attempt.
    Value and alpha are untouched, so the shading and the shape survive; the
    greys go along for the ride harmlessly, since scaling a saturation of
    nearly zero leaves it nearly zero.
    """
    if want not in RARITY_LOOK or got not in RARITY_LOOK:
        return None
    hue, want_sat = RARITY_LOOK[want]
    hues, sats, values = image.convert("RGB").convert("HSV").split()
    median = median_saturation(sats, image.getchannel("A"))
    if not median:
        return None
    scale = want_sat / median
    painted = Image.merge(
        "HSV",
        (
            hues.point(lambda _: round(hue * 255)),
            sats.point(lambda level: min(255, round(level * scale))),
            values,
        ),
    ).convert("RGB")
    painted.putalpha(image.getchannel("A"))
    return painted


def resolve(group, items):
    by_api = {i["apiName"]: i for i in items}
    by_name = collections.defaultdict(list)
    for item in items:
        if item.get("name"):
            by_name[normalise(item["name"])].append(item)

    resolved, missing, notes = {}, [], []
    for cls_name, display in group["entries"]():
        if cls_name in group["no_icon"]:
            continue
        if cls_name in group["overrides"]:
            match = by_api.get(group["overrides"][cls_name])
        else:
            candidates = by_name.get(normalise(display), [])
            match = (
                sorted(
                    candidates,
                    key=lambda i: (
                        not i["apiName"].startswith(group["prefer"]),
                        len(i["apiName"]),
                    ),
                )[0]
                if candidates
                else None
            )
        if not (match and match.get("icon")):
            missing.append((cls_name, display + " (no match)"))
            continue
        icon, api = match["icon"], match["apiName"]
        if not any(p in icon.lower() for p in group["allowed_paths"]):
            trees = " or ".join(group["allowed_paths"])
            missing.append((cls_name, f"{display} -> {api} is not in {trees}: {icon}"))
            continue
        if os.path.basename(icon).lower().startswith("missing"):
            missing.append((cls_name, f"{display} -> {api} is placeholder art: {icon}"))
            continue
        mismatch = rarity_mismatch(match)
        if mismatch:
            want, got = mismatch
            art = os.path.basename(icon)
            notes.append((cls_name, f"{want} augment on {got} art ({art}); recoloured"))
        resolved[cls_name] = (display, api, icon, mismatch)
    return resolved, missing, notes


def icon_url(path):
    # ".../Foo.tex" -> ".../foo.png", lowercased: that is how the game assets
    # are published over HTTP.
    return GAME_URL + re.sub(r"\.(tex|dds)$", ".png", path.lower())


def build(name, group, items):
    out_dir = os.path.join("icons", name)
    resolved, missing, notes = resolve(group, items)
    os.makedirs(out_dir, exist_ok=True)

    written = []
    for cls_name, (display, api, path, mismatch) in sorted(resolved.items()):
        url = icon_url(path)
        try:
            raw = fetch(url)
            image = Image.open(io.BytesIO(raw)).convert("RGBA")
            # A fully transparent icon is a placeholder, not artwork; it would
            # otherwise ship as an invisible gap in the table.
            if image.getchannel("A").getextrema()[1] == 0:
                missing.append((cls_name, f"{display} -> {api} icon is blank"))
                continue
            # Recolour before the downscale, so the resample averages the
            # colours the icon will actually ship in.
            if mismatch:
                image = recolour(image, *mismatch) or image
            image = image.resize((SIZE, SIZE), Image.LANCZOS)
            image.save(os.path.join(out_dir, cls_name + ".png"), optimize=True)
            written.append(cls_name)
        except Exception as error:  # noqa: BLE001 - report and keep going
            missing.append((cls_name, f"{display} <- {url} ({error})"))

    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as handle:
        json.dump(sorted(written), handle, indent=0)

    total = sum(os.path.getsize(os.path.join(out_dir, f)) for f in os.listdir(out_dir))
    print(f"{name}: wrote {len(written)} icons to {out_dir} ({total / 1024:.0f} KB)")
    for cls_name, why in group["no_icon"].items():
        print(f"  no icon by design: {cls_name} ({why})")
    for cls_name, why in notes:
        print(f"  note: {cls_name:24s} {why}")
    if missing:
        print(f"  {len(missing)} unresolved -- add an OVERRIDES entry:")
        for cls_name, why in missing:
            print(f"    {cls_name:26s} {why}")
    return out_dir, written, missing


def contact_sheet(sheets):
    """One labelled grid per group, to check the matches by eye.

    Worth the two minutes: a wrong match is a plausible-looking icon, so the
    only thing that catches it is looking. This is how "Red (no burn)" was
    caught shipping a transparent square.
    """
    columns, cell, pad = 8, SIZE, 26
    for out_dir, written in sheets:
        rows = (len(written) + columns - 1) // columns
        size = (columns * (cell + 8), rows * (cell + pad))
        sheet = Image.new("RGBA", size, (24, 26, 30, 255))
        draw = ImageDraw.Draw(sheet)
        for index, cls_name in enumerate(sorted(written)):
            x = (index % columns) * (cell + 8) + 4
            y = (index // columns) * (cell + pad)
            icon = Image.open(os.path.join(out_dir, cls_name + ".png"))
            sheet.paste(icon, (x, y), None)
            draw.text((x, y + cell + 2), cls_name[:14], fill=(220, 224, 230))
        path = out_dir + "_sheet.png"
        sheet.save(path)
        print(f"contact sheet: {path}")


def main():
    parser = argparse.ArgumentParser()
    groups = list(GROUPS)
    parser.add_argument("groups", nargs="*", choices=groups + [[]], help="default: all")
    parser.add_argument("--refresh", action="store_true", help="re-download the dump")
    parser.add_argument("--contact-sheet", action="store_true", help="check by eye")
    args = parser.parse_args()

    items = load_catalog(args.refresh)
    sheets, failed = [], 0
    for name in args.groups or GROUPS:
        out_dir, written, missing = build(name, GROUPS[name], items)
        sheets.append((out_dir, written))
        failed += len(missing)

    if args.contact_sheet:
        contact_sheet(sheets)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
