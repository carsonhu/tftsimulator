"""Set 19 items. Each is written from the selected build (its stats effect, tags and curve rows), one at a time like
the champions; a class is live only when listed in one of the registries below. Status and evidence per item:
docs/ITEMS.md (decision D6).
"""
import status
from buildstore import BuildDataError, load_build
from item import Item
from timing import TPS, ticks_up

# the DPS item table: offensive craftables only (owner, 2026-11-17: tank items such as Warmog's are not part of it)
offensive_craftables = ["AdaptiveHelm", "ArchangelsStaff", "Bloodthirster", "BlueBuff", "Deathblade", "EdgeOfNight",
                        "GiantSlayer", "GiantSlayerNoTank", "GuinsoosRageblade", "HandOfJustice", "HextechGunblade",
                        "InfinityEdge", "JeweledGauntlet", "KrakensFury", "LastWhisper", "Morellonomicon",
                        "NashorsTooth", "Quicksilver", "RabadonsDeathcap", "RedBuff", "SpearOfShojin", "SteraksGage",
                        "StrikersFlail", "TitansResolve", "VoidStaff"]
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


# ---------------------------------------------------------------- items whose scripts do nothing against dummies
class Bloodthirster(BuildItem):
    """Stats GE_Bloodthirster_Stats (15% AD, 15% AP, 20 MR, 20% omnivamp). Script GA_Bloodthirster: a shield and more
    omnivamp at 60% health, which training dummies never cause (they never attack, G9)."""
    KEY = "DA_Bloodthirster"
    STATS = ("GE_Bloodthirster_Stats",)
    display_name = _name(KEY)


class EdgeOfNight(BuildItem):
    """Stats GE_EdgeOfNight_Stats (10% AD, 10% AP, 15% AS, 20 armor). Script GA_EdgeOfNight: untargetable and a heal
    at 40% health, which dummies never cause (G9)."""
    KEY = "DA_EdgeOfNight"
    STATS = ("GE_EdgeOfNight_Stats",)
    display_name = _name(KEY)


class SteraksGage(BuildItem):
    """Stats GE_SteraksGage_Stats (45% AD, 300 HP). Script GA_SteraksGage: a shield at 40% health, which dummies never
    cause (G9)."""
    KEY = "DA_SteraksGage"
    STATS = ("GE_SteraksGage_Stats",)
    display_name = _name(KEY)


class HextechGunblade(BuildItem):
    """Stats GE_HextechGunblade_Stats (20% AD, 20% AP, 15% omnivamp, 1 mana regen). Script GA_HextechGunblade: heals the
    lowest-health ally for 20% of damage dealt, nothing against dummies."""
    KEY = "DA_HextechGunblade"
    STATS = ("GE_HextechGunblade_Stats",)
    display_name = _name(KEY)


class HandOfJustice(BuildItem):
    """Stats GE_HandOfJustice_Stats (20% crit, 1 mana regen). Script GA_HandOfJustice: on activation ApplyEffect
    applies AboveThresholdGE = GE_HandOfJustice_HighHealthEffect (36% AD, 36% AP, 12% omnivamp) while health is above
    HealthThreshold (50%) and swaps to the low-health effect below it (WaitForAttributeChangeRatioThreshold). Dummies
    never hit back (G9), so the high-health effect holds all fight."""
    KEY = "DA_HandOfJustice"
    STATS = ("GE_HandOfJustice_Stats",)
    display_name = _name(KEY)

    def applyStats(self, champion):
        super().applyStats(champion)
        for attr, stat in (("AttackDamage", champion.bonus_ad), ("AbilityPower", champion.ap)):
            v, scale = self.script_modifier(champion, "GE_HandOfJustice_HighHealthEffect", attr, "+")
            if scale is not None:
                raise BuildDataError(f"{self.KEY}: HighHealthEffect {attr} is not a plain number ({scale})")
            stat.addStat(v * 100)


class AdaptiveHelm(BuildItem):
    """Stats GE_AdaptiveHelm_Stats (20 MR, 3 mana regen, +15% mana from all sources). Script GA_AdaptiveHelm (0x3d5):
    a holder whose role tags include Tank or Fighter gets GE_AdaptiveHelm_TankFighter (armor and MR, nothing against
    dummies); any other role gets GE_AdaptiveHelm_OtherRoles (10% AD, 10% AP)."""
    KEY = "DA_AdaptiveHelm"
    STATS = ("GE_AdaptiveHelm_Stats",)
    display_name = _name(KEY)

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.role.archetype in ("Tank", "Fighter"):
            return
        for attr, stat in (("AttackDamage", champion.bonus_ad), ("AbilityPower", champion.ap)):
            v, scale = self.script_modifier(champion, "GE_AdaptiveHelm_OtherRoles", attr, "+")
            if scale is not None:
                raise BuildDataError(f"{self.KEY}: OtherRoles {attr} is not a plain number ({scale})")
            stat.addStat(v * 100)


class GiantSlayer(BuildItem):
    """Stats GE_GiantSlayer_Stats (15% AD, 15% AP, 15% AS, 15% damage amp). Script GA_GiantSlayer: before each damage
    the holder deals as a unit (WaitForDealDamage, Damage.Source.Unit), a target with Role.Tank (0x310) gives
    GE_GiantSlayer_ConditionalAmp (+AmpRatioAgainstTanks, 15%) for that damage, removed after it. Whether the dummies
    are Tanks is the choice between this entry (they are) and GiantSlayerNoTank (set18's two entries)."""
    KEY = "DA_GiantSlayer"
    STATS = ("GE_GiantSlayer_Stats",)
    display_name = _name(KEY) + " (vs Tank)"
    VS_TANK = True

    def applyStats(self, champion):
        super().applyStats(champion)
        if self.VS_TANK:
            v, scale = self.script_modifier(champion, "GE_GiantSlayer_ConditionalAmp", "OutgoingDamageMultiplier", "+")
            if scale is not None:
                raise BuildDataError(f"{self.KEY}: ConditionalAmp is not a plain number ({scale})")
            champion.dmgMultiplier.addStat(v)


class GiantSlayerNoTank(GiantSlayer):
    """Giant Slayer against targets that are not Tanks: its stats only."""
    display_name = _name(GiantSlayer.KEY) + " (vs non-Tank)"
    VS_TANK = False


# ---------------------------------------------------------------- on-attack and on-crit items
class KrakensFury(BuildItem):
    """Stats GE_KrakensFury_Stats (10% AD, 10% AS, 20 MR). Script GA_KrakensFury: every Combat.Event.LaunchAttack of
    the holder (WaitGameplayEvent, not exact: simulated attacks count, G11, as Titan's Resolve) while Stack <
    MaxStacks (15) applies ItemStackGE = GE_KrakensFury_ItemStack (Stack2 + ADCounter 3.5) and
    GE_KrakensFury_ItemStackCounter (Stack + 1); GE_KrakensFury_StackingAD gives AttackDamage + 0.01 x Stack2 (3.5% per
    stack). When Stack reaches MaxStacks (WaitForAttributeChanged) it applies BonusAS = GE_KrakensFury_BonusAS:
    AttackSpeed MultiplyAdditive by row Bonus_AS (15%)."""
    KEY = "DA_KrakensFury"
    STATS = ("GE_KrakensFury_Stats",)
    display_name = _name(KEY)

    def __init__(self):
        super().__init__(phases=["preCombat", "onLaunch"])
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.stacks = 0
        elif phase == "onLaunch" and self.stacks < self.row(champion, "MaxStacks"):
            self.stacks += 1
            stack2, _ = self.script_modifier(champion, "GE_KrakensFury_ItemStack", "Stack2", "+")
            coef, scale = self.script_modifier(champion, "GE_KrakensFury_StackingAD", "AttackDamage", "+")
            if scale != "Stack2":
                raise BuildDataError(f"{self.KEY}: StackingAD no longer scales with Stack2 ({scale})")
            champion.bonus_ad.addStat(coef * stack2 * 100)
            if self.stacks == self.row(champion, "MaxStacks"):
                champion.aspd.addStat(self.row(champion, "Bonus_AS") * 100)
        return input_


class NashorsTooth(BuildItem):
    """Stats GE_NashorsTooth_Stats (10% AS, 15% AP, 150 HP, 20% crit, ManaPerAttack 2: paid with the role's attack
    mana, I3). Script GA_NashorsTooth: every damage the holder deals with Damage.Result.WasCrit and
    Damage.Specifiers.AppliesOnHit.IsAttack (a critical attack) applies UpgradeHandler = GE_NashorsTooth_Mana
    (+ManaPerAttack_BonusOnCrit 2, BankIfOverflow) when it lands. The engine averages crits: its onCrit phase fires
    each time the accumulated crit chance passes 1 (I6)."""
    KEY = "DA_NashorsTooth"
    STATS = ("GE_NashorsTooth_Stats",)
    display_name = _name(KEY)

    def __init__(self):
        super().__init__(phases=["onCrit"])

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onCrit" and not input_:  # input_: is it spell damage
            champion.addMana(self.script_mana(champion, "GE_NashorsTooth_Mana"))
        return input_


class StrikersFlail(BuildItem):
    """Stats GE_StrikersFlail_Stats (150 HP, 10% AS, 20% crit, 10% damage amp). Script GA_StrikersFlail: every damage
    the holder deals with Damage.Result.WasCrit (attacks and spells) applies BuffGE = GE_StrikersFlail_Buff
    (OutgoingDamageMultiplier + DABuff 5%, BuffDuration 5 s) after it (PostApply). The buff's
    TFTStackGameplayEffectInstancesEffectComponent keeps separate instances up to MaxStacks (4); the simulator renews
    the oldest when a 5th lands (set18's rule; I6). The engine averages crits (onCrit, I6)."""
    KEY = "DA_StrikersFlail"
    STATS = ("GE_StrikersFlail_Stats",)
    display_name = _name(KEY)

    def __init__(self):
        super().__init__(phases=["preCombat", "onCrit"])
        self.slot = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.slot = 0
        elif phase == "onCrit":
            amp, scale = self.script_modifier(champion, "GE_StrikersFlail_Buff", "OutgoingDamageMultiplier", "+")
            if scale is not None:
                raise BuildDataError(f"{self.KEY}: the buff is not a plain number ({scale})")
            champion.applyStatus(status.DmgAmpModifier(f"StrikersFlail {id(self)} {self.slot}"), self, time,
                                 self.row(champion, "BuffDuration"), amp)
            self.slot = (self.slot + 1) % int(self.row(champion, "MaxStacks"))
        return input_


# ---------------------------------------------------------------- debuffs on the damaged target (I7)
def debuff_value(champion, row, level):
    """A shared debuff's value at the level an item passes (MakeDebuffGameplayEffectSpecHandle): the build's
    globals.debuff_level_to_value row (CT_DebuffLevelToValue; ShredSunderChill 30 -> 0.7, BurnWound 1 -> 0.01)."""
    from build_champion import curve_at  # build_champion imports the item registries
    g = ((getattr(champion, "build", None) or load_build()).data.get("globals") or {}).get("debuff_level_to_value")
    if not g or row not in g:
        raise BuildDataError(f"the build has no globals.debuff_level_to_value.{row} (re-snapshot)")
    return curve_at(g[row]["points"], level, g[row]["interp"] or "Linear")


class DebuffItem(BuildItem):
    """An item whose script answers the holder's attack and spell damage (WaitForDealDamage, Damage.Source.Unit) by
    applying a debuff to the damaged unit after the damage (PostApply): the next hit is reduced, not that one.
    LEVEL_PARAM / DURATION_PARAM name the GA parameters whose curve rows give the level and duration."""
    GA = None
    LEVEL_PARAM = DURATION_PARAM = None

    def __init__(self, phases=("PostOnDealDamage",)):
        super().__init__(phases=phases)

    def param_row(self, champion, param):
        ref = next(r for r in self.build_entry(champion).d["ability_refs"] if r["ga"] == self.GA)
        return self.row(champion, ref["params"][param]["RowName"])

    def performAbility(self, phase, time, champion, input_=0):
        target = getattr(champion, "lastDamagedOpponent", None)
        if phase == "PostOnDealDamage" and target is not None and input_ and input_[0]:
            self.debuff(champion, target, time, self.param_row(champion, self.LEVEL_PARAM),
                        self.param_row(champion, self.DURATION_PARAM))
        return input_

    def debuff(self, champion, target, time, level, duration):
        raise NotImplementedError


class LastWhisper(DebuffItem):
    """Stats GE_LastWhisper_Stats (20% AS, 15% AD, 20% crit). Script GA_LastWhisper: after each damage the holder
    deals (0x4fe Damage.Source.Unit, 0x6f7 attacks) it applies GE_ArmorSunder at level SunderPercent (30) for
    SunderDuration (3 s): Armor MultiplyAdditive ShredSunderChill(30) = x0.7. Sunders don't stack (the engine keeps
    the strongest, status.ArmorReduction)."""
    KEY = "DA_LastWhisper"
    STATS = ("GE_LastWhisper_Stats",)
    GA = "GA_LastWhisper"
    LEVEL_PARAM, DURATION_PARAM = "SunderPercentCurve", "DurationCurve"
    display_name = _name(KEY)

    def debuff(self, champion, target, time, level, duration):
        target.applyStatus(status.ArmorReduction("Sunder"), champion, time, duration,
                           debuff_value(champion, "ShredSunderChill", level))


class VoidStaff(DebuffItem):
    """Stats GE_VoidStaff_Stats (35% AP, 15% AS, 1 mana regen). Script GA_VoidStaff: after each damage the holder
    deals (0x572 Damage.Source.Unit, 0x76b attacks) it applies GE_MRShred at level ShredPercent (30) for
    ShredDuration (5 s): MagicResist MultiplyAdditive ShredSunderChill(30) = x0.7, not stacking."""
    KEY = "DA_VoidStaff"
    STATS = ("GE_VoidStaff_Stats",)
    GA = "GA_VoidStaff"
    LEVEL_PARAM, DURATION_PARAM = "ShredPercentCurve", "ShredDurationCurve"
    display_name = _name(KEY)

    def debuff(self, champion, target, time, level, duration):
        target.applyStatus(status.MRReduction("Shred"), champion, time, duration,
                           debuff_value(champion, "ShredSunderChill", level))


def apply_burn(champion, target, level, duration):
    """GE_Burn on `target` from `champion` (I7): one burn per target (StackLimitCount 1); a new application renews
    the duration but not the period (NeverReset); the first tick is one period after application
    (bExecutePeriodicEffectOnApplication false)."""
    g = champion.build.data["globals"]["burn"]
    burns = champion.__dict__.setdefault("burns", {})
    now, end = champion.tick, champion.tick + ticks_up(duration)
    b = burns.get(id(target))
    if b is None or b["end"] < now:
        burns[id(target)] = {"target": target, "next": now + ticks_up(g["period"]), "end": end, "level": level}
    else:
        b["end"], b["level"] = max(b["end"], end), max(b["level"], level)


def tick_burns(champion):
    """Deal the burns due this tick, once per tick however many burn items the holder has: true damage of
    BurnWound(level) x the target's max HP, not boosted by anything (owner, 2026-11-17; I7)."""
    if getattr(champion, "burn_tick", None) == champion.tick:
        return
    champion.burn_tick = champion.tick
    period = ticks_up(champion.build.data["globals"]["burn"]["period"])
    for b in (getattr(champion, "burns", None) or {}).values():
        while b["next"] <= champion.tick and b["next"] <= b["end"]:
            dmg = debuff_value(champion, "BurnWound", b["level"]) * b["target"].hp.stat
            # items=[]: a burn tick is not an attack or a spell, so no on-hit effect answers it
            champion.doDamage(b["target"], [], 0, dmg, dmg, "true", champion.tick / TPS)
            b["next"] += period


class BurnItem(DebuffItem):
    """An item that burns (and wounds: nothing against dummies) the targets of the holder's attacks and spells."""
    def __init__(self):
        super().__init__(phases=("preCombat", "PostOnDealDamage", "onUpdate"))

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.burns = {}
        elif phase == "onUpdate":
            tick_burns(champion)
        return super().performAbility(phase, time, champion, input_)

    def debuff(self, champion, target, time, level, duration):
        apply_burn(champion, target, level, duration)


class Morellonomicon(BurnItem):
    """Stats GE_Morellonomicon (150 HP, 20% AP, 1 mana regen). Script GA_Morellonomicon: after each damage the holder
    deals (Damage.Source.Unit) with AppliesOnHit.IsAttack or AppliesOnSpell (0x53), ApplyBurnAndWoundToTarget: GE_Burn
    at level BurnPercent (1) and GE_Wound for BurnAndWoundDuration (10 s)."""
    KEY = "DA_Morellonomicon"
    STATS = ("GE_Morellonomicon",)
    GA = "GA_Morellonomicon"
    LEVEL_PARAM, DURATION_PARAM = "BurnPercentRow", "BurnAndWoundDurationRow"
    display_name = _name(KEY)


class RedBuff(BurnItem):
    """Stats GE_RedBuff (3% damage amp, 45% AS). Script GA_RedBuff: after each damage the holder deals as a unit with
    IsAttack (0xa) or AppliesOnSpell (0x64e), GE_Burn at level Burn (1) and GE_Wound for Duration (5 s)."""
    KEY = "DA_RedBuff"
    STATS = ("GE_RedBuff",)
    GA = "GA_RedBuff"
    LEVEL_PARAM, DURATION_PARAM = "BurnCurveRow", "DurationCurveRow"
    display_name = _name(KEY)
