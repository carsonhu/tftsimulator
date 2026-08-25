"""Compare the simulator's numbers against reference/tft_data.json.

    python patch_check.py              # report drift
    python patch_check.py --coverage   # also list what nothing checks
    python patch_check.py --json       # machine-readable, for a diff

Reads only. It will never edit a champion or a trait, and that is the point:
"PBE moved" and "I want to follow PBE" are separate decisions, and only the
second one is yours to make. The checker answers the first and stops.

Exit code is 1 when something drifted, so it can gate a commit if you ever
want it to.


How to use it after a patch
---------------------------
    python tft_data.py diff --refresh    # what moved on CommunityDragon
    python patch_check.py                # which of that we actually model

The first is the whole game; the second is the ~40 numbers this simulator has
an opinion about. Most patches touch nothing here.

Then, for anything the checker calls UNBACKED -- champion ability damage, cast
times -- open the patch notes, because CommunityDragon does not have them. At
the time of writing 2 of the set's 99 champions have real spell DataValues and
the rest still carry the bin template's placeholders, so every ability number
in this simulator was read off a champion card by a person. patch_pin.json
records which patch each was read on; when that is behind, they need eyes.

A number that deliberately disagrees with the reference belongs in
patch_pin.json's "acknowledged" block with the reason, which is what keeps
this report short enough to be worth reading.
"""

import argparse
import json
import os
import sys

import set18buffs
import set18champs
from patch_hooks import (
    CHAMPION_API,
    DERIVED_TRAIT_HOOKS,
    STAT_FIELDS,
    TRAIT_CARD_ONLY,
    TRAIT_HOOKS,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REFERENCE = os.path.join(HERE, "reference", "tft_data.json")
PIN = os.path.join(HERE, "patch_pin.json")

# Reference floats arrive as float32 widened to float64 (0.15000000596046448),
# so an exact compare would report every value as drifted.
TOLERANCE = 1e-4


def load(path, what):
    if not os.path.exists(path):
        sys.exit(f"no {what} at {path} -- run `python tft_data.py update` first")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def close(a, b):
    try:
        return abs(float(a) - float(b)) <= TOLERANCE * max(1.0, abs(float(b)))
    except (TypeError, ValueError):
        return a == b


def trait_breakpoints(data, api_name):
    """{minUnits: {variable: value}} for one trait, or None if it is gone."""
    for trait in data["traits"]:
        if trait["apiName"] == api_name:
            return {
                bp["minUnits"]: (bp.get("variables") or {})
                for bp in trait["breakpoints"]
            }
    return None


def champion_record(data, api_name):
    for champ in data["champions"]:
        if champ["apiName"] == api_name:
            return champ
    return None


def code_value(cls, attr):
    """The trait's value for attr, from a class or a throwaway instance."""
    if hasattr(cls, attr):
        return getattr(cls, attr)
    for level in reversed(cls.levels):
        try:
            return getattr(cls(level, 0), attr)
        except Exception:
            continue
    raise AttributeError(attr)


class Report:
    def __init__(self):
        self.drift = []      # a number the reference disagrees with
        self.acknowledged = []  # ... that patch_pin.json already knows about
        self.unbacked = []   # nothing in the reference can confirm it
        self.broken = []     # the hook itself no longer resolves
        self.unverified = []  # a card value nobody has checked against a patch
        self.published = []  # cdragon now has real spell data for this unit
        self.checked = 0

    def compare(self, key, code, ref, ack, detail=""):
        self.checked += 1
        if close(code, ref):
            return
        if key in ack:
            entry = ack[key]
            # An acknowledgement is a claim about two specific numbers. If
            # either has moved since it was written it is no longer about this
            # disagreement, so it stops applying rather than covering whatever
            # the values happen to be now.
            if close(entry.get("code"), code) and close(entry.get("reference"), ref):
                self.acknowledged.append((key, code, ref, entry.get("why", "")))
                return
            detail = (detail + " " if detail else "") + (
                f"[stale acknowledgement: pinned {entry.get('code')} vs "
                f"{entry.get('reference')}]"
            )
        self.drift.append((key, code, ref, detail))


def check_traits(data, report, ack):
    for cls_name, attr, api_name, variable, scale in TRAIT_HOOKS:
        cls = getattr(set18buffs, cls_name, None)
        breakpoints = trait_breakpoints(data, api_name)
        if cls is None or breakpoints is None:
            report.broken.append(
                f"{cls_name}.{attr}: "
                + ("no such trait class" if cls is None else f"{api_name} not in reference")
            )
            continue
        try:
            value = code_value(cls, attr)
        except AttributeError:
            report.broken.append(f"{cls_name}.{attr}: no such attribute")
            continue

        if isinstance(value, dict):
            for level, code in value.items():
                # Level 0 is the trait being off, which the data has no row
                # for -- it is this simulator's own convention.
                if level == 0:
                    continue
                variables = breakpoints.get(level)
                if variables is None or variable not in variables:
                    # A breakpoint that grants none of this is written as 0 in
                    # the code and simply omitted in the data -- Executioner
                    # (2) is crit only, with no bleed until (3). The two agree.
                    if close(code, 0):
                        report.checked += 1
                        continue
                    report.broken.append(
                        f"{cls_name}.{attr}[{level}]: no {variable} at ({level}) "
                        f"in {api_name}"
                    )
                    continue
                report.compare(
                    f"{cls_name}.{attr}[{level}]",
                    code,
                    variables[variable] * scale,
                    ack,
                )
        else:
            # A flat number the data repeats at every breakpoint (an aura).
            found = [v[variable] for v in breakpoints.values() if variable in v]
            if not found:
                report.broken.append(f"{cls_name}.{attr}: no {variable} in {api_name}")
                continue
            if len({round(f, 6) for f in found}) > 1:
                report.broken.append(
                    f"{cls_name}.{attr}: {variable} is not flat in {api_name} "
                    f"({sorted(set(found))}) -- the hook should be a dict"
                )
                continue
            report.compare(f"{cls_name}.{attr}", value, found[0] * scale, ack)


def check_derived(data, report, ack):
    for cls_name, attr, api_name, variable, rule, why in DERIVED_TRAIT_HOOKS:
        cls = getattr(set18buffs, cls_name, None)
        breakpoints = trait_breakpoints(data, api_name)
        if cls is None or breakpoints is None:
            report.broken.append(f"{cls_name}.{attr}: hook no longer resolves")
            continue
        if rule is None:
            # The code applies a rule the data does not express; all the
            # checker can do is confirm the row it is derived from.
            report.unbacked.append(f"{cls_name}.{attr} -- {why}")
            continue
        try:
            value = code_value(cls, attr)
        except AttributeError:
            report.broken.append(f"{cls_name}.{attr}: no such attribute")
            continue
        for level, code in (value.items() if isinstance(value, dict) else []):
            variables = breakpoints.get(level) or {}
            if variable not in variables:
                # Blackthorn (2) has a Health row but no StatMultiplier: the
                # first breakpoint grants no bonus, which the code writes as
                # a 1.0 multiplier. Not a missing hook.
                if close(code, 1.0):
                    continue
                report.broken.append(
                    f"{cls_name}.{attr}[{level}]: no {variable} at ({level})"
                )
                continue
            report.compare(
                f"{cls_name}.{attr}[{level}]",
                code,
                rule(variables[variable]),
                ack,
                f"({why})",
            )


def check_champions(data, report, ack):
    for name in set18champs.champ_list:
        api_name = CHAMPION_API.get(name)
        if api_name is None:
            report.broken.append(f"{name}: no apiName in patch_hooks.CHAMPION_API")
            continue
        record = champion_record(data, api_name)
        if record is None:
            report.broken.append(f"{name}: {api_name} not in reference")
            continue
        champ = getattr(set18champs, name)(1)
        stats = record.get("stats") or {}
        for attr, field in STAT_FIELDS.items():
            ref = stats.get(field)
            if ref is None:
                continue
            report.compare(
                f"{name}.{field}", getattr(champ, attr).base, ref, ack
            )


def check_card_values(report, pin):
    """Ability numbers a person read off a card. Confirm the code still agrees.

    This catches the edit nobody meant to make. It cannot catch a balance
    patch -- only the patch label moving tells you to go and look.
    """
    for key, entry in sorted((pin.get("card_values") or {}).items()):
        owner, _, attr = key.partition(".")
        cls = getattr(set18champs, owner, None) or getattr(set18buffs, owner, None)
        if cls is None:
            report.broken.append(f"card_values[{key}]: no such class")
            continue
        try:
            value = code_value(cls, attr)
        except AttributeError:
            report.broken.append(f"card_values[{key}]: no such attribute")
            continue
        for half in ("ad", "ap"):
            recorded = entry.get(half)
            if recorded is None:
                continue
            actual = list(getattr(value, f"{half}_values", []) or [])
            if actual != list(recorded):
                report.drift.append((
                    f"{key}.{half}", actual, list(recorded),
                    f"code no longer matches what was recorded on "
                    f"{entry.get('read_on')}",
                ))
            report.checked += 1
        if entry.get("read_on") == "unverified":
            report.unverified.append(key)


def check_spell_data_published(data, report, pin):
    """Has Riot started shipping real spell numbers for anyone we model?

    Every ability number here was read off a card because the champion bins
    carry the template's placeholder DataValues (0/1/2/10...). That is a fact
    about right now, not forever: bins get authored, and a set that goes live
    has them. The moment one flips, its ability numbers stop being a hand-read
    CARD value and become checkable like everything else -- so this looks every
    run rather than leaving the assumption to rot.

    It reports rather than compares. A published bin names its values
    (PrimaryMagicDamage, MagicDamage) but says nothing about which tooltip line
    each feeds or how the card splits them, and this simulator's scalings are
    shaped by the card. Matching the two up is a reading job.
    """
    known = set(pin.get("spell_data_published") or [])
    for name, api_name in sorted(CHAMPION_API.items()):
        record = champion_record(data, api_name)
        spell = (record or {}).get("spell") or {}
        if not spell.get("dataValues") or spell.get("dataValuesArePlaceholder"):
            continue
        report.published.append((name, sorted(spell["dataValues"]), name in known))


def coverage(data, pin):
    """Modeled things with no hook pointing at them."""
    hooked = {h[0] for h in TRAIT_HOOKS} | {h[0] for h in DERIVED_TRAIT_HOOKS}
    hooked |= set(TRAIT_CARD_ONLY)
    missing_traits = [t for t in set18buffs.class_buffs if t not in hooked]
    card_owners = {k.partition(".")[0] for k in (pin.get("card_values") or {})}
    no_card = [c for c in set18champs.champ_list if c not in card_owners]
    return missing_traits, no_card


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--coverage", action="store_true",
                        help="also list modeled values nothing checks")
    parser.add_argument("--json", action="store_true", help="machine-readable")
    args = parser.parse_args(argv)

    data = load(REFERENCE, "reference data")
    pin = load(PIN, "pin") if os.path.exists(PIN) else {}
    ack = pin.get("acknowledged") or {}

    report = Report()
    check_traits(data, report, ack)
    check_derived(data, report, ack)
    check_champions(data, report, ack)
    check_card_values(report, pin)
    check_spell_data_published(data, report, pin)
    for cls_name, attrs in sorted(TRAIT_CARD_ONLY.items()):
        for attr in attrs:
            report.unbacked.append(
                f"{cls_name}.{attr} -- the trait carries no such variable"
            )

    if args.json:
        print(json.dumps({
            "checked": report.checked,
            "drift": report.drift,
            "acknowledged": [list(a) for a in report.acknowledged],
            "unbacked": report.unbacked,
            "unverified": report.unverified,
            "published": [[p[0], p[1]] for p in report.published if not p[2]],
            "broken": report.broken,
        }, indent=1))
        return 1 if report.drift or report.broken else 0

    print(f"reference: set {data.get('set')} from cdragon {data.get('channel')}, "
          f"string table v{data.get('stringTableVersion')}")
    if pin:
        print(f"pinned:    {pin.get('patch')}, accepted {pin.get('accepted')}")
    print(f"checked:   {report.checked} values\n")

    if report.drift:
        print(f"DRIFTED ({len(report.drift)}) -- code first, reference second:")
        for key, code, ref, detail in report.drift:
            print(f"  {key:38} {code}  ->  {ref}  {detail}".rstrip())
        print()
    else:
        print("No drift: every checked value matches the reference.\n")

    if report.broken:
        print(f"BROKEN HOOKS ({len(report.broken)}) -- these check nothing:")
        for line in report.broken:
            print(f"  {line}")
        print()

    if report.acknowledged:
        print(f"acknowledged ({len(report.acknowledged)}) -- deliberate, see patch_pin.json:")
        for key, code, ref, why in report.acknowledged:
            print(f"  {key:38} {code} vs {ref}  {why}")
        print()

    fresh = [p for p in report.published if not p[2]]
    if fresh:
        print(f"SPELL DATA NOW PUBLISHED ({len(fresh)}) -- CommunityDragon has real")
        print("DataValues for these, so their ability numbers no longer have to be")
        print("hand-read. Compare them against the card, then add the name to")
        print("patch_pin.json's spell_data_published to stop this notice:")
        for name, keys, _ in fresh:
            print(f"  {name:12} {', '.join(keys)}")
        print()

    if report.unverified:
        print(f"NEVER VERIFIED ({len(report.unverified)}) -- ability numbers with no")
        print("patch recorded against them. CommunityDragon cannot confirm these;")
        print("read them off the champion card or the patch notes, then set")
        print("read_on in patch_pin.json:")
        for key in report.unverified:
            print(f"  {key}")
        print()

    if args.coverage:
        print(f"unbacked ({len(report.unbacked)}) -- no reference value exists:")
        for line in report.unbacked:
            print(f"  {line}")
        missing_traits, no_card = coverage(data, pin)
        if missing_traits:
            print(f"\ntraits with no hook at all: {', '.join(missing_traits)}")
        if no_card:
            print(f"\nchampions with no card_values recorded: {', '.join(no_card)}")

    return 1 if report.drift or report.broken else 0


if __name__ == "__main__":
    sys.exit(main())
