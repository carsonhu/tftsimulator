"""Set 19 items. Each is written from the selected build (its stats effect, tags and curve rows), one at a time like
the champions; a class is live only when listed in one of the registries below. Status and evidence per item:
docs/ITEMS.md (decision D6).
"""
from buildstore import BuildDataError, load_build
from item import Item

offensive_craftables = ["InfinityEdge", "JeweledGauntlet", "SpearOfShojin"]
artifacts = []
radiants = []
emblems = []
animas = []
no_item = ["NoItem"]


class NoItem(Item):
    """The baseline row every table's ratios are read against."""
    display_name = "NoItem"

    def __init__(self):
        super().__init__(self.display_name, phases=None)


# ---------------------------------------------------------------- the stats layer (ledger I1-I3)
def _hp_multiplier(c, v):
    c.hp.mult += v - 1  # MultiplyAdditive: (1 + sum of (v - 1)) on max health


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
}
# attributes that change nothing against training dummies (they never attack, heal or shield) (I1)
NO_EFFECT_ON_DUMMIES = {"IncomingDamageMultiplier", "IncomingHealMultiplier", "IncomingShieldMultiplier",
                        "MaxTeamSizeBonus"}
# tags an item's effect grants that the engine models (I2)
TAG_MAP = {"Damage.Status.CanSpellCrit": lambda c: c.addPrecision()}


def item_stats(entry, effects):
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
        for m in e["modifiers"]:
            key = (m["attribute"], m["op"])
            if m["attribute"] in NO_EFFECT_ON_DUMMIES:
                continue
            if m.get("scale") is not None or len(set(m["values"])) != 1:
                raise BuildDataError(f"item {entry.key}: {m['attribute']} {m['op']} {m['text']} is not a plain value")
            if key not in STAT_MAP:
                raise BuildDataError(f"item {entry.key}: no stat mapping for {key} (ledger I1)")
            mods.append((m["attribute"], m["op"], m["values"][0], m.get("row")))
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

    def __init__(self, phases=()):
        super().__init__(self.display_name, phases=list(phases) or None)

    def performAbility(self, phase, time, champion, input_=0):
        return input_  # stats only; subclasses with mechanics override this for their phases

    def build_entry(self, champion):
        return (getattr(champion, "build", None) or load_build()).item(self.KEY)

    def applyStats(self, champion):
        mods, tags = item_stats(self.build_entry(champion), self.STATS)
        for attr, op, value, _ in mods:
            STAT_MAP[(attr, op)](champion, value)
        for t in tags:
            TAG_MAP[t](champion)


def _name(key):
    return load_build().item(key).name  # the newest build's display name


class InfinityEdge(BuildItem):
    """35% AD, 35% crit chance, Precision (GE_InfinityEdge grants Damage.Status.CanSpellCrit). No script."""
    KEY = "DA_InfinityEdge"
    STATS = ("GE_InfinityEdge",)
    display_name = _name(KEY)


class JeweledGauntlet(BuildItem):
    """35% AP, 35% crit chance, Precision (GE_JeweledGauntlet grants Damage.Status.CanSpellCrit). No script."""
    KEY = "DA_JeweledGauntlet"
    STATS = ("GE_JeweledGauntlet",)
    display_name = _name(KEY)


class SpearOfShojin(BuildItem):
    """15% AD, 15% AP, 1 mana regen; "Attacks grant 5 bonus Mana" is the ManaPerAttack attribute in the same effect,
    so it is paid with the role's attack mana (I3). No script."""
    KEY = "DA_SpearOfShojin"
    STATS = ("GE_SpearOfShojin",)
    display_name = _name(KEY)
