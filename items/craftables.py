"""The offensive craftables (the Craftable table; owner, 2026-11-17: no tank items). Status and evidence per item:
docs/ITEMS.md."""
from buildstore import BuildDataError
from registry import register
from items.base import BuildItem, StackingItem, item_name
from effects import ActiveEffect, apply_effect, legacy_last_tick
from items.debuffs import BurnItem, DebuffItem, debuff_value


@register("craftable")
class Deathblade(BuildItem):
    """55% AD; every bonus AD x1.15 (GE_Deathblade on Channel1: MultiplyAdditive ADMultiplier with AddFinal -1.15 + 1,
    I5). Two Deathblades: x1.30. No script."""
    KEY = "DA_Deathblade"
    STATS = ("GE_Deathblade",)
    display_name = item_name(KEY)


@register("craftable")
class RabadonsDeathcap(BuildItem):
    """55% AP; every bonus AP x1.15 (as Deathblade, GE_RabadonsDeathcap_Stats, I5). No script."""
    KEY = "DA_RabadonsDeathcap"
    STATS = ("GE_RabadonsDeathcap_Stats",)
    display_name = item_name(KEY)


@register("craftable")
class InfinityEdge(BuildItem):
    """35% AD, 35% crit chance, Precision (GE_InfinityEdge grants Damage.Status.CanSpellCrit). No script."""
    KEY = "DA_InfinityEdge"
    STATS = ("GE_InfinityEdge",)
    display_name = item_name(KEY)


@register("craftable")
class JeweledGauntlet(BuildItem):
    """35% AP, 35% crit chance, Precision (GE_JeweledGauntlet grants Damage.Status.CanSpellCrit). No script."""
    KEY = "DA_JeweledGauntlet"
    STATS = ("GE_JeweledGauntlet",)
    display_name = item_name(KEY)


@register("craftable")
class SpearOfShojin(BuildItem):
    """15% AD, 15% AP, 1 mana regen; "Attacks grant 5 bonus Mana" is the ManaPerAttack attribute in the same effect,
    so it is paid with the role's attack mana (I3). No script."""
    KEY = "DA_SpearOfShojin"
    STATS = ("GE_SpearOfShojin",)
    display_name = item_name(KEY)


@register("craftable")
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
    display_name = item_name(KEY)

    def per_stack(self, champion):
        stack, _ = self.script_modifier(champion, self.ga_param(champion, "GA_GuinsoosRageblade", "ItemStackGE"), "Stack", "+")
        coef, scale = self.script_modifier(champion, "GE_GuinsoosRageblade_StackingAS", "AttackSpeed", "MultiplyAdditive")
        if scale != "Stack":
            raise BuildDataError(f"{self.KEY}: StackingAS no longer scales with Stack ({scale})")
        self.stack_modifier(champion, "AttackSpeed", "MultiplyAdditive", 1 + coef * stack * self.next_k)


@register("craftable")
class Quicksilver(StackingItem):
    """Stats GE_Quicksilver_Stats (15% AS, 20% crit, 20 MR). Script GA_Quicksilver: WaitOnTimePassedInPhase(
    StackFrequency, combat) then RepeatAction(StackFrequency, 99) (0x343), whose first action is immediate; each
    action applies QuicksilverStackingEffect = GE_Quicksilver_StacksToAttackSpeed (AttackSpeed MultiplyAdditive 1.03).
    So +3% AS at 1, 2, 3, ... s, up to 99 times; EffectDuration (18 s) is only the Unstoppable (nothing against
    dummies). VOD4 Senna (docs/ITEMS.md): with Guinsoo's, one +0.075 AS step every 60 frames from 1 s."""
    KEY = "DA_Quicksilver"
    STATS = ("GE_Quicksilver_Stats",)
    MAX_ACTIONS = 99  # RepeatAction's count (script literal, 0x343)
    display_name = item_name(KEY)

    def period_seconds(self, champion):
        return self.row(champion, self.ga_param(champion, "GA_Quicksilver", "FrequencyCurveTable"))

    def per_stack(self, champion):
        if self.next_k > self.MAX_ACTIONS:
            return
        v, scale = self.script_modifier(champion, self.ga_param(champion, "GA_Quicksilver", "QuicksilverStackingEffect"),
                                        "AttackSpeed",
                                        "MultiplyAdditive")
        if scale is not None:
            raise BuildDataError(f"{self.KEY}: StacksToAttackSpeed is no longer a plain number ({scale})")
        champion.aspd.modify("MultiplyAdditive", v)


@register("craftable")
class TitansResolve(BuildItem):
    """Stats GE_TitansResolve_Stats (10% AS, 20 armor). Script GA_TitansResolve: at activation it applies
    StackingStatsGE = GE_TitansResolve_StackingStats (AttackDamage and AbilityPower + 0.02 x Stack); every
    Combat.Event.LaunchAttack of the holder (WaitGameplayEvent, not exact: simulated attacks count, 0x63f) and every
    attack or spell damage taken (nothing, against dummies) applies GE_TitansResolve_Stack (one stack) while Stack <
    MaxStacks (25). Full stacks: 15% max HP and Unstoppable (nothing against dummies). VOD4 Ezreal
    (docs/ITEMS.md): +2% AP on every release's frame and twice per cast (his two simulated attacks)."""
    KEY = "DA_TitansResolve"
    STATS = ("GE_TitansResolve_Stats",)
    display_name = item_name(KEY)

    def __init__(self):
        super().__init__(phases=["preCombat", "onLaunch"])
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.stacks = 0
        elif phase == "onLaunch" and self.stacks < self.row(champion, "MaxStacks"):
            self.stacks += 1
            for attr in ("AttackDamage", "AbilityPower"):
                coef, scale = self.script_modifier(
                    champion, self.ga_param(champion, "GA_TitansResolve", "StackingStatsGE"), attr, "+")
                if scale != "Stack":
                    raise BuildDataError(f"{self.KEY}: StackingStats {attr} no longer scales with Stack ({scale})")
                self.stack_modifier(champion, attr, "+", coef * self.stacks)
        return input_


@register("craftable")
class ArchangelsStaff(StackingItem):
    """Stats GE_ArchangelsStaff_Stats (30% AP, 1 mana regen). Script GA_ArchangelsStaff_RampingStats: at time 0 of
    phase 9 (combat; Blue Buff's script tests the same phase at combat start) it applies GE_ArchangelsStaff_StackToAP
    (AbilityPower + 0.01 x Stack) and starts a looping timer whose period is the FrequencyCurveRow parameter (row
    Period = 5 s); each expiry in combat applies RampingStatGE = GE_ArchangelsStaff_RampingStats (Stack + APStack =
    20). So +20 AP every 5 s from combat start. No VOD yet (predicted; set18: the same, a tick later)."""
    KEY = "DA_ArchangelsStaff"
    STATS = ("GE_ArchangelsStaff_Stats",)
    display_name = item_name(KEY)

    def period_seconds(self, champion):
        return self.row(champion, self.ga_param(champion, "GA_ArchangelsStaff_RampingStats", "FrequencyCurveRow"))

    def per_stack(self, champion):
        stack, _ = self.script_modifier(
            champion, self.ga_param(champion, "GA_ArchangelsStaff_RampingStats", "RampingStatGE"), "Stack", "+")
        coef, scale = self.script_modifier(champion, "GE_ArchangelsStaff_StackToAP", "AbilityPower", "+")
        if scale != "Stack":
            raise BuildDataError(f"{self.KEY}: StackToAP no longer scales with Stack ({scale})")
        self.stack_modifier(champion, "AbilityPower", "+", coef * stack * self.next_k)


@register("craftable")
class BlueBuff(BuildItem):
    """Stats GE_BlueBuff_Stats (6 mana regen, 15% AP, 15% AD). Script GA_BlueBuff: on activation, if the round's
    elapsed time is under 0.01 s in phase 9 (combat start), apply CombatStartManaGain = GE_BlueBuff_StartingMana
    (mana + StartingMana = 10, item source, AlwaysBank). preCombat, as set18's Blue Buff. VOD (items/BlueBuff.md E1,
    Varus): the panel's mana goes 30 -> 40 on the combat-start frame."""
    KEY = "DA_BlueBuff"
    STATS = ("GE_BlueBuff_Stats",)
    display_name = item_name(KEY)

    def __init__(self):
        super().__init__(phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.addMana(self.script_mana(champion, self.ga_param(champion, "GA_BlueBuff", "CombatStartManaGain")))
        return input_


# ---------------------------------------------------------------- items whose scripts do nothing against dummies
@register("craftable")
class Bloodthirster(BuildItem):
    """Stats GE_Bloodthirster_Stats (15% AD, 15% AP, 20 MR, 20% omnivamp). Script GA_Bloodthirster: a shield and more
    omnivamp at 60% health, which training dummies never cause (they never attack, G9)."""
    KEY = "DA_Bloodthirster"
    STATS = ("GE_Bloodthirster_Stats",)
    display_name = item_name(KEY)


@register("craftable")
class EdgeOfNight(BuildItem):
    """Stats GE_EdgeOfNight_Stats (10% AD, 10% AP, 15% AS, 20 armor). Script GA_EdgeOfNight: untargetable and a heal
    at 40% health, which dummies never cause (G9)."""
    KEY = "DA_EdgeOfNight"
    STATS = ("GE_EdgeOfNight_Stats",)
    display_name = item_name(KEY)


@register("craftable")
class SteraksGage(BuildItem):
    """Stats GE_SteraksGage_Stats (45% AD, 300 HP). Script GA_SteraksGage: a shield at 40% health, which dummies never
    cause (G9)."""
    KEY = "DA_SteraksGage"
    STATS = ("GE_SteraksGage_Stats",)
    display_name = item_name(KEY)


@register("craftable")
class HextechGunblade(BuildItem):
    """Stats GE_HextechGunblade_Stats (20% AD, 20% AP, 15% omnivamp, 1 mana regen). Script GA_HextechGunblade: heals the
    lowest-health ally for 20% of damage dealt, nothing against dummies."""
    KEY = "DA_HextechGunblade"
    STATS = ("GE_HextechGunblade_Stats",)
    display_name = item_name(KEY)


@register("craftable")
class HandOfJustice(BuildItem):
    """Stats GE_HandOfJustice_Stats (20% crit, 1 mana regen). Script GA_HandOfJustice: on activation ApplyEffect
    applies AboveThresholdGE = GE_HandOfJustice_HighHealthEffect (36% AD, 36% AP, 12% omnivamp) while health is above
    HealthThreshold (50%) and swaps to the low-health effect below it (WaitForAttributeChangeRatioThreshold). Dummies
    never hit back (G9), so the high-health effect holds all fight."""
    KEY = "DA_HandOfJustice"
    STATS = ("GE_HandOfJustice_Stats",)
    display_name = item_name(KEY)

    def applyStats(self, champion):
        super().applyStats(champion)
        for attr in ("AttackDamage", "AbilityPower"):
            v, scale = self.script_modifier(
                champion, self.ga_param(champion, "GA_HandOfJustice", "AboveThresholdGE"), attr, "+")
            if scale is not None:
                raise BuildDataError(f"{self.KEY}: HighHealthEffect {attr} is not a plain number ({scale})")
            champion.attribute(attr).modify("+", v)


@register("craftable")
class AdaptiveHelm(BuildItem):
    """Stats GE_AdaptiveHelm_Stats (20 MR, 3 mana regen, +15% mana from all sources). Script GA_AdaptiveHelm (0x3d5):
    a holder whose role tags include Tank or Fighter gets GE_AdaptiveHelm_TankFighter (armor and MR, nothing against
    dummies); any other role gets GE_AdaptiveHelm_OtherRoles (10% AD, 10% AP)."""
    KEY = "DA_AdaptiveHelm"
    STATS = ("GE_AdaptiveHelm_Stats",)
    display_name = item_name(KEY)

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.role.archetype in ("Tank", "Fighter"):
            return
        for attr in ("AttackDamage", "AbilityPower"):
            v, scale = self.script_modifier(champion, self.ga_param(champion, "GA_AdaptiveHelm", "OtherRolesGE"), attr, "+")
            if scale is not None:
                raise BuildDataError(f"{self.KEY}: OtherRoles {attr} is not a plain number ({scale})")
            champion.attribute(attr).modify("+", v)


@register("craftable")
class GiantSlayer(BuildItem):
    """Stats GE_GiantSlayer_Stats (15% AD, 15% AP, 15% AS, 15% damage amp). Script GA_GiantSlayer: before each damage
    the holder deals as a unit (WaitForDealDamage, Damage.Source.Unit), a target with Role.Tank (0x310) gives
    GE_GiantSlayer_ConditionalAmp (+AmpRatioAgainstTanks, 15%) for that damage, removed after it. Whether the dummies
    are Tanks is the choice between this entry (they are) and GiantSlayerNoTank (set18's two entries)."""
    KEY = "DA_GiantSlayer"
    STATS = ("GE_GiantSlayer_Stats",)
    display_name = item_name(KEY) + " (vs Tank)"
    VS_TANK = True

    def applyStats(self, champion):
        super().applyStats(champion)
        if self.VS_TANK:
            v, scale = self.script_modifier(champion, self.ga_param(champion, "GA_GiantSlayer", "OutgoingDamageMultHolder"),
                                            "OutgoingDamageMultiplier", "+")
            if scale is not None:
                raise BuildDataError(f"{self.KEY}: ConditionalAmp is not a plain number ({scale})")
            champion.dmgMultiplier.modify("+", v)


@register("craftable")
class GiantSlayerNoTank(GiantSlayer):
    """Giant Slayer against targets that are not Tanks: its stats only."""
    display_name = item_name(GiantSlayer.KEY) + " (vs non-Tank)"
    VS_TANK = False


# ---------------------------------------------------------------- on-attack and on-crit items
@register("craftable")
class KrakensFury(BuildItem):
    """Stats GE_KrakensFury_Stats (10% AD, 10% AS, 20 MR). Script GA_KrakensFury: every Combat.Event.LaunchAttack of
    the holder (WaitGameplayEvent, not exact: simulated attacks count, G11, as Titan's Resolve) while Stack <
    MaxStacks (15) applies ItemStackGE = GE_KrakensFury_ItemStack (Stack2 + ADCounter 3.5) and
    GE_KrakensFury_ItemStackCounter (Stack + 1); GE_KrakensFury_StackingAD gives AttackDamage + 0.01 x Stack2 (3.5% per
    stack). When Stack reaches MaxStacks (WaitForAttributeChanged) it applies BonusAS = GE_KrakensFury_BonusAS:
    AttackSpeed MultiplyAdditive by row Bonus_AS (15%)."""
    KEY = "DA_KrakensFury"
    STATS = ("GE_KrakensFury_Stats",)
    display_name = item_name(KEY)

    def __init__(self):
        super().__init__(phases=["preCombat", "onLaunch"])
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.stacks = 0
        elif phase == "onLaunch" and self.stacks < self.row(champion, "MaxStacks"):
            self.stacks += 1
            stack2, _ = self.script_modifier(champion, self.ga_param(champion, "GA_KrakensFury", "ItemStackGE"), "Stack2", "+")
            coef, scale = self.script_modifier(champion, "GE_KrakensFury_StackingAD", "AttackDamage", "+")
            if scale != "Stack2":
                raise BuildDataError(f"{self.KEY}: StackingAD no longer scales with Stack2 ({scale})")
            self.stack_modifier(champion, "AttackDamage", "+", coef * stack2 * self.stacks)
            if self.stacks == self.row(champion, "MaxStacks"):
                champion.aspd.modify("MultiplyAdditive", 1 + self.row(champion, "Bonus_AS"))
        return input_


@register("craftable")
class NashorsTooth(BuildItem):
    """Stats GE_NashorsTooth_Stats (10% AS, 15% AP, 150 HP, 20% crit, ManaPerAttack 2: paid with the role's attack
    mana, I3). Script GA_NashorsTooth: every damage the holder deals with Damage.Result.WasCrit and
    Damage.Specifiers.AppliesOnHit.IsAttack (a critical attack) applies UpgradeHandler = GE_NashorsTooth_Mana
    (+ManaPerAttack_BonusOnCrit 2, BankIfOverflow) when it lands. The engine averages crits: its onCrit phase fires
    each time the accumulated crit chance passes 1 (I6)."""
    KEY = "DA_NashorsTooth"
    STATS = ("GE_NashorsTooth_Stats",)
    display_name = item_name(KEY)

    def __init__(self):
        super().__init__(phases=["onCrit"])

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onCrit" and not input_:  # input_: is it spell damage
            champion.addMana(self.script_mana(champion, self.ga_param(champion, "GA_NashorsTooth", "UpgradeHandler")))
        return input_


@register("craftable")
class StrikersFlail(BuildItem):
    """Stats GE_StrikersFlail_Stats (150 HP, 10% AS, 20% crit, 10% damage amp). Script GA_StrikersFlail: every damage
    the holder deals with Damage.Result.WasCrit (attacks and spells) applies BuffGE = GE_StrikersFlail_Buff
    (OutgoingDamageMultiplier + DABuff 5%, BuffDuration 5 s) after it (PostApply). The buff's
    TFTStackGameplayEffectInstancesEffectComponent keeps separate instances up to MaxStacks (4); the simulator renews
    the oldest when a 5th lands (set18's rule; I6). The engine averages crits (onCrit, I6)."""
    KEY = "DA_StrikersFlail"
    STATS = ("GE_StrikersFlail_Stats",)
    display_name = item_name(KEY)

    def __init__(self):
        super().__init__(phases=["preCombat", "onCrit"])
        self.slot = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.slot = 0
        elif phase == "onCrit":
            amp, scale = self.script_modifier(champion, self.ga_param(champion, "GA_StrikersFlail", "BuffGE"),
                                              "OutgoingDamageMultiplier", "+")
            if scale is not None:
                raise BuildDataError(f"{self.KEY}: the buff is not a plain number ({scale})")
            # one effect per instance slot (TFTStackGameplayEffectInstancesEffectComponent, AggregateBySource)
            buff = ActiveEffect(f"StrikersFlail {id(self)} {self.slot}", [("dmgMultiplier", "+", amp, 1)])
            apply_effect(champion, buff, champion.tick,
                         legacy_last_tick(time, self.row(champion, "BuffDuration"), on_actor=True))
            self.slot = (self.slot + 1) % int(self.row(champion, "MaxStacks"))
        return input_


@register("craftable")
class LastWhisper(DebuffItem):
    """Stats GE_LastWhisper_Stats (20% AS, 15% AD, 20% crit). Script GA_LastWhisper: after each damage the holder
    deals (0x4fe Damage.Source.Unit, 0x6f7 attacks) it applies GE_ArmorSunder at level SunderPercent (30) for
    SunderDuration (3 s): Armor MultiplyAdditive ShredSunderChill(30) = x0.7 on Channel2. One sunder per target
    (StackLimitCount 1), renewed by each hit (effects.py)."""
    KEY = "DA_LastWhisper"
    STATS = ("GE_LastWhisper_Stats",)
    GA = "GA_LastWhisper"
    LEVEL_PARAM, DURATION_PARAM = "SunderPercentCurve", "DurationCurve"
    display_name = item_name(KEY)

    def debuff(self, champion, target, time, level, duration):
        op, channel = self.script_rule(champion, "GE_ArmorSunder", "Armor")
        sunder = ActiveEffect("Sunder", [("armor", op, debuff_value(champion, "ShredSunderChill", level), channel)])
        apply_effect(target, sunder, champion.tick, legacy_last_tick(time, duration, on_actor=False))


@register("craftable")
class VoidStaff(DebuffItem):
    """Stats GE_VoidStaff_Stats (35% AP, 15% AS, 1 mana regen). Script GA_VoidStaff: after each damage the holder
    deals (0x572 Damage.Source.Unit, 0x76b attacks) it applies GE_MRShred at level ShredPercent (30) for
    ShredDuration (5 s): MagicResist MultiplyAdditive ShredSunderChill(30) = x0.7 on Channel2, one per target."""
    KEY = "DA_VoidStaff"
    STATS = ("GE_VoidStaff_Stats",)
    GA = "GA_VoidStaff"
    LEVEL_PARAM, DURATION_PARAM = "ShredPercentCurve", "ShredDurationCurve"
    display_name = item_name(KEY)

    def debuff(self, champion, target, time, level, duration):
        op, channel = self.script_rule(champion, "GE_MRShred", "MagicResist")
        shred = ActiveEffect("Shred", [("mr", op, debuff_value(champion, "ShredSunderChill", level), channel)])
        apply_effect(target, shred, champion.tick, legacy_last_tick(time, duration, on_actor=False))


@register("craftable")
class Morellonomicon(BurnItem):
    """Stats GE_Morellonomicon (150 HP, 20% AP, 1 mana regen). Script GA_Morellonomicon: after each damage the holder
    deals (Damage.Source.Unit) with AppliesOnHit.IsAttack or AppliesOnSpell (0x53), ApplyBurnAndWoundToTarget: GE_Burn
    at level BurnPercent (1) and GE_Wound for BurnAndWoundDuration (10 s)."""
    KEY = "DA_Morellonomicon"
    STATS = ("GE_Morellonomicon",)
    GA = "GA_Morellonomicon"
    LEVEL_PARAM, DURATION_PARAM = "BurnPercentRow", "BurnAndWoundDurationRow"
    display_name = item_name(KEY)


@register("craftable")
class RedBuff(BurnItem):
    """Stats GE_RedBuff (3% damage amp, 45% AS). Script GA_RedBuff: after each damage the holder deals as a unit with
    IsAttack (0xa) or AppliesOnSpell (0x64e), GE_Burn at level Burn (1) and GE_Wound for Duration (5 s)."""
    KEY = "DA_RedBuff"
    STATS = ("GE_RedBuff",)
    GA = "GA_RedBuff"
    LEVEL_PARAM, DURATION_PARAM = "BurnCurveRow", "DurationCurveRow"
    display_name = item_name(KEY)
