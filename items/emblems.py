"""Spatula items: the two components, the Tactician's items and the emblems whose effect is plain stats. They matter
to U.R.F. (augments/combat.py), which counts them on the holder (ledger A6); an emblem also adds its stats and puts
its trait in the buff bar (`trait`).

Emblems with more than stats are not listed until their mechanic is written (docs/ITEMS.md): Arcanist (execute),
Bodyguard (resist conversion), Choreographer (back-row AS), Frontman, Swiftstriker (on-hit scripts), Heartsteel and
Hitmaker (tags their traits read), Juggernaut (amp per health), Manager (max-mana row),
Renegade (empowered crits), Slayer (execute-style amp)."""
from buildstore import BuildDataError
from items.base import BuildItem, item_name
from registry import register

# GE_URF's magnitude, MMC_NumSpatulaItemsOnHolder (Set_Shared, CalculateBaseMagnitude): 2 x the holder's items with
# Item.Equippable.Item.Tacticians, plus 1 x its items with ANY(Item.Equippable.Item.Component.SpatOrPan,
# Item.Equippable.Item.Emblem). Gameplay tag matching includes child tags, so Emblem.Elusive counts.
TACTICIANS = "Item.Equippable.Item.Tacticians"
SPAT_OR_EMBLEM = ("Item.Equippable.Item.Component.SpatOrPan", "Item.Equippable.Item.Emblem")


def _has(tags, tag):
    return any(t == tag or t.startswith(tag + ".") for t in tags)


def spatula_count(champion):
    """MMC_NumSpatulaItemsOnHolder for the champion's items, read from each item's tags in the champion's build."""
    n = 0
    for item in champion.items:
        if not isinstance(item, BuildItem) or item.KEY is None:
            continue
        tags = item.build_entry(champion).d.get("tags") or []
        n += 2 * _has(tags, TACTICIANS) + any(_has(tags, t) for t in SPAT_OR_EMBLEM)
    return n


class SpatulaItem(BuildItem):
    """A component or Tactician's item: no stats a dummy fight can see (MaxTeamSizeBonus only, I1)."""


@register("emblem")
class Spatula(SpatulaItem):
    KEY = "DA_Component_Spatula"
    display_name = item_name(KEY)


@register("emblem")
class FryingPan(SpatulaItem):
    KEY = "DA_Component_FryingPan"
    display_name = item_name(KEY)


@register("emblem")
class TacticiansCrown(SpatulaItem):
    KEY = "DA_TacticiansCrown"
    STATS = ("GE_TacticiansCrown_Stats",)
    display_name = item_name(KEY)


@register("emblem")
class TacticiansCape(SpatulaItem):
    KEY = "DA_TacticiansCape"
    STATS = ("GE_TacticiansCape_Stats",)
    display_name = item_name(KEY)


@register("emblem")
class TacticiansShield(SpatulaItem):
    KEY = "DA_TacticiansShield"
    STATS = ("GE_TacticiansShield_Stats",)
    display_name = item_name(KEY)


class BuildEmblem(BuildItem):
    """An emblem's stats effect GE_<Trait>_Emblem. Its AttackSpeed modifier is 1 x AttackSpeedCalc1 (1 + EmblemAS):
    applied here as MultiplyAdditive 1 + EmblemAS, after checking the calc is that formula. The trait it adds is the
    buff bar's level (the page offers `trait`)."""
    SKIP = (("AttackSpeed", "MultiplyAdditive", "AttackSpeedCalc1"),)
    TRAIT = None

    def __init__(self):
        super().__init__()
        self.trait = self.TRAIT

    def applyStats(self, champion):
        super().applyStats(champion)
        entry = self.build_entry(champion)
        as_ = self.row(champion, "EmblemAS") if "EmblemAS" in entry.rows() else 0
        calc = (entry.d.get("calcs") or {}).get("AttackSpeedCalc1")
        try:
            one, plus = (float(x) for x in calc.split(" + "))
        except (AttributeError, ValueError):
            raise BuildDataError(f"item {self.KEY}: AttackSpeedCalc1 {calc!r} is not '1 + EmblemAS'")
        if one != 1 or abs(plus - as_) > 1e-9:
            raise BuildDataError(f"item {self.KEY}: AttackSpeedCalc1 {calc!r} is not 1 + EmblemAS ({as_})")
        if as_:
            champion.aspd.modify("MultiplyAdditive", 1 + as_)


def _emblem(name, key, effect, trait):
    cls = type(name, (BuildEmblem,), {"KEY": key, "STATS": (effect,), "TRAIT": trait,
                                      "display_name": item_name(key), "__module__": __name__,
                                      "__doc__": f"{item_name(key)}: stats {effect} only."})
    globals()[name] = register("emblem")(cls)


# (class, key, stats effect, trait class in set19buffs or None when the trait isn't simulated)
for _row in [
    ("KDAEmblem", "DA_KDA19_Emblem", "GE_KDA19_Emblem", "KDA"),  # GE_KDA19_StarLevelContribution: trait side
    ("IllbeatsEmblem", "DA_IllBeats19_Emblem", "GE_IllBeats19_Emblem", "Illbeats"),
    ("IonicSparkEmblem", "DA_IonicSpark19_Emblem", "GE_IonicSpark19_Emblem", "IonicSpark"),
    ("RockEmblem", "DA_DemonVision19_Emblem", "GE_DemonVision19_Emblem", None),
    ("BeachPopEmblem", "DA_Oceansong19_Emblem", "GE_Oceansong19_Emblem", "BeachPop"),
    ("PentakillEmblem", "DA_Pentakill19_Emblem", "GE_Pentakill19_Emblem", "Pentakill"),
    ("JazzEmblem", "DA_Jazz19_Emblem", "GE_Jazz19_Emblem", "Jazz"),
    ("TrueDamageEmblem", "DA_TrueDamage19_Emblem", "GE_TrueDamage19_Emblem", "TrueDamage"),
    ("ClassicalEmblem", "DA_Virtuosos19_Emblem", "GE_Virtuosos19_Emblem", "Classical"),
    ("HyperpopEmblem", "DA_GlitterBomb19_Emblem", "GE_GlitterBomb19_Emblem", "Hyperpop"),
    # 150 Health, 1 Mana Regen; its on-cast max Health (1% per 10 Mana spent; owner, VOD7) deals no damage
    ("ProdigyEmblem", "DA_Prodigy19_Emblem", "GE_Prodigy19_Emblem", "Prodigy"),
]:
    _emblem(*_row)
del _row
