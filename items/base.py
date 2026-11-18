"""The item base classes: NoItem (the baseline row), the stats layer and BuildItem (ledger I1-I3, I5), StackingItem
(a combat-start timer, I4) and item_name."""
from buildstore import BuildDataError, load_build
from champion import Champion
from item import Item
from stats import OPS
from timing import ticks_up


class NoItem(Item):
    """The baseline row every table's ratios are read against."""
    display_name = "NoItem"

    def __init__(self):
        super().__init__(self.display_name, phases=None)


# ---------------------------------------------------------------- the stats layer (ledger I1-I3, I5)
# An item's stats effects are applied as the build lists them: each modifier's attribute, op and channel go to the
# holder's Attribute (stats.Attribute evaluates the game's formula), in game units, with no conversion.

# attributes that change nothing against training dummies (they never attack, heal or shield) (I1)
NO_EFFECT_ON_DUMMIES = {"IncomingDamageMultiplier", "IncomingHealMultiplier", "IncomingShieldMultiplier",
                        "MaxTeamSizeBonus"}
# OutgoingDamageMultiplier MultiplyAdditive (Rapid Firecannon's x1.05, the only amp in the build not written as +)
# joins the damage-amp pool additively: damage amp is additive by default (owner, 2026-11-17; I1). The stock
# formula would multiply the pool instead; open until a clip shows otherwise
# (docs/OPEN-QUESTIONS.md), so the restructure changes no number.
ADDITIVE_AMP = ("OutgoingDamageMultiplier", "MultiplyAdditive")
# tags an item's effect grants that the engine models (I2)
TAG_MAP = {"Damage.Status.CanSpellCrit": lambda c: c.addPrecision(),
           "ItemTags.Hullcrusher.Equipped": lambda c: None}  # a marker the item's own script reads


def item_stats(entry, effects, skip=()):
    """The plain stat modifiers and tags of an item's `effects` (effect names) in a build entry:
    ([(attribute, op, value, row, channel)], [tags]). Raises BuildDataError for anything the stats layer can't apply
    exactly: a magnitude computed in game, a value that differs per curve point, an attribute the engine doesn't
    have, an unknown op or tag."""
    by_name = {e["effect"]: e for e in entry.d.get("effects") or []}
    mods, tags = [], []
    for name in effects:
        e = by_name.get(name)
        if e is None:
            raise BuildDataError(f"item {entry.key} has no effect {name!r} in build {entry.build.version}")
        if e["duration"] != "Infinite":
            raise BuildDataError(f"item {entry.key}: effect {name} is {e['duration']}, not a permanent stat")
        for m in e["modifiers"]:
            attr, op = m["attribute"], m["op"]
            if attr in NO_EFFECT_ON_DUMMIES:
                continue
            if (attr, op, m.get("scale")) in skip:  # the item class says why this modifier is handled there
                continue
            if m.get("scale") is not None or len(set(m["values"])) != 1:
                raise BuildDataError(f"item {entry.key}: {attr} {op} {m['text']} is not a plain value")
            if attr not in Champion.ATTRIBUTES:
                raise BuildDataError(f"item {entry.key}: the engine has no attribute {attr} (ledger I1)")
            if op not in OPS:
                raise BuildDataError(f"item {entry.key}: {attr} has an unknown op {op!r}")
            mods.append((attr, op, m["values"][0], m.get("row"), m.get("channel", 1)))
        for t in e.get("granted_tags") or []:
            if t not in TAG_MAP:
                raise BuildDataError(f"item {entry.key}: effect {name} grants {t}, which the engine doesn't model")
            tags.append(t)
    return mods, tags


def apply_modifier(champion, attr, op, value, channel=1):
    """One build modifier onto the holder's attribute."""
    if (attr, op) == ADDITIVE_AMP:
        champion.dmgMultiplier.modify("+", value - 1, channel)
    else:
        champion.attribute(attr).modify(op, value, channel)


class BuildItem(Item):
    """An item whose stats come from the selected build (ledger I1-I3).

    STATS names the item's effects that are its unconditional stats, as reviewed in docs/ITEMS.md (an item's other
    effects, such as a conditional buff or one that grants an ability, are its mechanic and are written in the
    class). They are read from the champion's own build and applied in the static-stats pass (Item.applyStats),
    before any combat phase, so prePreCombat stays free for flags that items read later.
    """
    KEY = None
    STATS = ()
    SKIP = ()  # (attribute, op, scale) of stats modifiers the class handles itself; its docstring says why

    def __init__(self, phases=()):
        super().__init__(self.display_name, phases=list(phases) or None)

    def performAbility(self, phase, time, champion, input_=0):
        return input_  # stats only; subclasses with mechanics override this for their phases

    def build_entry(self, champion):
        return (getattr(champion, "build", None) or load_build()).item(self.KEY)

    def applyStats(self, champion):
        mods, tags = item_stats(self.build_entry(champion), self.STATS, self.SKIP)
        for attr, op, value, _, channel in mods:
            apply_modifier(champion, attr, op, value, channel)
        for t in tags:
            TAG_MAP[t](champion)

    def stack_modifier(self, champion, attr, op, value):
        """The item's effect whose size follows a Stack count, re-applied at the current total: one modifier per item
        and attribute (keyed), as the game re-evaluates one effect when Stack changes."""
        champion.attribute(attr).modify(op, value, key=f"{self.KEY} {id(self)} {attr}")

    # ------------------------------------------------------------ what an item's script applies (P8, script_effects)
    def script_modifier(self, champion, effect, attribute, op):
        """The single modifier of `attribute` with `op` in an effect the item's script applies: (values[0], scale).
        scale None = a plain number; 'Stack' etc. = coefficient x that attribute."""
        entry = self.build_entry(champion)
        ge = (entry.d.get("script_effects") or {}).get(effect)
        if ge is None:
            raise BuildDataError(f"item {self.KEY}: no script effect {effect!r} in build {entry.build.version}")
        ms = [m for m in ge["modifiers"] if m["attribute"] == attribute and m["op"] == op]
        if len(ms) != 1 or len(set(ms[0]["values"])) != 1:
            raise BuildDataError(f"item {self.KEY}: {effect} has no single {attribute} {op} modifier")
        return ms[0]["values"][0], ms[0].get("scale")

    def script_rule(self, champion, effect, attribute):
        """(op, channel) of the single `attribute` modifier in an effect the item's script applies (its value may
        come from elsewhere, e.g. a debuff level)."""
        ge = (self.build_entry(champion).d.get("script_effects") or {}).get(effect)
        ms = [m for m in (ge or {}).get("modifiers") or [] if m["attribute"] == attribute]
        if len(ms) != 1:
            raise BuildDataError(f"item {self.KEY}: {effect} has no single {attribute} modifier")
        return ms[0]["op"], ms[0].get("channel", 1)

    def script_mana(self, champion, effect):
        """The mana an effect the item's script applies gives (a plain number)."""
        entry = self.build_entry(champion)
        ge = (entry.d.get("script_effects") or {}).get(effect)
        terms = (ge or {}).get("mana") or []
        if len(terms) != 1 or terms[0].get("scale") is not None or len(set(terms[0]["values"])) != 1:
            raise BuildDataError(f"item {self.KEY}: {effect} has no single plain mana term in build {entry.build.version}")
        return terms[0]["values"][0]

    def ga_param(self, champion, ga, param):
        """A parameter the item gives its script: an effect name, or a curve row's name (`RowName`). A Radiant runs
        the same script with its own effects (GE_..._Radiant), so reading them here serves both."""
        ref = next((r for r in self.build_entry(champion).d.get("ability_refs") or [] if r["ga"] == ga), None)
        if ref is None or param not in (ref.get("params") or {}):
            raise BuildDataError(f"item {self.KEY}: no {ga} parameter {param!r}")
        v = ref["params"][param]
        return v["RowName"] if isinstance(v, dict) and "RowName" in v else v

    def row(self, champion, name):
        """The item's curve row (single point) from the champion's build."""
        pts = self.build_entry(champion).row(name)
        if len({v for _, v in pts}) != 1:
            raise BuildDataError(f"item {self.KEY}: row {name} differs per point")
        return pts[0][1]


class StackingItem(BuildItem):
    """An item whose script runs a looping timer from combat start and, on each expiry, adds to the item's Stack;
    another effect turns Stack into a stat (ledger I4). Timer expiries land on ticks_up(k x period) after combat
    start, in onUpdate (set18 used onUpdate with `time > k x period`, a tick later; O5)."""
    PERIOD_SECONDS = None  # a literal in the script (cite it), or None: read by period_seconds()

    def __init__(self):
        super().__init__(phases=["preCombat", "onUpdate"])
        self.next_k = 1

    def period_seconds(self, champion):
        return self.PERIOD_SECONDS

    def per_stack(self, champion):
        """Apply one timer expiry's stat gain to the champion."""
        raise NotImplementedError

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":  # the timer starts at combat start (I4)
            self.next_k = 1
        elif phase == "onUpdate":
            while champion.tick >= ticks_up(self.next_k * self.period_seconds(champion)):
                self.per_stack(champion)
                self.next_k += 1
        return input_


def item_name(key):
    return load_build().item(key).name  # the newest build's display name
