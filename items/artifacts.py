"""Artifacts (ledger I10). Damage an artifact deals on its own is not boosted, can't crit and triggers no item."""
from registry import register
from timing import TPS, ticks_up
from events import ITEM, LAUNCH, ONHIT_AFTER, ONHIT_PRE, damage_tags
from items.base import BuildItem, item_name
from layout import in_play


# ---------------------------------------------------------------- artifacts (I10)
@register("artifact")
class InfinityForce(BuildItem):
    """Stats GE_Artifact_InfinityForce (30% AD, 30% AP, 30% AS, 30 armor, 30 MR, 300 HP). No script."""
    KEY = "DA_Artifact_InfinityForce"
    STATS = ("GE_Artifact_InfinityForce",)
    display_name = item_name(KEY)


@register("artifact")
class GoldCollector(BuildItem):
    """Stats GE_Artifact_GoldCollector (35% AD, 20% crit). Script GA_Artifact_GoldCollector: executes enemies below
    ExecuteThreshold (12%) of max Health and drops gold; dummies never lose health (G9), so stats only."""
    KEY = "DA_Artifact_GoldCollector"
    STATS = ("GE_Artifact_GoldCollector",)
    display_name = item_name(KEY)


@register("artifact")
class LudensTempest(BuildItem):
    """Stats GE_Artifact_LudensTempest_Stats (55% AD, 55% AP). Script GA_Artifact_LudensTempest: overkill damage + 130
    to the two nearest enemies when the holder kills; dummies never die (G9), so stats only."""
    KEY = "DA_Artifact_LudensTempest"
    STATS = ("GE_Artifact_LudensTempest_Stats",)
    display_name = item_name(KEY)


@register("artifact")
class HorizonFocus(BuildItem):
    """Stats GE_Artifact_HorizonFocus_Stats (250 HP, 20 armor, 20 MR, 2 mana regen). Script GA_Artifact_HorizonFocus:
    lightning for 30% of a stunned enemy's max Health; no implemented champion stuns, so stats only."""
    KEY = "DA_Artifact_HorizonFocus"
    STATS = ("GE_Artifact_HorizonFocus_Stats",)
    display_name = item_name(KEY)


@register("artifact")
class SeekersArmguard(BuildItem):
    """Stats GE_Artifact_SeekersArmguard_Stats (25% AP, 10 armor, 10 MR, 20% omnivamp). Script
    GA_Artifact_SeekersArmguard: +20 armor, MR and AP per takedown; dummies never die (G9), so stats only."""
    KEY = "DA_Artifact_SeekersArmguard"
    STATS = ("GE_Artifact_SeekersArmguard_Stats",)
    display_name = item_name(KEY)


@register("artifact")
class Fishbones(BuildItem):
    """Stats GE_Artifact_Fishbones_Stats (25% AD, 25% AS, +2 attack range: no effect on flights, I10).
    GE_Artifact_Fishbones_Targeting makes attacks pick random enemies (Target.Overridden): every dummy is the same.
    No script."""
    KEY = "DA_Artifact_Fishbones"
    STATS = ("GE_Artifact_Fishbones_Stats",)
    display_name = item_name(KEY)


@register("artifact")
class RapidFireCannon(BuildItem):
    """Stats GE_Artifact_RapidFireCannon_Stats (55% AS, damage amp x1.05, +1 attack range: no effect on flights,
    owner 2026-11-17, I10). Script
    GA_Artifact_RapidFireCannon: +1 range per kill; dummies never die (G9)."""
    KEY = "DA_Artifact_RapidFireCannon"
    STATS = ("GE_Artifact_RapidFireCannon_Stats",)
    display_name = item_name(KEY)


@register("artifact")
class SilvermereDawn(BuildItem):
    """Stats GE_Artifact_SilvermereDawn_Stats (150% AD, 30 armor, 30 MR, 30% omnivamp, AttackSpeed Override 0.5: the
    holder's attack speed is 0.5 whatever else it has, I10). Script GA_Artifact_SilvermereDawn: attacks stun for 0.8 s,
    nothing against dummies."""
    KEY = "DA_Artifact_SilvermereDawn"
    STATS = ("GE_Artifact_SilvermereDawn_Stats",)
    display_name = item_name(KEY)



def item_damage(champion, target, amount, dtype):
    """Damage an item deals on its own (I10): not boosted by damage amp (owner, 2026-11-17), can't crit, and
    tagged Damage.Source.Item, so no effect that waits for the unit's damage hears it."""
    if amount > 0 and target is not None:
        champion.doDamage(target, champion.items, 0, amount, amount, dtype, champion.tick / TPS,
                          tags=damage_tags(dtype, ITEM))


def stage_value(item, champion, row):
    """A row keyed by stage (TFTStageMagnitude's lookup), at the stage the page's 'Current stage' sets."""
    from build_champion import curve_at  # build_champion imports this module's registries
    return curve_at(item.build_entry(champion).row(row), champion.stage, "Constant")


@register("artifact")
class LichBane(BuildItem):
    """Stats GE_Artifact_LichBane_Stats (55% AP, 10% AS). Script GA_Artifact_LichBane: every cast (0x917) arms it
    (ProcReady, 0x4da; no stacking); a melee holder procs on its next on-hit damage, a ranged one on the on-hit damage
    after its next attack release (0x7e7; simulated attacks count). After that hit (PostApply), GE_Artifact_
    LichBane_Damage: magic damage GenericCalc1 = ProcDamage at the current stage (250/250/350/500/600/700)."""
    KEY = "DA_Artifact_LichBane"
    STATS = ("GE_Artifact_LichBane_Stats",)
    display_name = item_name(KEY)

    LISTENS = {LAUNCH: frozenset(), ONHIT_AFTER: frozenset()}

    def __init__(self):
        super().__init__(phases=["preCombat", "preAbility"])
        self.armed = self.launched = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.armed = self.launched = False
        elif phase == "preAbility":
            if not self.armed:
                self.armed, self.launched = True, False
        elif phase == LAUNCH and self.armed:
            self.launched = True
        elif phase == ONHIT_AFTER and self.armed and (not champion.ranged or self.launched):
            self.armed = False
            item_damage(champion, input_.target, stage_value(self, champion, "ProcDamage") * input_.effectiveness,
                        "magical")  # I11
        return input_


@register("artifact")
class WitsEnd(BuildItem):
    """Stats GE_Artifact_WitsEnd_Stats (25% AS, 20 armor, 20 MR, 300 HP). Script GA_Artifact_WitsEnd: after every
    on-hit damage (0x3a6, PostApply), GE_Artifact_WitsEnd_OnHitDamage on the target: magic damage OnHitDamage at the
    current stage (TFTStageMagnitude: 25/25/45/65/85/100) x the hit's on-hit effectiveness (1 for an attack). The heal
    on magic damage does nothing against dummies."""
    KEY = "DA_Artifact_WitsEnd"
    STATS = ("GE_Artifact_WitsEnd_Stats",)
    display_name = item_name(KEY)

    LISTENS = {ONHIT_AFTER: frozenset()}

    def performAbility(self, phase, time, champion, input_=0):
        item_damage(champion, input_.target, stage_value(self, champion, "OnHitDamage") * input_.effectiveness,
                    "magical")  # I11
        return input_


@register("artifact")
class StatikkShiv(BuildItem):
    """Stats GE_Artifact_StatikkShiv_Artifact_Stats (40% AS, 25% AP). Script GA_Artifact_StatikkShiv: counts the
    holder's attack releases (Combat.Event.LaunchAttack, simulated attacks count, 0x1616; never reset) and on every
    3rd (0x16f4) fires at once, at the release: NumTargets x (BaseDamage + bonus AP x APScalar) split among
    min(enemies, NumTargets) bolts (0x228-0x4eb), magic (GE_Artifact_StatikkShiv_Damage): the attack's target first,
    then the others. Taken to hit 6 enemies whatever the page's number of targets (owner, 2026-11-18): NumTargets
    bolts of 15 + 35% of bonus AP each, over the dummies in play in turn (all dummies are alike)."""
    KEY = "DA_Artifact_StatikkShiv"
    STATS = ("GE_Artifact_StatikkShiv_Artifact_Stats",)
    display_name = item_name(KEY)
    EVERY = 3  # script literal (0x16f4)

    LISTENS = {LAUNCH: frozenset()}

    def __init__(self):
        super().__init__(phases=["preCombat"])
        self.count = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.count = 0
        elif phase == LAUNCH:
            self.count += 1
            if self.count % self.EVERY == 0 and champion.opponents:
                n = int(self.row(champion, "NumTargets"))
                enemies = in_play(champion.opponents)  # the page's targets, not the spare (layout.py)
                per = self.row(champion, "BaseDamage") + (champion.ap.stat - 1) * 100 * self.row(champion, "APScalar")
                for k in range(n):  # n enemies assumed (owner): one bolt each
                    item_damage(champion, enemies[k % len(enemies)], per, "magical")
        return input_


@register("artifact")
class TitanicHydra(BuildItem):
    """Stats GE_Artifact_TitanicHydra_Stats (300 HP, 20% AS, 20% AD). Script GA_Artifact_TitanicHydra: before each
    on-hit damage is applied (PreApply, 0x59), GE_Artifact_TitanicHydra_BonusDamage: physical, holder max Health x
    PercentHealthBonusDamage (2%) + Attack Damage x PercentADBonusDamage (4%) to the enemies within 1 hex of the
    target (TR_Add_EnemiesWithinHexRange, HexRange 1, taken to include the target): the target and one enemy next to
    it, whatever the page's number of targets (owner, 2026-11-18)."""
    KEY = "DA_Artifact_TitanicHydra"
    STATS = ("GE_Artifact_TitanicHydra_Stats",)
    display_name = item_name(KEY) + " (1 adjacent)"  # owner, 2026-11-18: one enemy next to the target assumed

    LISTENS = {ONHIT_PRE: frozenset()}

    def performAbility(self, phase, time, champion, input_=0):
        amount = (champion.hp.stat * self.row(champion, "PercentHealthBonusDamage")
                  + champion.atk.stat * champion.bonus_ad.stat * self.row(champion, "PercentADBonusDamage"))
        # the target and one enemy next to it, whatever the page's targets (owner, 2026-11-18)
        for target in (input_.target, champion.neighbour(input_.target)):
            item_damage(champion, target, amount * input_.effectiveness, "physical")  # I11
        return input_


@register("artifact")
class HellfireHatchet(BuildItem):
    """Stats GE_HellfireHatchet_Stats (400 HP, 20% omnivamp; its AttackSpeed per missing Health is 0 at full Health,
    and dummies never hit back). Script GA_Artifact_HellfireHatchet: after every on-hit damage (PostApply),
    GE_Artifact_HellfireHatchet_OnHitDamage on the target: physical, holder max Health x PercentHPDamage (3%)."""
    KEY = "DA_Artifact_HellfireHatchet"
    STATS = ("GE_HellfireHatchet_Stats",)
    SKIP = (("AttackSpeed", "MultiplyAdditive", "custom"),)
    display_name = item_name(KEY)

    LISTENS = {ONHIT_AFTER: frozenset()}

    def performAbility(self, phase, time, champion, input_=0):
        item_damage(champion, input_.target,
                    champion.hp.stat * self.row(champion, "PercentHPDamage") * input_.effectiveness, "physical")  # I11
        return input_


@register("artifact")
class Flickerblades(BuildItem):
    """Stats GE_Artifact_NavoriFlickerblade_Stats (10% AP, 20% AS). Script GA_Artifact_NavoriFlickerblade: every
    attack release (LaunchAttack, simulated attacks count) applies GE_Artifact_NavoriFlickerblade_StackingAttackSpeed
    (AttackSpeed MultiplyAdditive StackingAttackSpeed, +4%, no cap) and every AttacksPerADAPBuff-th (3, the item's
    parameter) GE_Artifact_NavoriFlickerblade_StackingADAP (+2% AD, +2% AP); the count resets at combat start."""
    KEY = "DA_Artifact_NavoriFlickerblade"
    STATS = ("GE_Artifact_NavoriFlickerblade_Stats",)
    display_name = item_name(KEY)

    LISTENS = {LAUNCH: frozenset()}

    def __init__(self):
        super().__init__(phases=["preCombat"])
        self.count = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.count = 0
        elif phase == LAUNCH:
            champion.aspd.modify("MultiplyAdditive", self.row(champion, "StackingAttackSpeed"))
            self.count += 1
            every = self.row(champion, self.ga_param(champion, "GA_Artifact_NavoriFlickerblade", "AttacksPerADAPBuff_CT"))
            if self.count >= every:
                self.count = 0
                champion.bonus_ad.modify("+", self.row(champion, "StackingAttackDamage"))
                champion.ap.modify("+", self.row(champion, "StackingAbilityPower"))
        return input_


@register("artifact")
class Dawncore(BuildItem):
    """Stats GE_Artifact_Dawncore_Stats (20% AD, 20% AP, 1 mana regen) and GE_Artifact_Dawncore_FlatManaReduction
    (ManaMax - FlatMaxManaReduction 10, at least MinimumMana 15). Script GA_Artifact_Dawncore: every cast (0x479)
    lowers ManaMax by ReductionOnSpellcastPercent (5%) of its current value, not below MinimumMana. Applied after the
    cast's cost is paid, so it lowers the next cast (the order is not in the script; I10)."""
    KEY = "DA_Artifact_Dawncore"
    STATS = ("GE_Artifact_Dawncore_Stats",)
    display_name = item_name(KEY)

    def __init__(self):
        super().__init__(phases=["postAbility"])

    def applyStats(self, champion):
        super().applyStats(champion)
        floor = self.row(champion, "MinimumMana")
        champion.fullMana.modify("+", -min(self.row(champion, "FlatMaxManaReduction"),
                                          max(0, champion.fullMana.stat - floor)))

    def performAbility(self, phase, time, champion, input_=0):
        floor = self.row(champion, "MinimumMana")
        cut = min(self.row(champion, "ReductionOnSpellcastPercent") / 100 * champion.fullMana.stat,
                  champion.fullMana.stat - floor)
        if cut > 0:
            champion.fullMana.modify("+", -cut)
        return input_


@register("artifact")
class Manazane(BuildItem):
    """Stats GE_Artifact_Manazane_Stats (15% AD, 15% AP, 1 mana regen). Script GA_Artifact_Manazane: on the first
    cast only (0xa05 ends the wait), a looping timer every ManaGainPeriod (0.1 s), first tick a period after the cast
    starts, grants CastManaGain / CastManaGainDuration x ManaGainPeriod (2.2) mana per tick (GE_Artifact_Manazane_
    ManaTick); a tick while the holder's mana is locked is skipped and doesn't count; it stops at CastManaGain (110)."""
    KEY = "DA_Artifact_Manazane"
    STATS = ("GE_Artifact_Manazane_Stats",)
    display_name = item_name(KEY)

    def __init__(self):
        super().__init__(phases=["preCombat", "preAbility", "onUpdate"])
        self.next_tick = self.given = None

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.next_tick, self.given = None, 0
        elif phase == "preAbility" and self.next_tick is None and self.given == 0:
            self.next_tick = champion.tick + ticks_up(self.row(champion, "ManaGainPeriod"))
        elif phase == "onUpdate" and self.next_tick is not None and champion.tick >= self.next_tick:
            total = self.row(champion, "CastManaGain")
            per = total / self.row(champion, "CastManaGainDuration") * self.row(champion, "ManaGainPeriod")
            self.next_tick += ticks_up(self.row(champion, "ManaGainPeriod"))
            if champion.tick >= champion.busy_until and champion.tick >= champion.mana_locked_until:
                champion.addMana(per)
                self.given += per
                if self.given >= total - 1e-9:
                    self.next_tick = None
        return input_


@register("artifact")
class Hullcrusher(BuildItem):
    """Stats GE_Artifact_Hullcrusher_Stats (60 armor, 60 MR). Script GA_Artifact_Hullcrusher: before combat, with no
    ally within 1 hex, GE_Artifact_Hullcrusher_Buff (HealthBonus 400 HP, ADBonus 10% AD, APBonus 10% AP); taken as
    met (owner, 2026-11-17: the holder stands alone)."""
    KEY = "DA_Artifact_Hullcrusher"
    STATS = ("GE_Artifact_Hullcrusher_Stats",)
    display_name = item_name(KEY)

    def applyStats(self, champion):
        super().applyStats(champion)
        champion.bonus_ad.modify("+", self.row(champion, "ADBonus"))
        champion.ap.modify("+", self.row(champion, "APBonus"))


@register("artifact")
class TalismanOfAscension(BuildItem):
    """Stats GE_Item_Artifact_TalismanOfAscension_Stats (20% AD, 20% AP, 450 HP). Script
    GA_Item_Artifact_TalismanOfAscension: DelayBeforeBuff (22 s) after combat start, GE_Item_Artifact_
    TalismanOfAscension_Buff: OutgoingDamageMultiplier + DamageAmpBuff (120%), ManaPerSecond + ManaGen (12), max Health
    x 2."""
    KEY = "DA_Item_Artifact_TalismanOfAscension"
    STATS = ("GE_Item_Artifact_TalismanOfAscension_Stats",)
    display_name = item_name(KEY)

    def __init__(self):
        super().__init__(phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        amp, regen = self.row(champion, "DamageAmpBuff"), self.row(champion, "ManaGen")

        def buff():
            champion.dmgMultiplier.modify("+", amp)
            champion.manaRegen.modify("+", regen)
        champion.schedule_tick(champion.tick + ticks_up(self.row(champion, "DelayBeforeBuff")), buff)
        return input_


@register("artifact")
class GamblersBlade(BuildItem):
    """Stats GE_Artifact_GamblersBlade_Stats: AttackSpeed MultiplyAdditive AttackSpeed (55%) and ScalingAttackSpeed
    (1%) x AttackSpeedCalc1 (gold in the bank, at most MaxCoinScaling 30): taken at 30 gold (owner, 2026-11-17), +30%.
    Script GA_Artifact_GamblersBlade: gold drops in player combat only."""
    KEY = "DA_Artifact_GamblersBlade"
    STATS = ("GE_Artifact_GamblersBlade_Stats",)
    SKIP = (("AttackSpeed", "MultiplyAdditive", "AttackSpeedCalc1"),)
    display_name = item_name(KEY)

    def applyStats(self, champion):
        super().applyStats(champion)
        champion.aspd.modify("MultiplyAdditive",
                             1 + self.row(champion, "ScalingAttackSpeed") * self.row(champion, "MaxCoinScaling"))


@register("artifact")
class CappaJuice(BuildItem):
    """Stats GE_Artifact_CappaJuice_Stats (25% AD, 25% AP, 25% AS, + ADPerStack / APPerStack 1% per Hat). A Hat per
    takedown, kept between rounds (GA_Artifact_CappaJuice); the Hats are the page's 'Total takedowns' (owner,
    2026-11-17, as set18)."""
    KEY = "DA_Artifact_CappaJuice"
    STATS = ("GE_Artifact_CappaJuice_Stats",)
    SKIP = (("AttackDamage", "+", "Stack"), ("AbilityPower", "+", "Stack"))
    display_name = item_name(KEY)
    # The table's row takes its own count, defaulting to the page's takedowns (owner, 2026-11-19): sim_entry sets
    # row_value from the page's rowInputs; None (an item slot) reads the champion's takedowns.
    ROW_INPUT = {"Title": "Takedowns", "Min": 0, "Max": 999, "Row": "{} takedowns"}
    row_value = None

    def applyStats(self, champion):
        super().applyStats(champion)
        hats = getattr(champion, "takedowns", 0) if self.row_value is None else self.row_value
        champion.bonus_ad.modify("+", self.row(champion, "ADPerStack") * hats)
        champion.ap.modify("+", self.row(champion, "APPerStack") * hats)
