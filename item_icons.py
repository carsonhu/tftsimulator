"""Download the item icons the results table shows, from CommunityDragon.

    python item_icons.py            # build icons/items/ from the cached dump
    python item_icons.py --refresh  # re-download the dump first

Writes one 48x48 PNG per item class into icons/items/, named after the class
in set18items (Archangels.png, GSNoGiant.png, ...), plus an index.json listing
what exists. app.js reads that index and only renders an <img> for a row whose
class is in it, so the buff and trait rows -- which have no icon -- cost no
failed requests.

Matching is by display name against the item list in CommunityDragon's
en_us.json, normalised to ignore case, punctuation and the parenthetical
qualifiers this project adds ("Giant Slayer (no Giant)" is Giant Slayer's
icon). The eight names that are shorthand rather than Riot's own -- Archangels
for Archangel's Staff, Morellos for Morellonomicon -- are listed in OVERRIDES
by apiName. Anything that fails to match is reported rather than skipped
silently, so a renamed item shows up as a line to fix rather than a missing
icon nobody notices.

Note the asset path for Flickerblades really is misspelled "Flickerplade" in
Riot's data; matching on the item's name rather than its icon path is what
makes that survivable.
"""

import argparse
import collections
import io
import json
import os
import re
import sys
import urllib.request

CHANNEL = "pbe"
CACHE = os.path.join(".tft_cache", CHANNEL, "en_us.json")
DATA_URL = f"https://raw.communitydragon.org/{CHANNEL}/cdragon/tft/en_us.json"
GAME_URL = f"https://raw.communitydragon.org/{CHANNEL}/game/"
OUT_DIR = os.path.join("icons", "items")
SIZE = 48

# raw.communitydragon.org answers 403 to a request with no User-Agent.
HEADERS = {"User-Agent": "tftsimulator-item-icons/1.0"}

# Project display names that are shorthand for Riot's, resolved by apiName.
OVERRIDES = {
    "HextechGunblade": "TFT_Item_HextechGunblade",
    "Archangels": "TFT_Item_ArchangelsStaff",
    "Morellos": "TFT_Item_Morellonomicon",
    "Flickerblade": "TFT_Item_Artifact_NavoriFlickerblades",
    # "Red (no burn)" reduces to "red", which collides with a Set 11 encounter
    # item literally called Red whose icon is a transparent placeholder. Riot
    # files Red Buff under RapidFireCannon.
    "Red": "TFT_Item_RapidFireCannon",
    "RadiantArchangels": "TFT5_Item_ArchangelsStaffRadiant",
    "RadiantTitans": "TFT5_Item_TitansResolveRadiant",
    "RadiantRed": "TFT5_Item_RapidFirecannonRadiant",
    "RadiantMorellos": "TFT5_Item_MorellonomiconRadiant",
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


def project_items():
    """(class name, display name) for every item the sidebar can offer."""
    import set18items

    groups = (
        set18items.offensive_craftables
        + set18items.artifacts
        + set18items.radiants
        + set18items.emblems
        + set18items.animas
    )
    out = []
    for cls_name in dict.fromkeys(groups):  # the radiant list repeats one entry
        cls = getattr(set18items, cls_name)
        out.append((cls_name, getattr(cls, "display_name", None) or cls_name))
    return out


def resolve(items):
    by_api = {i["apiName"]: i for i in items}
    by_name = collections.defaultdict(list)
    for item in items:
        if item.get("name"):
            by_name[normalise(item["name"])].append(item)

    resolved, missing = {}, []
    for cls_name, display in project_items():
        if cls_name in OVERRIDES:
            match = by_api.get(OVERRIDES[cls_name])
        else:
            candidates = by_name.get(normalise(display), [])
            # The same icon is published under several apiNames (DA_*, TFT_*);
            # they point at one file, so any is fine -- prefer the canonical.
            match = sorted(
                candidates,
                key=lambda i: (not i["apiName"].startswith("TFT_Item_"), len(i["apiName"])),
            )[0] if candidates else None
        if not (match and match.get("icon")):
            missing.append((cls_name, display + " (no match)"))
            continue
        # Item art lives in one of two trees: Icons/Items for the standard
        # ones, Particles/.../Item_Icons for artifacts, region items and trait
        # emblems. Anything outside both means the name collided with
        # something that is not an item -- an encounter choice, an augment --
        # which is how "Red (no burn)" once matched a transparent admin
        # placeholder from Icons/Augments/ChoiceUI.
        icon_path = match["icon"].lower()
        if "/icons/items/" not in icon_path and "/item_icons/" not in icon_path:
            missing.append((cls_name, f"{display} -> {match['apiName']} is not an item icon: {match['icon']}"))
            continue
        resolved[cls_name] = (display, match["apiName"], match["icon"])
    return resolved, missing


def icon_url(path):
    # ".../Foo.tex" -> ".../foo.png", lowercased: that is how the game assets
    # are published over HTTP.
    return GAME_URL + re.sub(r"\.(tex|dds)$", ".png", path.lower())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="re-download the dump")
    args = parser.parse_args()

    from PIL import Image

    items = load_catalog(args.refresh)
    resolved, missing = resolve(items)
    os.makedirs(OUT_DIR, exist_ok=True)

    written = []
    for cls_name, (display, api, path) in sorted(resolved.items()):
        url = icon_url(path)
        try:
            raw = fetch(url)
            image = Image.open(io.BytesIO(raw)).convert("RGBA")
            # A fully transparent icon is a placeholder, not artwork; it would
            # otherwise ship as an invisible gap in the table.
            if image.getchannel("A").getextrema()[1] == 0:
                missing.append((cls_name, f"{display} -> {api} icon is blank"))
                continue
            image = image.resize((SIZE, SIZE), Image.LANCZOS)
            image.save(os.path.join(OUT_DIR, cls_name + ".png"), optimize=True)
            written.append(cls_name)
        except Exception as error:  # noqa: BLE001 - report and keep going
            missing.append((cls_name, f"{display} <- {url} ({error})"))

    with open(os.path.join(OUT_DIR, "index.json"), "w", encoding="utf-8") as handle:
        json.dump(sorted(written), handle, indent=0)

    total = sum(os.path.getsize(os.path.join(OUT_DIR, f)) for f in os.listdir(OUT_DIR))
    print(f"wrote {len(written)} icons to {OUT_DIR} ({total / 1024:.0f} KB total)")
    if missing:
        print(f"\n{len(missing)} unresolved -- add an OVERRIDES entry:")
        for cls_name, why in missing:
            print(f"  {cls_name:26s} {why}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
