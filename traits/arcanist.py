"""The Arcanist trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
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
        champion.ap.modify("+", champion.trait_value(self.KEY, "ArcanistAP" if member else "NonArcanistAP"))


Arcanist.levels = [0] + Arcanist.breakpoints()
