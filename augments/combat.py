"""The offensive combat augments (owner's list, 2026-11-18) and the Sunder30 / Shred30 entries. Every number is the
augment's row in the selected build; the timing of the timed ones is their script's (build ga_scripts.zip,
Augment_Shared / Item_Shared), or the augment's own Delay row where no script exists (the augment is effects only).
Ledger: docs/ASSUMPTIONS.md A1-A8."""
from augments.base import BuildAugment
from events import DAMAGE_POST, ITEM, UNIT, damage_tags
from items.debuffs import apply_shred, apply_sunder
from items.emblems import spatula_count
from registry import register
from timing import TPS, ticks_up

# Player combats a 2-1 augment has seen by the start of a stage (A3): stages 2 and later each hold 5 player combats
# (X-1, X-2, X-3, X-5, X-6; X-4 is a carousel, X-7 a PvE round).
STAGES = ["2-1", "3-1", "4-1", "5-1", "6-1"]
COMBATS_PER_STAGE = 5


def player_combats(params):
    return COMBATS_PER_STAGE * int(params or 0)


def stage_parameter():
    return {"Title": "Stage", "Min": 0, "Max": len(STAGES) - 1, "Default": 0, "Options": STAGES}


# ---------------------------------------------------------------- damage amp
class _DamageAmp(BuildAugment):
    ROW = "DamageAmp"

    def stats(self, champion):
        champion.dmgMultiplier.modify("+", self.value(champion, self.ROW))


@register("augment")
class GlassCannonI(_DamageAmp):
    """Glass Cannon (DA_GlassCannon_Silver): back-row allies start at 80% Health, +DamageAmp (16%). The holder is
    taken to start in the back row (the player's choice)."""
    KEY, display_name = "DA_GlassCannon_Silver", "Glass Cannon I"


@register("augment")
class GlassCannonII(_DamageAmp):
    """Glass Cannon II (DA_GlassCannon_Gold): back-row allies, +DamageAmp_Gold (25%)."""
    KEY, display_name, ROW = "DA_GlassCannon_Gold", "Glass Cannon II", "DamageAmp_Gold"


@register("augment")
class StrangeDuetI(_DamageAmp):
    """Strange Duet (DA_StrangeDuet): allies that start isolated in pairs, +5% amp (and durability); taken to apply."""
    KEY, display_name = "DA_StrangeDuet", "Strange Duet I"


@register("augment")
class StrangeDuetII(_DamageAmp):
    """Strange Duet II (DA_StrangeDuetII): +8% amp for allies isolated in pairs."""
    KEY, display_name = "DA_StrangeDuetII", "Strange Duet II"


@register("augment")
class StrangeDuetIII(_DamageAmp):
    """Strange Duet III (DA_StrangeDuetIII): +14% amp for allies isolated in pairs."""
    KEY, display_name = "DA_StrangeDuetIII", "Strange Duet III"


@register("augment")
class ItsMeBaby(BuildAugment):
    """It's Me Baby (DA_ItsMeBaby): the unit in the championship hex gains DamageAmpPercent (15%) and AttackSpeed (x1.15,
    MultiplyAdditive). The holder is taken to stand in it."""
    KEY, display_name = "DA_ItsMeBaby", "It's Me Baby"

    def stats(self, champion):
        champion.dmgMultiplier.modify("+", self.value(champion, "DamageAmpPercent"))
        champion.aspd.modify("MultiplyAdditive", self.value(champion, "AttackSpeed"))


class _AmpAfter(BuildAugment):
    """+DamageAmp after ActivationDelay seconds of combat (effects only, no script: the row's delay, on the tick at or
    after it, A2)."""

    def __init__(self, level=1, params=0):
        super().__init__(level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        amp = self.value(champion, "DamageAmp")
        champion.schedule_tick(champion.tick + ticks_up(self.value(champion, "ActivationDelay")),
                               lambda: champion.dmgMultiplier.modify("+", amp))
        return input_


@register("augment")
class Ascension(_AmpAfter):
    """Ascension (DA_Ascension): after 12 s of combat, +35% damage amp."""
    KEY, display_name = "DA_Ascension", "Ascension"


@register("augment")
class PartialAscension(_AmpAfter):
    """Partial Ascension (DA_PartialAscension): after 12 s of combat, +20% damage amp."""
    KEY, display_name = "DA_PartialAscension", "Partial Ascension"


# ---------------------------------------------------------------- AD / AP
class _ADAP(BuildAugment):
    ROWS = ()  # (row, scale) pairs added to both AD and AP

    def stats(self, champion):
        v = sum(self.value(champion, r) * k for r, k in self.ROWS)
        champion.bonus_ad.modify("+", v)
        champion.ap.modify("+", v)


@register("augment")
class BattleOfTheBands(_ADAP):
    """Battle of the Bands (DA_BattleOfTheBands): with 2+ active Bands, +18% AD and AP to the team (owner: always
    active)."""
    KEY, display_name, ROWS = "DA_BattleOfTheBands", "Battle of the Bands", (("AttackDamageAndAbilityPower", 1),)


@register("augment")
class DoubleTrouble(_ADAP):
    """Double Trouble (DA_DoubleTrouble): exactly 2 copies of a champion: both +25% AD and AP (and resists). The holder
    is taken to be one of the pair."""
    KEY, display_name, ROWS = "DA_DoubleTrouble", "Double Trouble", (("DamageStatAdd", 1),)


class _HoldTheLine(BuildAugment):
    """Hold the Line (DA_HoldTheLine): back-2-row allies gain AttackDamagePcntPerFrontLiner and
    AbilityPowerPcntPerFrontLiner (11%) per ally starting in the front row; the holder in the back rows."""
    KEY = "DA_HoldTheLine"
    FRONT = 0

    def stats(self, champion):
        champion.bonus_ad.modify("+", self.value(champion, "AttackDamagePcntPerFrontLiner") * self.FRONT)
        champion.ap.modify("+", self.value(champion, "AbilityPowerPcntPerFrontLiner") * self.FRONT)


@register("augment")
class HoldTheLine7(_HoldTheLine):
    display_name, FRONT = "Hold the Line (7 units)", 7


@register("augment")
class HoldTheLine5(_HoldTheLine):
    display_name, FRONT = "Hold the Line (5 units)", 5


class _StagedADAP(BuildAugment):
    """+AD and AP that grow with player combats: the stage is the parameter (A3)."""

    @staticmethod
    def extraParameters():
        return stage_parameter()


@register("augment")
class EarlyLearnings(_StagedADAP):
    """Early Learnings (DA_EarlyLearnings): the team gains Buff (1%) x (InitialStacks (3) + StacksPerCombat (1) per player
    combat since) AD and AP; 1-cost champions x 1CostMultiplier (2). The stage is the parameter (A3)."""
    KEY, display_name = "DA_EarlyLearnings", "Early Learnings"

    def stats(self, champion):
        stacks = self.value(champion, "InitialStacks") + self.value(champion, "StacksPerCombat") * player_combats(self.params)
        v = self.value(champion, "Buff") * stacks
        if champion.data.d.get("cost") == 1:
            v *= self.value(champion, "1CostMultiplier")
        champion.bonus_ad.modify("+", v)
        champion.ap.modify("+", v)


@register("augment")
class NoScoutNoPivot(_StagedADAP):
    """No Scout No Pivot (DA_NoScoutNoPivot): +PostCombatAdBoost / PostCombatApBoost (1%) after each player combat, from
    the stage the parameter names (A3: 0 at 2-1)."""
    KEY, display_name = "DA_NoScoutNoPivot", "No Scout No Pivot"

    def stats(self, champion):
        n = player_combats(self.params)
        champion.bonus_ad.modify("+", self.value(champion, "PostCombatAdBoost") * n)
        champion.ap.modify("+", self.value(champion, "PostCombatApBoost") * n)


@register("augment")
class TonsOfStatsI(BuildAugment):
    """Tons of Stats (DA_TonsOfStatsI): +ADAP (4%) AD and AP, AttackSpeed x1.04, Mana (4) at combat start (and Health,
    resists)."""
    KEY, display_name = "DA_TonsOfStatsI", "Tons of Stats"

    def __init__(self, level=1, params=0):
        super().__init__(level, params, phases=["preCombat"])

    def stats(self, champion):
        champion.bonus_ad.modify("+", self.value(champion, "ADAP"))
        champion.ap.modify("+", self.value(champion, "ADAP"))
        champion.aspd.modify("MultiplyAdditive", self.value(champion, "AttackSpeed"))

    def performAbility(self, phase, time, champion, input_=0):
        champion.addMana(self.value(champion, "Mana"))
        return input_


@register("augment")
class TonsOfStatsII(TonsOfStatsI):
    """Tons of Stats (Prismatic) (DA_TonsOfStatsII): 8% AD and AP, x1.08 AS, 8 mana."""
    KEY, display_name = "DA_TonsOfStatsII", "Tons of Stats (Prismatic)"


class _Timed(BuildAugment):
    """+AD/AP steps on a script's timer: WaitOnTimePassedInPhase(start, combat), then RepeatAction(interval, n) whose
    first action is at once (as Quicksilver, A1)."""
    START = INTERVAL = STEP = None
    ROWS_AD = ROWS_AP = True
    COUNT = 99

    def __init__(self, level=1, params=0):
        super().__init__(level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        start, every, step = (self.value(champion, r) for r in (self.START, self.INTERVAL, self.STEP))

        def add():
            champion.bonus_ad.modify("+", step)
            if self.ROWS_AP:
                champion.ap.modify("+", step)
        for k in range(self.COUNT):
            champion.schedule_tick(champion.tick + ticks_up(start + k * every), add)
        return input_


@register("augment")
class FocusedFire(_Timed):
    """Focused Fire (DA_FocusedFire, GA_FocusedFire): GE_FocusedFire_Stacking at activation (+AD 10%), then
    WaitOnTimePassedInPhase(Timer 5 s) and RepeatAction(Timer, 9999), first at once: +StackAD (4%) AD at 5, 10, 15 s."""
    KEY, display_name = "DA_FocusedFire", "Focused Fire"
    START, INTERVAL, STEP, ROWS_AP = "Timer", "Timer", "StackAD", False

    def stats(self, champion):
        champion.bonus_ad.modify("+", self.value(champion, "AD"))


@register("augment")
class BaronsLair(_Timed):
    """Baron's Lair (DA_BaronsLair, GA_BaronsLair): WaitOnTimePassedInPhase(StartSeconds 8), RepeatAction(IntervalSeconds
    1 s, 99) first at once: +Stats (4%) AD and AP at 8, 9, 10, ... s (the tank item is not modelled)."""
    KEY, display_name = "DA_BaronsLair", "Baron's Lair"
    START, INTERVAL, STEP = "StartSeconds", "IntervalSeconds", "Stats"


@register("augment")
class SubmitToThePit(_Timed):
    """Submit to the Pit (DA_SubmitToThePit, GA_SubmitToThePit): +AttackDamageAndAbilityPowerPerSecond (3%) AD and AP
    every IntervalSeconds (1 s) from StartSeconds (1 s) while in the center 4 rows. Whether the unit is there is the
    parameter: 'By range' (default: melee yes, ranged no), 'In the center rows', 'Outside them'."""
    KEY, display_name = "DA_SubmitToThePit", "Submit to the Pit"
    START, INTERVAL, STEP = "StartSeconds", "IntervalSeconds", "AttackDamageAndAbilityPowerPerSecond"
    PLACES = ["By range", "In the center rows", "Outside them"]

    @staticmethod
    def extraParameters():
        return {"Title": "Stands", "Min": 0, "Max": 2, "Default": 0, "Options": SubmitToThePit.PLACES}

    def performAbility(self, phase, time, champion, input_=0):
        place = self.PLACES[int(self.params or 0)]
        inside = champion.attack_range <= 1 if place == "By range" else place == "In the center rows"
        return super().performAbility(phase, time, champion, input_) if inside else input_


@register("augment")
class SoulAwakening(BuildAugment):
    """Soul Awakening (DA_SoulAwakening, GA_SoulAwakening): RepeatAction(IntervalLengthSeconds 1 s, MaxStacksNum 10) of
    GE_SoulAwakening_StatBoost: +CombatStartAdBoost / CombatStartApBoost (1.5%) AD and AP a stack; at MaxStacksNum, the
    true damage GA: TrueDamage (12%) of each damage the unit deals, as true damage. Timing as set18's (18.5 replays):
    the first stack 0.8 s into combat, then each second, the true damage from the 10th (9.8 s) (A4)."""
    KEY, display_name = "DA_SoulAwakening", "Soul Awakening"
    FIRST = 0.8  # set18 (18.5 replays: holders' hits by time; tftFightSim): the first stack 0.8 s in
    LISTENS = {DAMAGE_POST: frozenset((UNIT,))}

    def __init__(self, level=1, params=0):
        super().__init__(level, params, phases=["preCombat"])
        self.true_damage = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.true_damage = False
            n = int(self.value(champion, "MaxStacksNum"))
            ad, ap = self.value(champion, "CombatStartAdBoost"), self.value(champion, "CombatStartApBoost")
            every = self.value(champion, "IntervalLengthSeconds")
            for k in range(n):
                last = k == n - 1

                def stack(last=last):
                    champion.bonus_ad.modify("+", ad)
                    champion.ap.modify("+", ap)
                    if last:
                        self.true_damage = True
                champion.schedule_tick(champion.tick + ticks_up(self.FIRST + k * every), stack)
        elif phase == DAMAGE_POST and self.true_damage and input_.amount:
            dmg = input_.amount * self.value(champion, "TrueDamage")
            champion.doDamage(input_.target, [], 0, dmg, dmg, "true", champion.tick / TPS,
                              tags=damage_tags("true", ITEM))
        return input_


# ---------------------------------------------------------------- attack speed, mana
@register("augment")
class Espresso(BuildAugment):
    """That's That Espresso (DA_ThatsThatEspresso): the team gains InitialAttackSpeed (x1.1); after Delay (12 s),
    FinalAttackSpeed (x1.3) instead (effects only: the row's delay, A2). The Recurve Bow is not modelled."""
    KEY, display_name = "DA_ThatsThatEspresso", "Espresso"

    def __init__(self, level=1, params=0):
        super().__init__(level, params, phases=["preCombat"])

    def stats(self, champion):
        champion.aspd.modify("MultiplyAdditive", self.value(champion, "InitialAttackSpeed"), key="espresso")

    def performAbility(self, phase, time, champion, input_=0):
        final = self.value(champion, "FinalAttackSpeed")
        champion.schedule_tick(champion.tick + ticks_up(self.value(champion, "Delay")),
                               lambda: champion.aspd.modify("MultiplyAdditive", final, key="espresso"))
        return input_


@register("augment")
class ComebackStory(BuildAugment):
    """Comeback Story (DA_ComebackStory, GA_ComebackStory): the team gains ASMultiplyPerMissingHP (0.4%) attack speed per
    missing player Health (and Health). The player's Health is the parameter (default 50)."""
    KEY, display_name = "DA_ComebackStory", "Comeback Story"

    @staticmethod
    def extraParameters():
        return {"Title": "Player Health", "Min": 1, "Max": 100, "Default": 50}

    def stats(self, champion):
        hp = int(self.params or 50)
        champion.aspd.modify("MultiplyAdditive", 1 + self.value(champion, "ASMultiplyPerMissingHP") * (100 - hp))


@register("augment")
class ZekesHerald(BuildAugment):
    """Zeke's Herald (DA_ZekesHeraldAugment): the holder and allies within 2 hexes in its row gain AllyAS (x1.3,
    MultiplyAdditive). Owner: an ally holds it, this unit in range."""
    KEY, display_name = "DA_ZekesHeraldAugment", "Zeke's Herald"

    def stats(self, champion):
        champion.aspd.modify("MultiplyAdditive", self.value(champion, "AllyAS"))


@register("augment")
class ChaliceOfPower(BuildAugment):
    """Chalice of Power (DA_ChaliceOfPowerAugment): the holder and allies within 2 hexes in its row gain AllyAP (25%) and
    AllyMana (1 mana regen). Owner: an ally holds it, this unit in range."""
    KEY, display_name = "DA_ChaliceOfPowerAugment", "Chalice of Power"

    def stats(self, champion):
        champion.ap.modify("+", self.value(champion, "AllyAP"))
        champion.manaRegen.modify("+", self.value(champion, "AllyMana"))


@register("augment")
class URF(BuildAugment):
    """U.R.F. (DA_URF): GE_URF gives AS (MultiplyAdditive 0.2) and ManaPerSecond (3), each x MMC_NumSpatulaItemsOnHolder:
    1 per Spatula, Frying Pan or emblem the unit holds, 2 per Tactician's item (items.emblems.spatula_count; A6).
    Nothing when it holds none."""
    KEY, display_name = "DA_URF", "U.R.F."

    def stats(self, champion):
        n = spatula_count(champion)
        if n:
            champion.aspd.modify("MultiplyAdditive", 1 + n * self.value(champion, "AS"))
            champion.manaRegen.modify("+", n * self.value(champion, "ManaRegen"))


@register("augment")
class SeraphimsStaff(BuildAugment):
    """Seraphim's Staff (DA_SeraphimsStaff): Archangel's Staff grants ManaPerSecond (2) more mana regen while its holder
    has APThreshold (an AP multiplier of 2.1: 110% bonus) or more. Needs Archangel's Staff on the unit; checked every
    tick, so it switches on when Archangel's stacks reach it (A7)."""
    KEY, display_name = "DA_SeraphimsStaff", "Seraphim's Staff"

    def __init__(self, level=1, params=0):
        super().__init__(level, params, phases=["preCombat", "onUpdate"])
        self.on = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.on = False
            self.holder = any(type(i).__name__ == "ArchangelsStaff" for i in champion.items)
        elif self.holder and not self.on and champion.ap.stat >= self.value(champion, "APThreshold") - 1e-9:
            self.on = True
            champion.manaRegen.modify("+", self.value(champion, "ManaPerSecond"))
        return input_


# ---------------------------------------------------------------- trait augments
@register("augment")
class DigOnThis(BuildAugment):
    """Dig on This (DA_Jazz19_DigOnThis): Jazz champions gain BonusPercent (150%) more Health and damage amp from Jazz:
    a Jazz member gets 1.5 x its Jazz amp again (the Jazz trait on the page sets the tier and the trait count)."""
    KEY, display_name = "DA_Jazz19_DigOnThis", "Dig on This"
    JAZZ = "DA_Jazz19"

    def stats(self, champion):
        jazz = next((i for i in champion.items if type(i).__name__ == "Jazz" and i.level), None)
        if jazz is None or self.JAZZ not in (champion.data.d.get("trait_keys") or []):
            return
        trait = champion.build.trait(self.JAZZ)
        amp = trait.row("JazzDamageAmp", col=trait.tier_of(jazz.level)) * int(jazz.params or 5)
        champion.dmgMultiplier.modify("+", amp * self.value(champion, "BonusPercent"))


class _HeartsteelAugment(BuildAugment):
    """Read by the Heartsteel trait: `heartsteel_extra(champion, bias, fielded)` is the extra share of its bonuses."""

    def heartsteel_extra(self, champion, bias, fielded):
        return 0


@register("augment")
class BigSolo(_HeartsteelAugment):
    """Big Solo (DA_Augment19_Heartsteel_BigSolo): Heartsteel Biases gain ActiveBonusPercentIncrease (150%) more of all
    active Heartsteel bonuses (the Heartsteel trait adds it for a Bias)."""
    KEY, display_name = "DA_Augment19_Heartsteel_BigSolo", "Big Solo"

    def heartsteel_extra(self, champion, bias, fielded):
        return self.value(champion, "ActiveBonusPercentIncrease") if bias else 0


@register("augment")
class SmallSquad(_HeartsteelAugment):
    """Small Squad (DA_Augment19_Heartsteel_SmallSquad): with MaxHeartsteelChamps (3) or fewer Heartsteel champions
    fielded, their bonuses increase by BonusPercentIncrease (100%) (the Heartsteel trait counts its tick boxes)."""
    KEY, display_name = "DA_Augment19_Heartsteel_SmallSquad", "Small Squad"

    def heartsteel_extra(self, champion, bias, fielded):
        member = "DA_Heartsteel19" in (champion.data.d.get("trait_keys") or [])
        ok = member and fielded <= self.value(champion, "MaxHeartsteelChamps")
        return self.value(champion, "BonusPercentIncrease") if ok else 0


# ---------------------------------------------------------------- not augments: target debuffs (owner, 2026-11-18)
class _Debuff30(BuildAugment):
    """Every enemy is debuffed by 30% for the whole combat (a page entry, not an augment: the shared GE at debuff level
    30 = x0.7, CT_DebuffLevelToValue)."""
    KEY = None
    LEVEL = 30
    APPLY = None

    def __init__(self, level=1, params=0):
        super().__init__(level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        for d in champion.opponents or []:
            type(self).APPLY(champion, d, self.LEVEL, 10 ** 4)
        return input_


@register("augment")
class Sunder30(_Debuff30):
    display_name = "30% Sunder (armor)"
    APPLY = staticmethod(apply_sunder)


@register("augment")
class Shred30(_Debuff30):
    display_name = "30% Shred (MR)"
    APPLY = staticmethod(apply_shred)
