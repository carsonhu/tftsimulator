"""The Renegade trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class Renegade(BuildTrait):
    """Renegade (DA_Renegade19): "Renegades gain Precision, Critical Strike Chance, and Critical Strike Damage."
    CT_Renegade19 at the tier: CritChance (15/20/25/35%), CritDamage (12/18/22/25%), Durability (10% at (5)).

    DA_Renegade19's tier effect GE_Renegade19 on members (TFTAddAlliesWithTraitsOfSource): CritChance + CritChance,
    CritDamage + CritDamage, IncomingDamageMultiplier (durability: nothing against dummies that never hit back) and
    the tag Damage.Status.CanSpellCrit (Precision, I2). Infinite, Channel1, applied with the item stats (I1). The
    augment (High Rolling) and the emblem are not modelled.
    """
    KEY = "DA_Renegade19"
    display_name = "Renegade"

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0 or not champion.has_trait(self.KEY):
            return
        champion.crit.modify("+", champion.trait_value(self.KEY, "CritChance"))
        champion.critDmg.modify("+", champion.trait_value(self.KEY, "CritDamage"))
        champion.addPrecision()


Renegade.levels = [0] + Renegade.breakpoints()
