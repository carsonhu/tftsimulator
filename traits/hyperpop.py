"""The Hyperpop trait."""
from buildstore import BuildDataError
from registry import register
from traits.base import BuildTrait


@register("trait")
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
        if champion.trait_tier(self.KEY) == 0 or not champion.has_trait(self.KEY):
            return
        if champion.trait_value(self.KEY, "PercentIncreasePerLevel") != 0:
            raise BuildDataError(f"{self.KEY}: PercentIncreasePerLevel is not 0 in build {champion.build.version}: "
                                 f"Hype now scales the stats (needs a Hype-level parameter)")
        champion.aspd.modify("MultiplyAdditive", 1 + champion.trait_value(self.KEY, "BaseAttackSpeed"))


Hyperpop.levels = [0] + Hyperpop.breakpoints()
