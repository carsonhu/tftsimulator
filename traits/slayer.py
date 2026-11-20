"""The Slayer trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class Slayer(BuildTrait):
    """Slayer (DA_Mosher19): "Slayers gain Attack Speed and Omnivamp, which increases up to 100%, based on their
    missing Health." CT_Mosher19 at the tier: AttackSpeed (20/40/65%), Omnivamp (8/10/12%),
    IncreaseMaxBasedOnMissingHealth (1: up to double at 0 Health).

    The tier effect on members: AttackSpeed MultiplyAdditive and Omnivamp, scaled by 1 + missing Health fraction x
    IncreaseMaxBasedOnMissingHealth. Training dummies never hit back (G9), so the simulated unit stays at full Health:
    +20/40/65% attack speed; omnivamp heals nothing that matters. Infinite, Channel1, with the item stats (I1). The
    emblem is not modelled.
    """
    KEY = "DA_Mosher19"
    display_name = "Slayer"

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0 or not champion.has_trait(self.KEY):
            return
        champion.aspd.modify("MultiplyAdditive", 1 + champion.trait_value(self.KEY, "AttackSpeed"))


Slayer.levels = [0] + Slayer.breakpoints()
