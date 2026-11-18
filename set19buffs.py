"""Set 19 traits, augments and other buffs. Each is written from the selected build; a class is live only when
listed in one of the registries below."""
from buildstore import BuildDataError, load_build
from item import Item
from stats import Attack
from timing import TPS, projectile_ticks, ticks_up

class_buffs = []  # traits
augments = []
no_buff = ["NoBuff"]


class Buff(Item):
    """A trait or augment: `level` is the breakpoint (0 = off), `params` any extra input (see extraParameters)."""
    levels = [0]

    def __init__(self, name, level, params, phases):
        super().__init__(name, phases=phases)
        self.level = level
        self.params = params

    def performAbility(self, phase, time, champion, input_=0):
        raise NotImplementedError("Please Implement this method")

    def ability(self, phase, time, champion, input_=0):
        if self.level == 0:
            return input_
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

    @staticmethod
    def extraParameters():
        return 0

    def hashFunction(self):
        init_tuple = (self.name, str(self.level))
        param_tuple = (self.params,) if isinstance(self.params, int) else tuple(self.params)
        return init_tuple + param_tuple

    def __hash__(self):
        return hash(self.hashFunction())


class NoBuff(Buff):
    levels = [0]
    display_name = "NoItem"

    def __init__(self, level=0, params=0):
        super().__init__(self.display_name, level, params, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0


# ---------------------------------------------------------------- traits from the build (ledger B11)
class BuildTrait(Buff):
    """A Set 19 trait whose numbers come from the selected build.

    `level` is how many units with the trait the board fields (0 = inactive), offered at the build's breakpoints.
    In the static-stats pass (Item.applyStats, before any combat phase) the trait records the tier those units reach
    under the champion's own build (B11) in `champion.trait_tiers[KEY]`, so every phase can read it; a member's spell
    reads its trait's values at that tier (`BuildChampion.trait_value`). A trait whose effect is entirely inside its
    members' spells (Encore) does nothing else.
    """
    KEY = None
    levels = [0]

    def __init__(self, level=0, params=0, phases=None):
        super().__init__(self.display_name, level, params, phases=phases)

    @classmethod
    def breakpoints(cls, build=None):
        return (build or load_build()).trait(cls.KEY).thresholds

    def applyStats(self, champion):
        build = getattr(champion, "build", None) or load_build()
        tiers = getattr(champion, "trait_tiers", None)
        if tiers is None:
            tiers = champion.trait_tiers = {}
        tiers[self.KEY] = build.trait(self.KEY).tier_of(self.level)

    def performAbility(self, phase, time, champion, input_=0):
        return input_


class Encore(BuildTrait):
    """Encore (DA_Encore19): "When Encore champions fire projectiles with their abilities, they fire an extra one
    with reduced effectiveness." The extra missiles are in each member's spell script, which reads
    CT_Encore19 RecastEffectiveness at the Encore tier (e.g. Neeko). Non-members are unaffected."""
    KEY = "DA_Encore19"
    display_name = "Encore"


Encore.levels = [0] + Encore.breakpoints()  # the newest build's breakpoints (units on the board)

class_buffs.append("Encore")


def bounce_hexes(opponents):
    """Hexes a Trickshot ricochet travels between dummies (B12): the next one stands 1 hex away; with a single dummy
    the ricochet returns to it (the bounce computer re-picks an already-hit enemy when none is left), 0 hexes."""
    return 1 if len(opponents) > 1 else 0


class Trickshot(BuildTrait):
    """Trickshot (DA_Trickshot19): "Trickshots' Attacks and Abilities ricochet. Each ricochet deals a percentage of
    the previous bounce's damage." CT_Trickshot19 at the tier: NumRichochets (1/1/2), RichochetDamage (0.22/0.33/0.33).

    Attacks (members only; GA_LaunchProjectileAttack_Trickshot19 -> BounceComputer_Autoattacks ->
    HandleAutoAttackBounce): when an attack lands, ricochet k = 1..NumRichochets flies the attack's projectile from
    the previous target to the next (nearest not yet hit) and applies GE_AutoAttack_Bounce_Trickshot19:
    BasicAttackDamage x RichochetDamage^k (MMC_TrickshotReduction), physical, with the attack's crit result
    (PassInCritResult; the engine averages crits, so the same chance). Not an attack (no IsAttack tag): no mana, no
    attack count. Its on-hit effects at RichochetDamage^k are not modelled (no listed item has one).
    Spells: each member's own script handles the spell ricochets (e.g. Draven) at the same tier.
    """
    KEY = "DA_Trickshot19"
    display_name = "Trickshot"

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["onAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        opponents = input_
        if self.KEY not in (champion.data.d.get("trait_keys") or []) or champion.trait_tier(self.KEY) == 0:
            return input_
        n = int(champion.trait_value(self.KEY, "NumRichochets"))
        r = champion.trait_value(self.KEY, "RichochetDamage")
        step = projectile_ticks(champion.timing.proj_speed, bounce_hexes(opponents))
        for k in range(1, n + 1):
            def ricochet(k=k):
                target = opponents[k % len(opponents)]
                attack = Attack(opponents=[target], scaling=lambda level, baseAD, AD, AP: baseAD * AD * r ** k,
                                canCrit=True, canOnHit=False, attackType="physical", numTargets=1,
                                regularAuto=False)
                champion.doAttack(attack, champion.items, champion.tick / TPS)
            champion.schedule_tick(champion.tick + k * step, ricochet)
        return input_


Trickshot.levels = [0] + Trickshot.breakpoints()

class_buffs.append("Trickshot")


class KDA(BuildTrait):
    """K/DA (DA_KDA19): "K/DA champions release new songs based on their total star level. At Combat Start and after
    8 seconds, they gain power for each of their songs." `level` is the members' total star level (B14).

    GA_KDA19 applies GE_KDA19_BonusApplier to the members at combat start (TriggerOnCombatStart) and once more after
    MidCombatTrigger seconds; GA_KDA19_BonusApplier then applies, by tier (m = PreviousTraitBoost from tier 4, else 1):
      tier >= 1 (POP/STARS): GE_KDA19_ManaReduction, ManaMax MultiplyCompound by the chain (ManaReduction x m - 1) x -1
                 = 1 - 0.1 m; infinite, stack limit 1 (the second trigger adds nothing)
      tier >= 2 (DRUM GO DUM): a shield (nothing against dummies)
      tier >= 3 (VILLAIN): GE_KDA19_DecayingAS (_Boosted from tier 4): AttackSpeed MultiplyAdditive 1 + DecayingAS (x m),
                 for ASDuration s, periodic 0.25 s with bChangeOverTimeForPeriodic toward 1: the bonus falls by
                 1/32 of itself every 0.25 s (B14)
    Tier 5 (WATCH ME, a stun) changes nothing against dummies; tier 6 (FIRESTARTER) is the trait's damage
    (GE_KDA19_FirestarterDoT with the trait as source), not the unit's, and is not counted; tier 7 is 4-star units.
    """
    KEY = "DA_KDA19"
    display_name = "K/DA"
    DECAY_PERIOD = 0.25  # GE_KDA19_DecayingAS Period (effect literal)

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["preCombat"])

    def row(self, champion, name):
        """CT_KDA19 rows have one point (1); a curve is flat outside its points, so every tier reads it."""
        return champion.trait_value(self.KEY, name, tier=1)

    def _member(self, champion):
        return self.KEY in (champion.data.d.get("trait_keys") or []) and champion.trait_tier(self.KEY) > 0

    def _boost(self, champion):
        return self.row(champion, "PreviousTraitBoost") if champion.trait_tier(self.KEY) >= 4 else 1

    def applyStats(self, champion):
        super().applyStats(champion)
        if not self._member(champion):
            return
        m = self._boost(champion)
        champion.fullMana.mult *= 1 - self.row(champion, "ManaReduction") * m

    def performAbility(self, phase, time, champion, input_=0):
        if not self._member(champion) or champion.trait_tier(self.KEY) < 3:
            return input_
        m = self._boost(champion)
        bonus = self.row(champion, "DecayingAS") * m * 100  # attack speed points
        duration = self.row(champion, "ASDuration")
        steps = int(round(duration / self.DECAY_PERIOD))
        triggers = [0.0]
        if self.row(champion, "TriggerOnCombatStart") != 1:
            triggers = []
        triggers.append(self.row(champion, "MidCombatTrigger"))
        for t0 in triggers:
            for j in range(steps + 1):
                # the bonus held from step j to step j + 1; at the end of the duration it is gone
                before = bonus * (1 - (j - 1) / steps) if j else 0.0
                after = bonus * (1 - j / steps) if j < steps else 0.0
                delta = after - before
                champion.schedule_tick(champion.tick + ticks_up(t0 + j * self.DECAY_PERIOD),
                                       lambda d=delta: champion.aspd.addStat(d))
        return input_


KDA.levels = [0] + KDA.breakpoints()

class_buffs.append("KDA")


class Swiftstriker(BuildTrait):
    """Swiftstriker (DA_Swiftstriker19): "Your team gains 10% Attack Speed. Swiftstrikers gain more every 2 seconds,
    up to 5 times." CT_Swiftstriker19 at the tier: TeamAS, SwiftieAS, Period, Stacks.

    Team: GE_Swiftstriker19_AttackSpeed_Team, AttackSpeed MultiplyAdditive 1 + TeamAS, infinite, on every unit of the
    team (members or not), already shown in planning (VOD2 Yunara 0.77 = 0.7 x 1.1).
    Members (GA_Swiftstriker19, triggered at combat start by Combat.Event.Passive): TaskWaitDelay(Period), then
    RepeatAction(Period, Stacks) whose first action is immediate: GE_Swiftstriker19_AttackSpeed_Selfish (MultiplyAdditive
    1 + SwiftieAS) at Period, 2 Period, ..., Stacks x Period (2, 4, 6, 8, 10 s) (B15).
    """
    KEY = "DA_Swiftstriker19"
    display_name = "Swiftstriker"

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["preCombat"])

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) > 0:
            champion.aspd.addStat(champion.trait_value(self.KEY, "TeamAS") * 100)

    def performAbility(self, phase, time, champion, input_=0):
        if self.KEY not in (champion.data.d.get("trait_keys") or []) or champion.trait_tier(self.KEY) == 0:
            return input_
        period = champion.trait_value(self.KEY, "Period")
        bonus = champion.trait_value(self.KEY, "SwiftieAS") * 100
        for k in range(1, int(champion.trait_value(self.KEY, "Stacks")) + 1):
            champion.schedule_tick(champion.tick + ticks_up(k * period), lambda: champion.aspd.addStat(bonus))
        return input_


Swiftstriker.levels = [0] + Swiftstriker.breakpoints()

class_buffs.append("Swiftstriker")


class Arcanist(BuildTrait):
    """Arcanist (DA_Arcanist19): "Your team gains Ability Power, Arcanists gain more." CT_Arcanist19 at the tier:
    ArcanistAP (25/50/70%), NonArcanistAP (12/18/30%).

    DA_Arcanist19's TargetEffectsForTier (B16): GE_19_Arcanist_TeamAP (AbilityPower + NonArcanistAP) on allies
    without the trait (TFTAddAlliesWithoutTraitRule), GE_19_Arcanist_SelfishAP (AbilityPower + ArcanistAP) on allies
    with it (TFTAddAlliesWithTraitsOfSource): a member gets ArcanistAP only, not both. Both infinite, Channel1 (bonus
    AP, so Rabadon's multiplies it, I5). Applied in the static-stats pass like items (I1). The emblem (mana on kill)
    is not modelled.
    """
    KEY = "DA_Arcanist19"
    display_name = "Arcanist"

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0:
            return
        member = self.KEY in (champion.data.d.get("trait_keys") or [])
        champion.ap.addStat(champion.trait_value(self.KEY, "ArcanistAP" if member else "NonArcanistAP") * 100)


Arcanist.levels = [0] + Arcanist.breakpoints()

class_buffs.append("Arcanist")


class Hyperpop(BuildTrait):
    """Hyperpop (DA_GlitterBomb19): "Hyperpop champions gain Health and Attack Speed. After player combat, they
    generate Hype ..." CT_GlitterBomb19 at the tier: BaseAttackSpeed (10/15/25/40%), BaseHealth (100/200/300/500).

    The (2) tier gives GE_Glitterbomb19_UnitStats to members only (TFTAddAllAlliesTargetRule then
    TFTRemoveIfNotHasTraitTargetRule): AttackSpeed MultiplyAdditive AttackSpeedCalc1 = BaseAttackSpeed x
    MagicDamageCalc1 + 1, HealthMax + BaseHealth x MagicDamageCalc1, where MagicDamageCalc1 = PercentIncreasePerLevel
    x Stack (the Hype level) + 1. PercentIncreasePerLevel is 0 at every tier in this build, so Hype doesn't change
    combat stats; the AttackSpeedPerHypeLevel / FlatHealthPerHypeLevel rows are read by no effect or script, and
    HypeMult only scales the Hype earned (GA_GlitterBomb19). Hype rewards (gold, items, units) are outside combat.
    A build where PercentIncreasePerLevel is not 0 raises: the Hype level would then be a parameter.
    """
    KEY = "DA_GlitterBomb19"
    display_name = "Hyperpop"

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0 or self.KEY not in (champion.data.d.get("trait_keys") or []):
            return
        if champion.trait_value(self.KEY, "PercentIncreasePerLevel") != 0:
            raise BuildDataError(f"{self.KEY}: PercentIncreasePerLevel is not 0 in build {champion.build.version}: "
                                 f"Hype now scales the stats (needs a Hype-level parameter)")
        champion.aspd.addStat(champion.trait_value(self.KEY, "BaseAttackSpeed") * 100)


Hyperpop.levels = [0] + Hyperpop.breakpoints()

class_buffs.append("Hyperpop")


class IonicSpark(BuildTrait):
    """Ionic Spark (DA_IonicSpark19): "Fans cheer on Ionic Spark members with gifts every 4 seconds. (3) Letters that
    restore 2% Health and grant 7% AS. (5) Personalized gifts that grant 25% AD or 25% AP. (7) gold and consumables.
    (10) Fans rush the stage!" (B22)

    Letters, (3)+ (GA_IonicSpark19_LetterFan): RepeatAction(LetterFrequency (4 s), 99) from the army's arrival
    (OnReinforcementArmyTravelEnd); action 0 sends nothing (ActionNumber > 0, 0x2c8), each later one sends
    Set19.Trait.IonicSpark.SendLetters, and GA_IonicSpark19_FansManager throws a letter to every member in combat
    (GetFansAndMembersForLetterGranting: the fans round-robin). On arrival, GE_IonicSpark19_LetterAS (AttackSpeed
    MultiplyAdditive AttackSpeedCalc1 = LetterASGain + 1, infinite for the combat, no stack limit) and a heal (nothing
    against dummies). So +7% AS at 4, 8, 12, ... s; the letter's flight from the fans is not modelled.
    Gifts, (5)+ (GA_IonicSpark19_BigGiftFan): RepeatAction(LetterFrequency, 99) whose first action is immediate picks
    DetermineNextIonicSparkMemberToBuff (members, Tanks last (TR_Sort_ByRoleWeighted TankWeight 0), then by items
    equipped, without Set19.Trait.IonicSpark.GiftRecieved) and throws a gift: Role.Attack gets GE_IonicSpark19_Gift_
    Attack (AttackDamage + PersonalGiftAD 25%), Role.Magic or Role.Hybrid GE_IonicSpark19_Gift_Magic (AbilityPower +
    PersonalGiftAP 25%), once per combat. Which gift this unit gets is the 'Gift' option (1st at 0 s, 2nd at 4 s, 3rd
    at 8 s, or none); the throw and flight are not modelled. Bonus Health, (7)'s economy and (10)'s waves of fans
    (damage to enemies, not modelled) aside.
    """
    KEY = "DA_IonicSpark19"
    display_name = "Ionic Spark"
    team_trait = False  # members only: the gift order is about this unit
    GIFTS = ["1st", "2nd", "3rd", "None"]
    ACTIONS = 99  # RepeatAction's count (both fans)

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["preCombat"])

    @staticmethod
    def extraParameters():
        return {"Title": "Gift", "Min": 0, "Max": len(IonicSpark.GIFTS) - 1, "Default": 0, "Options": IonicSpark.GIFTS}

    def performAbility(self, phase, time, champion, input_=0):
        tier = champion.trait_tier(self.KEY)
        if tier == 0 or self.KEY not in (champion.data.d.get("trait_keys") or []):
            return input_
        period = champion.trait_value(self.KEY, "LetterFrequency")
        letter = champion.trait_value(self.KEY, "LetterASGain") * 100
        for k in range(1, self.ACTIONS):
            champion.schedule_tick(champion.tick + ticks_up(k * period), lambda: champion.aspd.addStat(letter))
        if tier >= 2 and self.GIFTS[self.params] != "None":
            attack = champion.role.key.startswith("Attack")
            stat = champion.bonus_ad if attack else champion.ap
            gift = champion.trait_value(self.KEY, "PersonalGiftAD" if attack else "PersonalGiftAP") * 100
            champion.schedule_tick(champion.tick + ticks_up(self.params * period), lambda: stat.addStat(gift))
        return input_


IonicSpark.levels = [0] + IonicSpark.breakpoints()

class_buffs.append("IonicSpark")


class Hitmaker(BuildTrait):
    """Hitmaker (DA_Hitmaker19): "Hitmakers gain 12% Attack Damage. The Hitmakers with the most items become Big Shots,
    gaining even more Attack Damage." CT_Hitmaker19 at the tier: BaseAD (12%), BonusAD (20/35%), NumHitmakers (1/2).

    Every member: DA_Hitmaker19's tier effect GE_19_Hitmaker_BaseAD (AttackDamage + BaseAD) (B18).
    Big Shots: GA_Hitmaker19 UpdateBigShots, outside combat, registers MostItemsTargetEffects: the NumHitmakers members
    first by TR_Sort_ByNumItemsEquipped (after TR_Sort_ByStrongestRules and an attribute sort) get
    GE_19_Hitmaker_BonusAD (AttackDamage + BonusAD) as well: 32% / 47% in all. Which members those are depends on the
    whole board, so it is the "Is Big Shot" flag (default 1). Both effects are infinite, Channel1 (bonus AD,
    multiplied by Deathblade, I5). The emblem is not modelled.
    """
    KEY = "DA_Hitmaker19"
    display_name = "Hitmaker"
    team_trait = False  # the flag is about this champion, not membership

    @staticmethod
    def extraParameters():
        return {"Title": "Is Big Shot", "Min": 0, "Max": 1, "Default": 1}

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0 or self.KEY not in (champion.data.d.get("trait_keys") or []):
            return
        champion.bonus_ad.addStat(champion.trait_value(self.KEY, "BaseAD") * 100)
        if self.params:
            champion.bonus_ad.addStat(champion.trait_value(self.KEY, "BonusAD") * 100)


Hitmaker.levels = [0] + Hitmaker.breakpoints()

class_buffs.append("Hitmaker")


class Illbeats(BuildTrait):
    """Illbeats (DA_Illbeats19): "Open the Illbeats Mixer to allocate Decibels. Illbeats champions receive different
    stats based on your mix. Your team gains 50% of the mix." (B20)

    The tier grants GE_Illbeats19_GrantStats to members and GE_Illbeats19_GrantSelflessStats to everyone else; each
    grants one GA_Illbeats19_UpdateStat per channel (HP Stack, AD Stack2, AP Stack3, gold Stack4). CalculateStatAmount
    sums CT_Illbeats19_PercentAtEachTick's row at ticks 1..n (n = the channel's decibels), times StatMult at the trait
    level (1 / 1 / 1.5), times SelflessStatMult (0.5) for non-members, and applies it as the channel's effect:
    GE_Illbeats19_PercentAttackDamage / PercentAbilityPower (AttackDamage / AbilityPower +, Channel1). Decibels: Remix
    (10 / 14 / 18) in all, at most MaxRemixPerChannel (10) per channel. Applied while planning (the stat is not
    changed in combat), so in the static-stats pass. HP and gold chance change nothing against dummies.

    The mix is the parameter (Options): every decibel the option doesn't spend on AD or AP goes to HP or gold.
    """
    KEY = "DA_Illbeats19"
    display_name = "Illbeats"
    TABLE = "CT_Illbeats19_PercentAtEachTick"
    MIXES = ["All AD", "All AP", "Split AD/AP", "No AD/AP"]

    @staticmethod
    def extraParameters():
        return {"Title": "Mix", "Min": 0, "Max": len(Illbeats.MIXES) - 1, "Default": 0, "Options": Illbeats.MIXES}

    def ticks(self, champion):
        """(AD decibels, AP decibels) of the chosen mix at the board's tier."""
        total = int(champion.trait_value(self.KEY, "Remix"))
        cap = int(champion.trait_value(self.KEY, "MaxRemixPerChannel"))
        mix = self.MIXES[self.params]
        if mix == "All AD":
            return min(cap, total), 0
        if mix == "All AP":
            return 0, min(cap, total)
        if mix == "Split AD/AP":
            ad = min(cap, (total + 1) // 2)
            return ad, min(cap, total - ad)
        return 0, 0

    def channel_value(self, champion, row, n):
        """The channel's stat at n decibels for a member: CalculateStatAmount's sum x StatMult."""
        from build_champion import curve_at  # build_champion imports this module
        pts = champion.build.trait(self.KEY).table_row(self.TABLE, row)
        total = sum(curve_at(pts, i, "Linear") for i in range(1, n + 1))
        return total * champion.trait_value(self.KEY, "StatMult")

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0:
            return
        member = self.KEY in (champion.data.d.get("trait_keys") or [])
        share = 1 if member else champion.trait_value(self.KEY, "SelflessStatMult")
        ad, ap = self.ticks(champion)
        champion.bonus_ad.addStat(self.channel_value(champion, "PercentAD", ad) * share * 100)
        champion.ap.addStat(self.channel_value(champion, "PercentAP", ap) * share * 100)


Illbeats.levels = [0] + Illbeats.breakpoints()

class_buffs.append("Illbeats")


class Heartsteel(BuildTrait):
    """Heartsteel (DA_Heartsteel19): "(1) Heartsteel members grant your team bonuses. (3) Choose a Bias, empowering
    their Ability. (5) Choose a 2nd Bias. (7) Heartsteel champions gain an additional 150% of active Heartsteel
    bonuses." (B21)

    GA_Heartsteel19_BonusManager tags the army with <Name>Active for each member fielded (one bonus however many
    copies), and the (1) tier gives every ally (TFTAddAllAlliesTargetRule) each active member's SelflessBonus, Channel1:
    Kayn AttackDamage + KaynAD (7%), Alune AbilityPower + AluneAP (7%), Aphelios AttackSpeed x (1 + ApheliosAS (6%)),
    Ezreal CritChance + EzrealCritChance (10%); Sett, K'Sante, Yone and Sona give HP, armor/MR, omnivamp and healing,
    which change nothing against dummies. The (7) tier gives Heartsteel members each active member's StanBonus as well:
    the row x StanPercentIncrease (1.5 at level 4). Ezreal's StanBonus reads the plain 10% (DamageAmpCalc1, not
    TrueDamageCalc1); the owner ruled (2026-11-17) to follow the tooltip, +15%. The (3) and (5) tiers give a member
    chosen as Bias the SpellUpgradeTierIsActive + Selected tags its spell checks (`champion.heartsteel_bias`, e.g.
    Ezreal). The two (7) tiers are the same level with and without the Prismatic quest; its car is not modelled.

    Which members are fielded, and whether this unit is a Bias, are tick boxes (the parameter's bits). A unit always
    counts itself as fielded.
    """
    KEY = "DA_Heartsteel19"
    display_name = "Heartsteel"
    # tick box -> (champion, curve row, where it lands); AD, AP and AS are percent points, crit a fraction (I1)
    MEMBERS = [
        ("Kayn", "DA_Kayn19", "KaynAD", lambda c, v: c.bonus_ad.addStat(v * 100)),
        ("Alune", "DA_Alune19", "AluneAP", lambda c, v: c.ap.addStat(v * 100)),
        ("Aphelios", "DA_Aphelios19", "ApheliosAS", lambda c, v: c.aspd.addStat(v * 100)),
        ("Ezreal", "DA_Ezreal19", "EzrealCritChance", lambda c, v: c.crit.addStat(v)),
    ]
    BIAS = len(MEMBERS)  # the bit after the members

    @staticmethod
    def extraParameters():
        names = [m[0] for m in Heartsteel.MEMBERS] + ["Bias"]
        # default: Ezreal fielded and a Bias (the one Heartsteel champion implemented)
        return {"Title": "Fielded", "Min": 0, "Max": 2 ** len(names) - 1, "Default": (1 << 3) | (1 << Heartsteel.BIAS),
                "Flags": names, "TeamFlags": len(Heartsteel.MEMBERS)}

    def applyStats(self, champion):
        if getattr(champion, "trait_tiers", None) is None:
            champion.trait_tiers = {}
        # trait level = distinct breakpoints reached: (7) is level 4 with or without its Prismatic quest
        champion.trait_tiers[self.KEY] = sum(1 for t in self.levels[1:] if self.level >= t)
        tier = champion.trait_tier(self.KEY)
        champion.heartsteel_bias = False
        if tier == 0:
            return
        member = self.KEY in (champion.data.d.get("trait_keys") or [])
        stan = champion.trait_value(self.KEY, "StanPercentIncrease") if member else 0
        for bit, (name, key, row, add) in enumerate(self.MEMBERS):
            if not (self.params >> bit) & 1 and getattr(champion, "KEY", None) != key:
                continue
            add(champion, champion.trait_value(self.KEY, row) * (1 + stan))
        champion.heartsteel_bias = member and tier >= 2 and bool((self.params >> self.BIAS) & 1)


Heartsteel.levels = [0] + sorted(set(Heartsteel.breakpoints()))

class_buffs.append("Heartsteel")


class TrueDamage(BuildTrait):
    """True Damage (DA_TrueDamage19), A-Side (Win) only: "True Damage members deal 18% / 30% bonus true damage."

    DA_TrueDamage19 has six tiers, three per side (A-Side: trait levels 1-3 at (3), (5), (5) Prismatic; B-Side: 4-6).
    The A-Side (3) tier gives members GE_TrueDamage19_GrantBonusTDGA, whose GA_TrueDamage19_DealBonusTD answers every
    damage the unit deals (WaitForDealDamage, Damage.Source.Unit, PostApply) with GE_TrueDamage19_DealTrueDamage:
    the damage dealt x SideB_BonusTDPercent at the trait level (B19). The (5) tier's effects in this build are an
    execute and omnivamp whose rows are 0; the owner ruled (2026-11-17) to follow its tooltip, 30% bonus true damage.
    The B-Side's combat effects and the Prismatic quest tiers are not modelled. The bonus is not itself a trigger
    (no other effect hears it) and is not amplified again.
    """
    KEY = "DA_TrueDamage19"
    display_name = "True Damage"
    levels = [0, 3, 5]  # A-Side units on the board

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["PostOnDealDamage"])

    def applyStats(self, champion):
        if getattr(champion, "trait_tiers", None) is None:
            champion.trait_tiers = {}
        # A-Side trait level: 1 at (3), 2 at (5) (the Prismatic level 3 needs its quest)
        champion.trait_tiers[self.KEY] = 2 if self.level >= 5 else 1 if self.level >= 3 else 0

    def performAbility(self, phase, time, champion, input_=0):
        if (champion.trait_tier(self.KEY) == 0 or self.KEY not in (champion.data.d.get("trait_keys") or [])
                or not input_ or not input_[0]):
            return input_
        bonus = champion.trait_value(self.KEY, "SideB_BonusTDPercent") * input_[0]
        # items=[]: nothing reacts to the bonus itself (and it doesn't trigger itself)
        champion.doDamage(champion.lastDamagedOpponent, [], 0, bonus, bonus, "true", time)
        return input_


class_buffs.append("TrueDamage")
