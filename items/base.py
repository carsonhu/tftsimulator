"""The item base classes: NoItem (the baseline row), the stats layer and BuildItem (ledger I1-I3), StackingItem
(a combat-start timer, I4) and item_name."""
from buildstore import BuildDataError, load_build
from item import Item
from timing import ticks_up


class NoItem(Item):
    """The baseline row every table's ratios are read against."""
    display_name = "NoItem"

    def __init__(self):
        super().__init__(self.display_name, phases=None)


# ---------------------------------------------------------------- the stats layer (ledger I1-I3)
def _hp_multiplier(c, v):
    c.hp.mult += v - 1  # MultiplyAdditive: (1 + sum of (v - 1)) on max health


def _bonus_multiplier(stat):
    """MultiplyAdditive on AD or AP in the item channel (I5): Channel1 = ((1 + bonuses) x (1 + sum of (v - 1))) +
    AddFinal, where the effect's AddFinal terms cancel the x on the base 1 (checked in item_stats), so the effect
    multiplies every bonus on the channel: the engine's addMultiplier (AD = base x (1 + addMultiplier x bonus))."""
    def apply(c, v):
        getattr(c, stat).addMultiplier += v - 1
    return apply


# the channel the stats layer models: items, traits and roles add to Channel1; Channel0 is the unit's base and
# Channel2 applies after them (Last Whisper's armor x, Void Staff, healing cuts) (I5)
ITEM_CHANNEL = 1


# (attribute, operation) -> where a plain stat modifier lands in the engine (I1). Engine units: AD, AP and AS are
# percent points; crit chance, omnivamp and damage amp are fractions; HP, armor, MR and mana are flat.
STAT_MAP = {
    ("AbilityPower", "+"): lambda c, v: c.ap.addStat(v * 100),
    ("AttackDamage", "+"): lambda c, v: c.bonus_ad.addStat(v * 100),
    ("AttackSpeed", "MultiplyAdditive"): lambda c, v: c.aspd.addStat((v - 1) * 100),
    ("CritChance", "+"): lambda c, v: c.crit.addStat(v),
    ("HealthMax", "+"): lambda c, v: c.hp.addStat(v),
    ("HealthMax", "MultiplyAdditive"): _hp_multiplier,
    ("Armor", "+"): lambda c, v: c.armor.addStat(v),
    ("MagicResist", "+"): lambda c, v: c.mr.addStat(v),
    ("ManaPerSecond", "+"): lambda c, v: c.manaRegen.addStat(v),
    ("ManaPerAttack", "+"): lambda c, v: c.manaPerAttack.addStat(v),
    ("Omnivamp", "+"): lambda c, v: c.omnivamp.addStat(v),
    ("OutgoingDamageMultiplier", "+"): lambda c, v: c.dmgMultiplier.addStat(v),
    ("IncomingManaMultiplier", "+"): lambda c, v: c.manaGainMultiplier.addStat(v),
    ("OutgoingDamageMultiplier", "MultiplyAdditive"): lambda c, v: c.dmgMultiplier.addStat(v - 1),
    # item range is kept apart: flights stay the unit's own range (owner, 2026-11-17: Rapid Firecannon doesn't change them)
    ("AttackRange", "+"): lambda c, v: setattr(c, "bonus_range", getattr(c, "bonus_range", 0) + int(v)),
    ("AttackSpeed", "="): lambda c, v: setattr(c.aspd, "override", v),  # Silvermere Dawn's lock (I10)
    ("AttackDamage", "MultiplyAdditive"): _bonus_multiplier("bonus_ad"),
    ("AbilityPower", "MultiplyAdditive"): _bonus_multiplier("ap"),
}
# an Override on Channel2 (after every item and trait bonus on Channel1) is the attribute's final value (I10)
FINAL_OVERRIDES = {("AttackSpeed", "=")}
BONUS_MULTIPLIERS = {"AttackDamage", "AbilityPower"}  # their MultiplyAdditive comes with base-cancelling AddFinals
# attributes that change nothing against training dummies (they never attack, heal or shield) (I1)
NO_EFFECT_ON_DUMMIES = {"IncomingDamageMultiplier", "IncomingHealMultiplier", "IncomingShieldMultiplier",
                        "MaxTeamSizeBonus"}
# tags an item's effect grants that the engine models (I2)
TAG_MAP = {"Damage.Status.CanSpellCrit": lambda c: c.addPrecision(),
           "ItemTags.Hullcrusher.Equipped": lambda c: None}  # a marker the item's own script reads


def item_stats(entry, effects, skip=()):
    """The plain stat modifiers and tags of an item's `effects` (effect names) in a build entry:
    ([(attribute, op, value, row)], [tags]). Raises BuildDataError for anything the stats layer can't apply exactly:
    a magnitude computed in game, a value that differs per curve point, an unknown (attribute, op) or tag."""
    by_name = {e["effect"]: e for e in entry.d.get("effects") or []}
    mods, tags = [], []
    for name in effects:
        e = by_name.get(name)
        if e is None:
            raise BuildDataError(f"item {entry.key} has no effect {name!r} in build {entry.build.version}")
        if e["duration"] != "Infinite":
            raise BuildDataError(f"item {entry.key}: effect {name} is {e['duration']}, not a permanent stat")
        finals = {}  # attribute -> sum of its AddFinal terms (consumed by a bonus multiplier below)
        for m in e["modifiers"]:
            if m["op"] == "AddFinal" and m["attribute"] in BONUS_MULTIPLIERS and len(set(m["values"])) == 1:
                finals[m["attribute"]] = finals.get(m["attribute"], 0) + m["values"][0]
        final_attrs = set(finals)
        for m in e["modifiers"]:
            key = (m["attribute"], m["op"])
            if m["attribute"] in NO_EFFECT_ON_DUMMIES or (m["op"] == "AddFinal" and m["attribute"] in final_attrs):
                continue
            if key + (m.get("scale"),) in skip:  # the item class says why this modifier is handled there
                continue
            if m.get("scale") is not None or len(set(m["values"])) != 1:
                raise BuildDataError(f"item {entry.key}: {m['attribute']} {m['op']} {m['text']} is not a plain value")
            if m.get("channel", ITEM_CHANNEL) != ITEM_CHANNEL and not (key in FINAL_OVERRIDES and m.get("channel") == 2):
                raise BuildDataError(f"item {entry.key}: {m['attribute']} {m['op']} is on channel {m['channel']}, "
                                     f"not the item channel {ITEM_CHANNEL} (I5)")
            if key[1] == "MultiplyAdditive" and key[0] in BONUS_MULTIPLIERS:
                # the base 1 is multiplied too: the effect's AddFinals must take back exactly 1 x (v - 1)
                if abs(finals.pop(key[0], 0) - (1 - m["values"][0])) > 1e-9:
                    raise BuildDataError(f"item {entry.key}: {key[0]} x{m['values'][0]} without AddFinal terms that "
                                         f"cancel it on the base (I5)")
            if key not in STAT_MAP:
                raise BuildDataError(f"item {entry.key}: no stat mapping for {key} (ledger I1)")
            mods.append((m["attribute"], m["op"], m["values"][0], m.get("row")))
        if finals:
            raise BuildDataError(f"item {entry.key}: AddFinal on {sorted(finals)} with no multiplier to cancel (I5)")
        for t in e.get("granted_tags") or []:
            if t not in TAG_MAP:
                raise BuildDataError(f"item {entry.key}: effect {name} grants {t}, which the engine doesn't model")
            tags.append(t)
    return mods, tags


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
        for attr, op, value, _ in mods:
            STAT_MAP[(attr, op)](champion, value)
        for t in tags:
            TAG_MAP[t](champion)

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
