"""Set 19 items. Each is written from the selected build (its stats effect, tags and curve rows), one at a time like
the champions; a class is live only when listed in one of the registries below. Status and evidence per item:
docs/ITEMS.md (decision D6).
"""
from buildstore import BuildDataError, load_build
from item import Item
from timing import ticks_up

offensive_craftables = ["ArchangelsStaff", "BlueBuff", "Deathblade", "GuinsoosRageblade", "InfinityEdge",
                        "JeweledGauntlet", "Quicksilver", "RabadonsDeathcap", "SpearOfShojin", "TitansResolve"]
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
    ("AttackDamage", "MultiplyAdditive"): _bonus_multiplier("bonus_ad"),
    ("AbilityPower", "MultiplyAdditive"): _bonus_multiplier("ap"),
}
BONUS_MULTIPLIERS = {"AttackDamage", "AbilityPower"}  # their MultiplyAdditive comes with base-cancelling AddFinals
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
        finals = {}  # attribute -> sum of its AddFinal terms (consumed by a bonus multiplier below)
        for m in e["modifiers"]:
            if m["op"] == "AddFinal" and m["attribute"] in BONUS_MULTIPLIERS and len(set(m["values"])) == 1:
                finals[m["attribute"]] = finals.get(m["attribute"], 0) + m["values"][0]
        final_attrs = set(finals)
        for m in e["modifiers"]:
            key = (m["attribute"], m["op"])
            if m["attribute"] in NO_EFFECT_ON_DUMMIES or (m["op"] == "AddFinal" and m["attribute"] in final_attrs):
                continue
            if m.get("scale") is not None or len(set(m["values"])) != 1:
                raise BuildDataError(f"item {entry.key}: {m['attribute']} {m['op']} {m['text']} is not a plain value")
            if m.get("channel", ITEM_CHANNEL) != ITEM_CHANNEL:
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


def _name(key):
    return load_build().item(key).name  # the newest build's display name


class Deathblade(BuildItem):
    """55% AD; every bonus AD x1.15 (GE_Deathblade on Channel1: MultiplyAdditive ADMultiplier with AddFinal -1.15 + 1,
    I5). Two Deathblades: x1.30. No script."""
    KEY = "DA_Deathblade"
    STATS = ("GE_Deathblade",)
    display_name = _name(KEY)


class RabadonsDeathcap(BuildItem):
    """55% AP; every bonus AP x1.15 (as Deathblade, GE_RabadonsDeathcap_Stats, I5). No script."""
    KEY = "DA_RabadonsDeathcap"
    STATS = ("GE_RabadonsDeathcap_Stats",)
    display_name = _name(KEY)


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


class GuinsoosRageblade(StackingItem):
    """Stats GE_GuinsoosRageblade_Base (10% AP, 10% AS). Script GA_GuinsoosRageblade: at activation (combat start)
    it applies GE_GuinsoosRageblade_StackingAS (AttackSpeed MultiplyAdditive 0.01 x Stack) and starts a looping
    1-second timer (0x1b9: K2_SetTimerDelegate(Stack, 1, true)); each expiry in combat applies the ItemStackGE
    parameter, GE_GuinsoosRageblade_ItemStack (Stack + ASCounter = 7). So +7% AS per second, additive with other AS.
    VOD (items/GuinsoosRageblade.md E1, Varus): first stack exactly 1.000 s after combat start, then every second,
    AS = base x (1.10 + 0.07n)."""
    KEY = "DA_GuinsoosRageblade"
    STATS = ("GE_GuinsoosRageblade_Base",)
    PERIOD_SECONDS = 1.0  # script literal (0x1b9)
    display_name = _name(KEY)

    def per_stack(self, champion):
        stack, _ = self.script_modifier(champion, "GE_GuinsoosRageblade_ItemStack", "Stack", "+")
        coef, scale = self.script_modifier(champion, "GE_GuinsoosRageblade_StackingAS", "AttackSpeed", "MultiplyAdditive")
        if scale != "Stack":
            raise BuildDataError(f"{self.KEY}: StackingAS no longer scales with Stack ({scale})")
        champion.aspd.addStat(coef * stack * 100)


class Quicksilver(StackingItem):
    """Stats GE_Quicksilver_Stats (15% AS, 20% crit, 20 MR). Script GA_Quicksilver: WaitOnTimePassedInPhase(
    StackFrequency, combat) then RepeatAction(StackFrequency, 99) (0x343), whose first action is immediate; each
    action applies QuicksilverStackingEffect = GE_Quicksilver_StacksToAttackSpeed (AttackSpeed MultiplyAdditive 1.03).
    So +3% AS at 1, 2, 3, ... s, up to 99 times; EffectDuration (18 s) is only the Unstoppable (nothing against
    dummies). VOD4 Senna (docs/ITEMS.md): with Guinsoo's, one +0.075 AS step every 60 frames from 1 s."""
    KEY = "DA_Quicksilver"
    STATS = ("GE_Quicksilver_Stats",)
    MAX_ACTIONS = 99  # RepeatAction's count (script literal, 0x343)
    display_name = _name(KEY)

    def period_seconds(self, champion):
        ref = next(r for r in self.build_entry(champion).d["ability_refs"] if r["ga"] == "GA_Quicksilver")
        return self.row(champion, ref["params"]["FrequencyCurveTable"]["RowName"])

    def per_stack(self, champion):
        if self.next_k > self.MAX_ACTIONS:
            return
        v, scale = self.script_modifier(champion, "GE_Quicksilver_StacksToAttackSpeed", "AttackSpeed",
                                        "MultiplyAdditive")
        if scale is not None:
            raise BuildDataError(f"{self.KEY}: StacksToAttackSpeed is no longer a plain number ({scale})")
        champion.aspd.addStat((v - 1) * 100)


class TitansResolve(BuildItem):
    """Stats GE_TitansResolve_Stats (10% AS, 20 armor). Script GA_TitansResolve: at activation it applies
    StackingStatsGE = GE_TitansResolve_StackingStats (AttackDamage and AbilityPower + 0.02 x Stack); every
    Combat.Event.LaunchAttack of the holder (WaitGameplayEvent, not exact: simulated attacks count, 0x63f) and every
    attack or spell damage taken (nothing, against dummies) applies GE_TitansResolve_Stack (one stack) while Stack <
    MaxStacks (25). Full stacks: 15% max HP and Unstoppable (nothing against dummies). VOD4 Ezreal
    (docs/ITEMS.md): +2% AP on every release's frame and twice per cast (his two simulated attacks)."""
    KEY = "DA_TitansResolve"
    STATS = ("GE_TitansResolve_Stats",)
    display_name = _name(KEY)

    def __init__(self):
        super().__init__(phases=["preCombat", "onLaunch"])
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.stacks = 0
        elif phase == "onLaunch" and self.stacks < self.row(champion, "MaxStacks"):
            self.stacks += 1
            for attr, stat in (("AttackDamage", champion.bonus_ad), ("AbilityPower", champion.ap)):
                coef, scale = self.script_modifier(champion, "GE_TitansResolve_StackingStats", attr, "+")
                if scale != "Stack":
                    raise BuildDataError(f"{self.KEY}: StackingStats {attr} no longer scales with Stack ({scale})")
                stat.addStat(coef * 100)  # one stack
        return input_


class ArchangelsStaff(StackingItem):
    """Stats GE_ArchangelsStaff_Stats (30% AP, 1 mana regen). Script GA_ArchangelsStaff_RampingStats: at time 0 of
    phase 9 (combat; Blue Buff's script tests the same phase at combat start) it applies GE_ArchangelsStaff_StackToAP
    (AbilityPower + 0.01 x Stack) and starts a looping timer whose period is the FrequencyCurveRow parameter (row
    Period = 5 s); each expiry in combat applies RampingStatGE = GE_ArchangelsStaff_RampingStats (Stack + APStack =
    20). So +20 AP every 5 s from combat start. No VOD yet (predicted; set18: the same, a tick later)."""
    KEY = "DA_ArchangelsStaff"
    STATS = ("GE_ArchangelsStaff_Stats",)
    display_name = _name(KEY)

    def period_seconds(self, champion):
        ref = next(r for r in self.build_entry(champion).d["ability_refs"] if r["ga"] == "GA_ArchangelsStaff_RampingStats")
        return self.row(champion, ref["params"]["FrequencyCurveRow"]["RowName"])

    def per_stack(self, champion):
        stack, _ = self.script_modifier(champion, "GE_ArchangelsStaff_RampingStats", "Stack", "+")
        coef, scale = self.script_modifier(champion, "GE_ArchangelsStaff_StackToAP", "AbilityPower", "+")
        if scale != "Stack":
            raise BuildDataError(f"{self.KEY}: StackToAP no longer scales with Stack ({scale})")
        champion.ap.addStat(coef * stack * 100)


class BlueBuff(BuildItem):
    """Stats GE_BlueBuff_Stats (6 mana regen, 15% AP, 15% AD). Script GA_BlueBuff: on activation, if the round's
    elapsed time is under 0.01 s in phase 9 (combat start), apply CombatStartManaGain = GE_BlueBuff_StartingMana
    (mana + StartingMana = 10, item source, AlwaysBank). preCombat, as set18's Blue Buff. VOD (items/BlueBuff.md E1,
    Varus): the panel's mana goes 30 -> 40 on the combat-start frame."""
    KEY = "DA_BlueBuff"
    STATS = ("GE_BlueBuff_Stats",)
    display_name = _name(KEY)

    def __init__(self):
        super().__init__(phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.addMana(self.script_mana(champion, "GE_BlueBuff_StartingMana"))
        return input_
