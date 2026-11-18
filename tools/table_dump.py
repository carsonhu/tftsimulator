"""Dump every results table for every champion, to diff two runs (docs/RESTRUCTURE.md, step 0).

    python tools/table_dump.py out.json            # newest build
    python tools/table_dump.py out.json --build <version>
    python tools/table_dump.py --diff before.json after.json

For each champion at 1 and 2 stars it runs every slice the page offers (with the champion's own traits on at their
first breakpoint, so the Trait slice has rows), and records each row's DPS and ratio columns plus the full damage
vector of the row's trial and the champion's stats panel. A restructuring step is done only when --diff finds
nothing.
"""
import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, ROOT)

import set19buffs  # noqa: E402
import set19champs  # noqa: E402
import sim_entry  # noqa: E402

LEVELS = (1, 2)


def config(champ, level, build, slice_name):
    cls = getattr(set19champs, champ)
    fresh = cls(level, build=sim_entry.load_build(build))
    buffs = []
    for trait in fresh.default_traits:
        if trait in set19buffs.class_buffs:
            levels = [l for l in getattr(set19buffs, trait).levels if l > 0]
            buffs.append([trait, levels[0], 0])
    return {"champ": champ, "level": level, "build": build, "stage": "4-1", "tactician_level": 4,
            "items": ["NoItem"] * 3, "buffs": buffs, "enemy": {"hp": 1800, "armor": 100, "mr": 100},
            "frame_rate": 30, "t": 30, "slice": slice_name}


def dump(build):
    catalog = sim_entry.get_catalog()
    out = {}
    for champ in sorted(set19champs.champ_list):
        for level in LEVELS:
            info = sim_entry.get_champ_info(config(champ, level, build, "Craftable"))
            out[f"{champ}/{level}/stats"] = info["stats"]
            for slice_name in catalog["slices"]:
                res = sim_entry.run_slice(config(champ, level, build, slice_name))
                rows = {}
                for r in res["rows"]:
                    tl = res["timelines"][str(r["idx"])]
                    rows[r["extra"]] = {"dps": r["dps"], "ratio": r["ratio"],
                                        "t": tl["t"], "dmg": tl["dmg"], "type": tl["type"]}
                out[f"{champ}/{level}/{slice_name}"] = rows
    return out


def diff(a, b, path=""):
    """Every difference between two dumps, as 'path: a != b' lines."""
    if isinstance(a, dict) and isinstance(b, dict):
        lines = []
        for k in sorted(set(a) | set(b), key=str):
            if k not in a:
                lines.append(f"{path}/{k}: only in the second")
            elif k not in b:
                lines.append(f"{path}/{k}: only in the first")
            else:
                lines += diff(a[k], b[k], f"{path}/{k}")
        return lines
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        lines = []
        for i, (x, y) in enumerate(zip(a, b)):
            lines += diff(x, y, f"{path}[{i}]")
            if len(lines) > 5:
                break
        return lines
    return [] if a == b else [f"{path}: {str(a)[:80]} != {str(b)[:80]}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?")
    ap.add_argument("--build")
    ap.add_argument("--diff", nargs=2)
    args = ap.parse_args()
    if args.diff:
        a, b = (json.load(open(p, encoding="utf-8")) for p in args.diff)
        lines = diff(a, b)
        print("\n".join(lines[:200]) if lines else "identical")
        sys.exit(1 if lines else 0)
    data = dump(args.build)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"{len(data)} tables -> {args.out}")


if __name__ == "__main__":
    main()
