"""The Pentakill trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class Pentakill(BuildTrait):
    """Pentakill (DA_Pentakill19): "Pentakill members gain Attack Damage and Ability Power. The first few enemies to
    drop below 10% Health are executed and summon an allied ghoul in their place." CT_Pentakill19 at the tier: ADAP
    (15/30/35%).

    DA_Pentakill19's tier effect GE_Pentakill19_Stats on allies with the trait (TFTAddAlliesWithTraitRule):
    AttackDamage + ADAP and AbilityPower + ADAP, infinite, Channel1 (bonus AD and AP), applied with the item stats
    (I1). The execute, the ghouls, the Iron Maiden and the Mosh Pit need enemies that die: not modelled (owner,
    2026-11-18: the summons are irrelevant to the damage sim).
    """
    KEY = "DA_Pentakill19"
    display_name = "Pentakill"

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0 or not champion.has_trait(self.KEY):
            return
        v = champion.trait_value(self.KEY, "ADAP")
        champion.bonus_ad.modify("+", v)
        champion.ap.modify("+", v)


# (7) is listed twice (the Prismatic Quest's two versions); one level is enough
Pentakill.levels = [0] + sorted(set(Pentakill.breakpoints()))
